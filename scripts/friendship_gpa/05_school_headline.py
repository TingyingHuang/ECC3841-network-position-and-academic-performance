"""
05_school_headline.py

Restrict the confirmatory ("headline") test to the high-school group --
the only group where GPA is genuinely time-varying -- so that we can:

  1. measure position at t and GPA at t+1 (a real lag), and
  2. control for the student's own GPA at t.

Neither is possible pooled across all 5 groups: for the four university
cohorts, GPA is a single static measurement (see README), so "own past
GPA" is not a well-defined, separate regressor there. The brief's model
equation always included this control; script 04's pooled headline test
never actually ran with it, because it can't be, for 80%+ of that sample.
This script is the fix: a smaller but properly specified test.

University groups are not re-run here -- there is no t -> t+1 design
possible for them at all. They remain the cross-sectional comparison
already produced by 02/03/04 (see final_heterogeneity_by_group.csv).

Also reports, before trusting the regression: the correlation matrix and
VIF among the right-hand-side variables, to check whether adding own
past GPA introduces collinearity with the other regressors (raised in
review -- own past GPA correlates strongly with the *outcome*, which is
its job, not with the other regressors, which would be the actual
problem; this checks that directly instead of assuming it).
"""
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

ROOT = Path(__file__).resolve().parent.parent.parent
OUT = ROOT / "output" / "friendship_gpa"

PHI_FRACTIONS = [0.05, 0.20, 0.40, 0.60, 0.80, 0.95]


def zscore(s):
    sd = s.std()
    return (s - s.mean()) / sd if sd > 0 else s * 0.0


def build_lagged(df):
    """df needs: student_id, time_index, gpa, katz_val, in_degree,
    out_degree, avg_friend_gpa. Returns predictors at t + outcome at t+1."""
    cur = df.rename(columns={
        "gpa": "gpa_t", "katz_val": "katz_t",
        "in_degree": "indeg_t", "out_degree": "outdeg_t",
        "avg_friend_gpa": "avg_friend_gpa_t",
    }).copy()
    cur["time_index_next"] = cur["time_index"] + 1
    nxt = df[["student_id", "time_index", "gpa"]].rename(
        columns={"gpa": "gpa_t1", "time_index": "time_index_next"})
    return cur.merge(nxt, on=["student_id", "time_index_next"], how="inner")


def add_z(lag):
    lag["katz_t_z"] = zscore(lag["katz_t"])
    lag["gpa_t_z"] = zscore(lag["gpa_t"])
    lag["indeg_t_z"] = zscore(lag["indeg_t"])
    lag["outdeg_t_z"] = zscore(lag["outdeg_t"])
    return lag


FORMULA = "gpa_t1 ~ katz_t_z + gpa_t_z + avg_friend_gpa_t + indeg_t_z + outdeg_t_z"


def main():
    panel = pd.read_csv(OUT / "panel_long.csv")
    school = panel[panel.group == "school"].copy()
    print(f"school panel: {school.student_id.nunique()} students, "
          f"{school.time_index.nunique()} time points")

    # ------------------------------------------------ headline (alpha=0.85)
    base = school.rename(columns={"katz_centrality": "katz_val"})
    lagged = build_lagged(base)
    lagged = add_z(lagged)
    lagged = lagged.dropna(subset=["gpa_t1", "katz_t_z", "gpa_t_z",
                                    "avg_friend_gpa_t", "indeg_t_z", "outdeg_t_z"])
    print(f"lagged headline sample: n={len(lagged)}, "
          f"students={lagged.student_id.nunique()}")

    # ---- multicollinearity check among RHS variables (not vs. outcome) ----
    rhs_cols = ["katz_t_z", "gpa_t_z", "avg_friend_gpa_t", "indeg_t_z", "outdeg_t_z"]
    rhs = lagged[rhs_cols]
    corr = rhs.corr()
    corr.to_csv(OUT / "school_headline_rhs_correlations.csv")
    print("\nRHS correlation matrix (predictors only, not the outcome):")
    print(corr.round(3))

    vif_rows = []
    for col in rhs_cols:
        others = [c for c in rhs_cols if c != col]
        r2 = smf.ols(f"{col} ~ {' + '.join(others)}", data=rhs).fit().rsquared
        vif = 1 / (1 - r2) if r2 < 0.999999 else np.inf
        vif_rows.append({"variable": col, "vif": vif})
    vif_df = pd.DataFrame(vif_rows)
    vif_df.to_csv(OUT / "school_headline_vif.csv", index=False)
    print("\nVIF among predictors:")
    print(vif_df.to_string(index=False))

    # ---- the headline regression itself ----
    m = smf.ols(FORMULA, data=lagged).fit(
        cov_type="cluster", cov_kwds={"groups": lagged["student_id"]})
    with open(OUT / "school_headline_test.txt", "w") as f:
        f.write("SCHOOL-ONLY HEADLINE TEST\n")
        f.write("gpa_(t+1) ~ Katz_z(alpha=0.85) + GPA_t_z (own past GPA) "
                "+ avg_friend_gpa_t + indeg_z + outdeg_z\n")
        f.write(f"n = {len(lagged)}, students = {lagged.student_id.nunique()}\n")
        f.write("SEs clustered by student.\n\n")
        f.write(m.summary().as_text())
        f.write("\n\nRHS correlation matrix:\n")
        f.write(corr.round(3).to_string())
        f.write("\n\nVIF:\n")
        f.write(vif_df.to_string(index=False))
    print("\nHeadline regression:")
    print(m.summary())

    # ------------------------------------------------ phi sweep, school only
    sweep = pd.read_csv(OUT / "robustness_alpha_sweep_raw.csv")
    sweep = sweep[sweep.group == "school"].copy()
    afg = school[["student_id", "time_index", "avg_friend_gpa"]]
    sweep = sweep.merge(afg, on=["student_id", "time_index"], how="left")

    rows = []
    for frac in PHI_FRACTIONS:
        sub = sweep[sweep.alpha_frac == frac][
            ["student_id", "time_index", "gpa", "katz",
             "in_degree", "out_degree", "avg_friend_gpa"]
        ].rename(columns={"katz": "katz_val"})
        lag = build_lagged(sub)
        lag = add_z(lag)
        lag = lag.dropna(subset=["gpa_t1", "katz_t_z", "gpa_t_z",
                                  "avg_friend_gpa_t", "indeg_t_z", "outdeg_t_z"])
        mm = smf.ols(FORMULA, data=lag).fit(
            cov_type="cluster", cov_kwds={"groups": lag["student_id"]})
        rows.append({
            "phi_frac": frac, "n": len(lag),
            "katz_coef": mm.params["katz_t_z"], "katz_se": mm.bse["katz_t_z"],
            "katz_pval": mm.pvalues["katz_t_z"], "r2": mm.rsquared,
        })
    sweep_df = pd.DataFrame(rows)
    sweep_df.to_csv(OUT / "school_headline_phi_sweep.csv", index=False)
    print("\nphi sweep, school only, own-past-GPA now controlled:")
    print(sweep_df.to_string(index=False))


if __name__ == "__main__":
    main()
