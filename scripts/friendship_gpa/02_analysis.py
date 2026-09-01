"""
Three-layer analysis on the Smirnov & Thurner (2017) replication data.

LAYER 1 - reproduce the original paper's selection-vs-influence logic
  Check 1 (against "socialization"/peer-influence): lagged regression
      gpa_t ~ gpa_{t-1} + avg_friend_gpa_{t-1}
  Only meaningful for the 'school' group, which is the only group with a
  GPA time series (university groups have one static GPA value per
  student -- see 01_build_master_dataset.py docstring). Reported as such.

  Check 2 (for "selection"): two-sample t-test comparing the GPA gap
  |gpa_ego - gpa_alter| on edges that are newly formed between two
  consecutive snapshots vs. edges that are dropped between the same two
  snapshots. Selection predicts: new-tie gap < dropped-tie gap.
  Run for every group (school + all 4 university cohorts).

LAYER 2 - does Katz-Bonacich centrality have independent explanatory power
  for GPA after controlling for the (average-friend-GPA) channel the
  original paper attributes to selection?
      gpa ~ katz_centrality + avg_friend_gpa + C(group) [+ time FE for school]
  clustered SEs by student (repeated snapshots per student).

LAYER 3 - split Layer 1 (check 2) and Layer 2 by level (high_school vs
  university) and compare estimated effects.
"""
import time
from itertools import combinations
from pathlib import Path

import numpy as np
import pandas as pd
import scipy.io as sio
import statsmodels.formula.api as smf
from scipy import stats

ROOT = Path(__file__).resolve().parent.parent.parent
MAT_PATH = ROOT / "data" / "friendship_gpa" / "data.mat"
PANEL_CSV = ROOT / "output" / "friendship_gpa" / "panel_long.csv"
OUT = ROOT / "output" / "friendship_gpa"

_T0 = time.time()


def log(msg):
    print(f"[{time.time() - _T0:6.1f}s] {msg}", flush=True)


GROUPS = ["school", "freshmen", "sophomores", "juniors", "seniors"]


# ---------------------------------------------------------------------------
# LAYER 1, CHECK 1: lagged own-GPA regression (school group only)
# ---------------------------------------------------------------------------
def layer1_check1_lagged_regression(panel: pd.DataFrame):
    log("LAYER 1 / CHECK 1: lagged regression gpa_t ~ gpa_(t-1) + avg_friend_gpa_(t-1)")
    log("  (only 'school' has a real GPA time series; university GPA is static)")
    sub = panel[panel["group"] == "school"].copy()
    sub = sub.sort_values(["student_id", "time_index"])

    sub["gpa_lag"] = sub.groupby("student_id")["gpa"].shift(1)
    sub["avg_friend_gpa_lag"] = sub.groupby("student_id")["avg_friend_gpa"].shift(1)

    reg_data = sub.dropna(subset=["gpa", "gpa_lag", "avg_friend_gpa_lag"])
    log(f"  n obs (school, with valid lags): {len(reg_data)}")

    model = smf.ols(
        "gpa ~ gpa_lag + avg_friend_gpa_lag", data=reg_data
    ).fit(cov_type="cluster", cov_kwds={"groups": reg_data["student_id"]})
    print(model.summary())
    with open(OUT / "layer1_check1_lagged_regression.txt", "w") as f:
        f.write("LAYER 1 / CHECK 1: lagged GPA regression (school group only)\n")
        f.write("Prediction from original paper: avg_friend_gpa_lag should be\n")
        f.write("insignificant once gpa_lag (own past performance) is controlled\n")
        f.write("for -- i.e. friends' past GPA does not predict your future GPA\n")
        f.write("once your own trajectory is accounted for (rules out peer influence).\n\n")
        f.write(model.summary().as_text())
    log("  saved -> layer1_check1_lagged_regression.txt")
    return model


# ---------------------------------------------------------------------------
# LAYER 1, CHECK 2: new-tie vs dropped-tie GPA-gap t-test
# ---------------------------------------------------------------------------
def layer1_check2_new_vs_dropped(mat, panel: pd.DataFrame):
    log("LAYER 1 / CHECK 2: new-tie vs dropped-tie GPA-gap t-test, by group")
    results = []
    per_group_gaps = {}

    for group_name in GROUPS:
        nets = mat[f"networks_{group_name}"]
        gpa_mat = mat[f"gpa_{group_name}"]
        time_varying = gpa_mat.shape[1] > 1
        n_tp = nets.shape[1]

        new_gaps, dropped_gaps = [], []
        for t in range(n_tp - 1):
            A_t = np.asarray(nets[0, t]).astype(bool)
            A_t1 = np.asarray(nets[0, t + 1]).astype(bool)
            gpa_t = gpa_mat[:, t] if time_varying else gpa_mat[:, 0]

            new_edges = np.argwhere(A_t1 & ~A_t)
            dropped_edges = np.argwhere(A_t & ~A_t1)

            if len(new_edges):
                new_gaps.extend(np.abs(gpa_t[new_edges[:, 0]] - gpa_t[new_edges[:, 1]]))
            if len(dropped_edges):
                dropped_gaps.extend(
                    np.abs(gpa_t[dropped_edges[:, 0]] - gpa_t[dropped_edges[:, 1]])
                )

        new_gaps = np.array(new_gaps)
        dropped_gaps = np.array(dropped_gaps)
        per_group_gaps[group_name] = (new_gaps, dropped_gaps)

        if len(new_gaps) > 1 and len(dropped_gaps) > 1:
            tstat, pval = stats.ttest_ind(new_gaps, dropped_gaps, equal_var=False)
            results.append(
                {
                    "group": group_name,
                    "level": "high_school" if group_name == "school" else "university",
                    "n_new_ties": len(new_gaps),
                    "n_dropped_ties": len(dropped_gaps),
                    "mean_gap_new": new_gaps.mean(),
                    "mean_gap_dropped": dropped_gaps.mean(),
                    "diff": new_gaps.mean() - dropped_gaps.mean(),
                    "t_stat": tstat,
                    "p_value": pval,
                }
            )

    res_df = pd.DataFrame(results)
    print(res_df.to_string(index=False))
    res_df.to_csv(OUT / "layer1_check2_new_vs_dropped.csv", index=False)
    log("  saved -> layer1_check2_new_vs_dropped.csv")

    # pooled by level
    log("  Pooled by level (high_school vs university):")
    pooled = []
    for level, group_list in [
        ("high_school", ["school"]),
        ("university", ["freshmen", "sophomores", "juniors", "seniors"]),
    ]:
        new_all = np.concatenate([per_group_gaps[g][0] for g in group_list if len(per_group_gaps[g][0])])
        drop_all = np.concatenate([per_group_gaps[g][1] for g in group_list if len(per_group_gaps[g][1])])
        tstat, pval = stats.ttest_ind(new_all, drop_all, equal_var=False)
        pooled.append(
            {
                "level": level,
                "n_new_ties": len(new_all),
                "n_dropped_ties": len(drop_all),
                "mean_gap_new": new_all.mean(),
                "mean_gap_dropped": drop_all.mean(),
                "diff": new_all.mean() - drop_all.mean(),
                "t_stat": tstat,
                "p_value": pval,
            }
        )
    pooled_df = pd.DataFrame(pooled)
    print(pooled_df.to_string(index=False))
    pooled_df.to_csv(OUT / "layer1_check2_pooled_by_level.csv", index=False)
    log("  saved -> layer1_check2_pooled_by_level.csv")
    return res_df, pooled_df


# ---------------------------------------------------------------------------
# LAYER 2 + 3: Katz-Bonacich centrality regression, pooled and split by level
# ---------------------------------------------------------------------------
def layer2_3_centrality_regression(panel: pd.DataFrame):
    log("LAYER 2: gpa ~ katz_centrality + avg_friend_gpa + C(group), clustered by student")
    reg_data = panel.dropna(subset=["gpa", "katz_centrality", "avg_friend_gpa"]).copy()

    # z-score katz_centrality within group so coefficients are comparable
    # across groups with very different network sizes/densities.
    reg_data["katz_z"] = reg_data.groupby("group")["katz_centrality"].transform(
        lambda s: (s - s.mean()) / s.std() if s.std() > 0 else 0.0
    )

    m_pooled = smf.ols(
        "gpa ~ katz_z + avg_friend_gpa + C(group)", data=reg_data
    ).fit(cov_type="cluster", cov_kwds={"groups": reg_data["student_id"]})
    print(m_pooled.summary())
    with open(OUT / "layer2_pooled_regression.txt", "w") as f:
        f.write("LAYER 2: gpa ~ katz_centrality(z-scored within group) + avg_friend_gpa + C(group)\n")
        f.write("SEs clustered by student (repeated network snapshots per student).\n\n")
        f.write(m_pooled.summary().as_text())
    log("  saved -> layer2_pooled_regression.txt")

    log("LAYER 3: same regression, split by level (high_school vs university)")
    for level in ["high_school", "university"]:
        sub = reg_data[reg_data["level"] == level]
        formula = "gpa ~ katz_z + avg_friend_gpa" + (" + C(group)" if level == "university" else "")
        m = smf.ols(formula, data=sub).fit(
            cov_type="cluster", cov_kwds={"groups": sub["student_id"]}
        )
        print(f"\n===== LEVEL: {level} (n={len(sub)}) =====")
        print(m.summary())
        with open(OUT / f"layer3_{level}_regression.txt", "w") as f:
            f.write(f"LAYER 3: {level} subsample -- {formula}\n")
            f.write("SEs clustered by student.\n\n")
            f.write(m.summary().as_text())
        log(f"  saved -> layer3_{level}_regression.txt")

    return m_pooled


def main():
    log("Loading panel and raw .mat file...")
    panel = pd.read_csv(PANEL_CSV)
    mat = sio.loadmat(MAT_PATH)

    layer1_check1_lagged_regression(panel)
    layer1_check2_new_vs_dropped(mat, panel)
    layer2_3_centrality_regression(panel)

    log("ALL DONE.")


if __name__ == "__main__":
    main()
