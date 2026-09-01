"""
Final synthesis script. Consolidates every check that shaped the project's
actual conclusion (several of which were originally run as one-off snippets
during exploration) into one reproducible script:

  A. Replicate Smirnov & Thurner's own headline statistic (the Homophily
     Index: Pearson r between own GPA and average friend GPA) directly from
     getHomophily.m's formula, on the same data -- gives an apples-to-apples
     benchmark for how large *their* effect is.

  B. THE PRE-SPECIFIED HEADLINE TEST. This is the one regression we treat as
     confirmatory: pooled sample, the baseline Katz-Bonacich centrality
     computed in step 01 (alpha = 0.85 / lambda_max -- chosen when the panel
     was first built, before any alpha-sweep exploration), horse-raced
     against raw in/out-degree AND against avg_friend_gpa (Smirnov &
     Thurner's own selection-channel variable) plus cohort fixed effects.
     Because this specification was fixed before the alpha sweep existed,
     it is not subject to a look-elsewhere/multiple-comparisons critique.

  C/D. The alpha-sweep heterogeneity breakdown, by level (high_school vs
     university) and by the 5 individual cohorts -- exploratory /
     supplementary evidence, explicitly labelled as such.

  E. Network structural diagnostics (density, avg in-degree, reciprocity,
     clustering) per cohort, to check whether cohort-level heterogeneity in
     the Katz effect tracks network sparsity (it does, r=0.86 on n=5 -- a
     suggestive, not inferential, pattern).
"""
import time
from pathlib import Path

import networkx as nx
import numpy as np
import pandas as pd
import scipy.io as sio
import statsmodels.formula.api as smf
from scipy.stats import pearsonr

ROOT = Path(__file__).resolve().parent.parent.parent
MAT_PATH = ROOT / "data" / "friendship_gpa" / "data.mat"
PANEL_CSV = ROOT / "output" / "friendship_gpa" / "panel_long.csv"
SWEEP_RAW_CSV = ROOT / "output" / "friendship_gpa" / "robustness_alpha_sweep_raw.csv"
OUT = ROOT / "output" / "friendship_gpa"

_T0 = time.time()


def log(msg):
    print(f"[{time.time() - _T0:6.1f}s] {msg}", flush=True)


GROUPS = ["school", "freshmen", "sophomores", "juniors", "seniors"]


def zscore(s):
    return (s - s.mean()) / s.std() if s.std() > 0 else s * 0


# ---------------------------------------------------------------------------
# A. Replicate Smirnov & Thurner's Homophily Index
# ---------------------------------------------------------------------------
def replicate_homophily_index(mat):
    log("A. Replicating Smirnov & Thurner's Homophily Index (own code, real data)")
    rows = []
    for g in GROUPS:
        nets = mat[f"networks_{g}"]
        gpa_mat = mat[f"gpa_{g}"]
        time_varying = gpa_mat.shape[1] > 1
        n_tp = nets.shape[1]
        hs = []
        for t in range(n_tp):
            A = np.asarray(nets[0, t]).astype(float)
            gpa = gpa_mat[:, t] if time_varying else gpa_mat[:, 0]
            row_sum = A.sum(axis=1)
            with np.errstate(invalid="ignore", divide="ignore"):
                gpa_friends = (A @ gpa) / row_sum
            gpa_friends = np.nan_to_num(gpa_friends, nan=0.0)
            mask = gpa_friends > 0
            if mask.sum() > 1:
                r, _ = pearsonr(gpa[mask], gpa_friends[mask])
                hs.append(r)
        rows.append({"group": g, "n_timepoints": len(hs), "homophily_index_mean": np.mean(hs)})
        log(f"  {g:12s} mean Homophily Index = {np.mean(hs):.3f}")
    df = pd.DataFrame(rows)
    df.to_csv(OUT / "final_homophily_index_replication.csv", index=False)
    log(f"  saved -> final_homophily_index_replication.csv "
        f"(pooled mean = {df['homophily_index_mean'].mean():.3f})")
    return df


# ---------------------------------------------------------------------------
# B. Pre-specified headline test
# ---------------------------------------------------------------------------
def headline_test(panel: pd.DataFrame):
    log("B. HEADLINE TEST (pre-specified, alpha=0.85 baseline, pooled)")
    reg = panel.dropna(
        subset=["gpa", "katz_centrality", "avg_friend_gpa", "in_degree", "out_degree"]
    ).copy()
    reg["katz_z"] = reg.groupby("group")["katz_centrality"].transform(zscore)
    reg["indeg_z"] = reg.groupby("group")["in_degree"].transform(zscore)
    reg["outdeg_z"] = reg.groupby("group")["out_degree"].transform(zscore)

    m = smf.ols(
        "gpa ~ katz_z + indeg_z + outdeg_z + avg_friend_gpa + C(group)", data=reg
    ).fit(cov_type="cluster", cov_kwds={"groups": reg["student_id"]})
    print(m.summary())
    with open(OUT / "final_headline_test.txt", "w") as f:
        f.write(
            "HEADLINE TEST (pre-specified before any alpha-sweep exploration)\n"
            "gpa ~ katz_z + indeg_z + outdeg_z + avg_friend_gpa + C(group)\n"
            "alpha = 0.85 / lambda_max (baseline choice from step 01, not "
            "selected post-hoc from the sweep). SEs clustered by student.\n\n"
        )
        f.write(m.summary().as_text())
    log(f"  katz_z coef = {m.params['katz_z']:+.4f}  p = {m.pvalues['katz_z']:.4f}")
    log("  saved -> final_headline_test.txt")
    return m


# ---------------------------------------------------------------------------
# C/D. Alpha-sweep heterogeneity, by level and by group (exploratory)
# ---------------------------------------------------------------------------
def heterogeneity_breakdown(sweep_raw: pd.DataFrame):
    log("C/D. Exploratory heterogeneity across the alpha sweep (by level, by group)")
    df = sweep_raw.copy()
    df["level"] = np.where(df["group"] == "school", "high_school", "university")
    df = df.dropna(subset=["gpa", "katz", "in_degree", "out_degree"])

    rows_level = []
    for alpha in sorted(df["alpha_frac"].unique()):
        for level in ["high_school", "university"]:
            sub = df[(df["alpha_frac"] == alpha) & (df["level"] == level)].copy()
            sub["katz_z"] = sub.groupby("group")["katz"].transform(zscore)
            sub["indeg_z"] = sub.groupby("group")["in_degree"].transform(zscore)
            sub["outdeg_z"] = sub.groupby("group")["out_degree"].transform(zscore)
            formula = "gpa ~ katz_z + indeg_z + outdeg_z" + (" + C(group)" if level == "university" else "")
            m = smf.ols(formula, data=sub).fit(cov_type="cluster", cov_kwds={"groups": sub["student_id"]})
            rows_level.append({
                "alpha_frac": alpha, "level": level, "n": len(sub),
                "katz_coef": m.params.get("katz_z", np.nan),
                "katz_pval": m.pvalues.get("katz_z", np.nan),
            })
    res_level = pd.DataFrame(rows_level)
    res_level["sig"] = res_level["katz_pval"] < 0.05
    res_level.to_csv(OUT / "final_heterogeneity_by_level.csv", index=False)
    log("  saved -> final_heterogeneity_by_level.csv")

    rows_group = []
    for alpha in sorted(df["alpha_frac"].unique()):
        for group in GROUPS:
            sub = df[(df["alpha_frac"] == alpha) & (df["group"] == group)].copy()
            sub["katz_z"] = zscore(sub["katz"])
            sub["indeg_z"] = zscore(sub["in_degree"])
            sub["outdeg_z"] = zscore(sub["out_degree"])
            m = smf.ols("gpa ~ katz_z + indeg_z + outdeg_z", data=sub).fit(
                cov_type="cluster", cov_kwds={"groups": sub["student_id"]}
            )
            rows_group.append({
                "alpha_frac": alpha, "group": group, "n": len(sub),
                "katz_coef": m.params.get("katz_z", np.nan),
                "katz_pval": m.pvalues.get("katz_z", np.nan),
            })
    res_group = pd.DataFrame(rows_group)
    res_group["sig"] = res_group["katz_pval"] < 0.05
    res_group.to_csv(OUT / "final_heterogeneity_by_group.csv", index=False)
    log("  saved -> final_heterogeneity_by_group.csv")
    return res_level, res_group


# ---------------------------------------------------------------------------
# E. Structural diagnostics per cohort (explains the heterogeneity)
# ---------------------------------------------------------------------------
def structural_diagnostics(mat, res_group: pd.DataFrame):
    log("E. Network structural diagnostics per cohort")
    rows = []
    for g in GROUPS:
        nets = mat[f"networks_{g}"]
        n_tp = nets.shape[1]
        densities, indegs, recips, clusters = [], [], [], []
        for t in range(n_tp):
            A = np.asarray(nets[0, t])
            G = nx.from_numpy_array(A, create_using=nx.DiGraph)
            n, e = G.number_of_nodes(), G.number_of_edges()
            densities.append(e / (n * (n - 1)))
            indegs.append(e / n)
            recips.append(nx.reciprocity(G))
            clusters.append(nx.average_clustering(G.to_undirected()))
        rows.append({
            "group": g,
            "density": np.mean(densities),
            "avg_in_degree": np.mean(indegs),
            "reciprocity": np.mean(recips),
            "clustering": np.mean(clusters),
        })
    struct = pd.DataFrame(rows)

    katz_at_95 = res_group[res_group["alpha_frac"] == 0.95][["group", "katz_coef"]]
    merged = struct.merge(katz_at_95, on="group")
    r, _ = pearsonr(merged["avg_in_degree"], merged["katz_coef"])
    print(merged.to_string(index=False))
    print(f"\ncorr(avg_in_degree, katz_coef @ alpha=0.95) = {r:.3f}  (n=5, suggestive only)")
    merged.to_csv(OUT / "final_structural_diagnostics.csv", index=False)
    log("  saved -> final_structural_diagnostics.csv")
    return merged


def main():
    log("Loading data...")
    mat = sio.loadmat(MAT_PATH)
    panel = pd.read_csv(PANEL_CSV)
    sweep_raw = pd.read_csv(SWEEP_RAW_CSV)

    replicate_homophily_index(mat)
    headline_test(panel)
    _, res_group = heterogeneity_breakdown(sweep_raw)
    structural_diagnostics(mat, res_group)

    log("ALL DONE.")


if __name__ == "__main__":
    main()
