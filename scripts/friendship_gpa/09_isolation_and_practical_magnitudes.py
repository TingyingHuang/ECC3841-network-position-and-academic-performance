"""Presentation 3: can a school use friendship data to target academic support,
and how large are the effects in practical units?

Part A - isolation check (school panel). The primary model in 07 controls for
average contact GPA, which is undefined for a student who names no one, so those
students drop out of it. Here they are kept. Does naming no one (out-degree 0),
being named by no one (in-degree 0), or both, predict GPA at t+1 for students
with the same GPA at t? Also: the share whose GPA falls by more than 0.1 points,
and a linear probability model for that fall. share_of_all_falls_flagged says
how many of all GPA falls a school would catch by flagging that group, to set
against how many students the flag covers.
    gpa_t1 ~ gpa_t_z + <indicator> + C(time_index), SEs clustered by student

Part B - effect sizes in the units Lecture 7 uses: each single-measure position
coefficient from 07 (GPA points per 1 s.d. of the measure), divided by the s.d.
of GPA at t+1 in the same estimation sample.

Part C - seeding in head counts: extra students reached by each seeding rule in
the 08 simulation, relative to random seeding.

Outputs (output/friendship_gpa/):
  isolation_check.csv
  position_effect_in_gpa_sd.csv
  contagion_seed_headcount.csv
"""
import importlib.util
from pathlib import Path

import pandas as pd
import statsmodels.formula.api as smf

ROOT = Path(__file__).resolve().parent.parent.parent
OUT = ROOT / "output" / "friendship_gpa"
DROP = -0.1


def load_07():
    spec = importlib.util.spec_from_file_location("broad07", ROOT / "scripts/friendship_gpa/07_school_broad_position.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def isolation_panel(panel):
    school = panel[panel.group == "school"].sort_values(["student_id", "time_index"]).copy()
    school["gpa_t1"] = school.groupby("student_id")["gpa"].shift(-1)
    school["next_index"] = school.groupby("student_id")["time_index"].shift(-1)
    lag = school[school.next_index == school.time_index + 1].copy()
    lag["gpa_t_z"] = (lag.gpa - lag.gpa.mean()) / lag.gpa.std()
    lag["names_no_one"] = (lag.out_degree == 0).astype(int)
    lag["named_by_no_one"] = (lag.in_degree == 0).astype(int)
    lag["fully_isolated"] = ((lag.out_degree == 0) & (lag.in_degree == 0)).astype(int)
    lag["gpa_fell"] = ((lag.gpa_t1 - lag.gpa) < DROP).astype(int)
    return lag


def part_a(lag):
    rows = []
    for ind in ["names_no_one", "named_by_no_one", "fully_isolated"]:
        for outcome in ["gpa_t1", "gpa_fell"]:
            m = smf.ols(f"{outcome} ~ gpa_t_z + {ind} + C(time_index)", data=lag).fit(
                cov_type="cluster", cov_kwds={"groups": lag["student_id"]})
            lo, hi = m.conf_int().loc[ind]
            rows.append({"indicator": ind, "outcome": outcome, "share_of_student_terms": lag[ind].mean(),
                         "coef": m.params[ind], "se": m.bse[ind], "pval": m.pvalues[ind],
                         "ci_low": lo, "ci_high": hi,
                         "fell_share_if_1": lag.loc[lag[ind] == 1, "gpa_fell"].mean(),
                         "fell_share_if_0": lag.loc[lag[ind] == 0, "gpa_fell"].mean(),
                         "share_of_all_falls_flagged": lag.loc[lag.gpa_fell == 1, ind].mean(),
                         "n": int(m.nobs), "students": lag.student_id.nunique()})
    return pd.DataFrame(rows)


def part_b(panel, m07):
    lag = m07.lagged(panel[panel.group == "school"])
    sd = lag["gpa_t1"].std()
    res = pd.read_csv(OUT / "school_broad_position.csv")
    rows = []
    for spec, term in [("Katz only", "katz_t_z"), ("Out-degree only", "outdeg_t_z"),
                       ("In-degree only", "indeg_t_z"), ("Katz + in- + out-degree", "katz_t_z"),
                       ("Katz + in- + out-degree", "outdeg_t_z")]:
        r = res[(res.specification == spec) & (res.term == term)].iloc[0]
        rows.append({"specification": spec, "term": term, "coef_gpa_points": r.coef, "pval": r.pval,
                     "gpa_t1_sd": sd, "share_of_gpa_sd": r.coef / sd, "n": int(r.n)})
    m = m07.fit(lag, [])
    rows.append({"specification": "baseline", "term": "gpa_t_z", "coef_gpa_points": m.params["gpa_t_z"],
                 "pval": m.pvalues["gpa_t_z"], "gpa_t1_sd": sd, "share_of_gpa_sd": m.params["gpa_t_z"] / sd,
                 "n": int(m.nobs)})
    return pd.DataFrame(rows)


def part_c():
    sim = pd.read_csv(OUT / "contagion_seed_comparison.csv")
    wide = sim.pivot_table(index=["group", "n_nodes", "k_seed", "seed_fraction", "threshold_r"],
                           columns="seed_strategy", values="mean_adoption_share").reset_index()
    wide["extra_vs_random_top_out_degree"] = (wide.top_out_degree - wide.random) * wide.n_nodes
    wide["extra_vs_random_top_katz"] = (wide.top_katz - wide.random) * wide.n_nodes
    wide["extra_top_out_degree_vs_top_katz"] = (wide.top_out_degree - wide.top_katz) * wide.n_nodes
    return wide


def main():
    panel = pd.read_csv(OUT / "panel_long.csv")
    m07 = load_07()

    lag = isolation_panel(panel)
    a = part_a(lag)
    a.to_csv(OUT / "isolation_check.csv", index=False)
    print(f"isolation panel: n={len(lag)}, students={lag.student_id.nunique()}")
    print(a.round(4).to_string(index=False))

    b = part_b(panel, m07)
    b.to_csv(OUT / "position_effect_in_gpa_sd.csv", index=False)
    print("\n", b.round(4).to_string(index=False))

    c = part_c()
    c.to_csv(OUT / "contagion_seed_headcount.csv", index=False)
    print("\n", c.round(3).to_string(index=False))


if __name__ == "__main__":
    main()
