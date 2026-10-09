"""Primary test with a broad definition of network position.

Position has three parts, all measured at time t:
  popularity   = in-degree   (nominations received)
  activity     = out-degree  (nominations sent)
  wider reach  = outgoing Katz centrality (direct plus indirect paths)

Popularity and activity are part of position, not nuisance controls. The primary
question is therefore: does position, taken as a whole, predict GPA at t+1 once
GPA at t and contacts' GPA are controlled for? The joint Wald test of the three
position coefficients answers it. Each measure on its own, and the split between
"direct links" and "reach beyond direct links", are reported alongside.

Every school-panel model controls for GPA at t, average contact GPA at t and
snapshot fixed effects, and clusters standard errors by student.
Scripts 05 and 06 remain as the narrower question: does Katz add anything beyond
direct degree?

Outputs (output/friendship_gpa/):
  school_broad_position.csv          each specification, each term
  school_broad_position_tests.csv    joint tests, school panel + pooled cross-sections
  school_broad_position_robustness.csv   tie definitions and Katz attenuation sweep
"""
import importlib.util
from pathlib import Path

import pandas as pd
import statsmodels.formula.api as smf

ROOT = Path(__file__).resolve().parent.parent.parent
OUT = ROOT / "output" / "friendship_gpa"

BASE = "gpa_t1 ~ gpa_t_z + avg_friend_gpa_t + C(time_index)"
POSITION = ["katz_t_z", "indeg_t_z", "outdeg_t_z"]
SPECS = {
    "Katz only": ["katz_t_z"],
    "In-degree only": ["indeg_t_z"],
    "Out-degree only": ["outdeg_t_z"],
    "In- and out-degree": ["indeg_t_z", "outdeg_t_z"],
    "Katz + in- + out-degree": POSITION,
}
PHI_FRACTIONS = [0.05, 0.20, 0.40, 0.60, 0.80, 0.95]


def zscore(s):
    sd = s.std()
    return (s - s.mean()) / sd if sd > 0 else s * 0.0


def lagged(df, katz="katz_centrality", friend="avg_friend_gpa", terms=POSITION):
    cur = df.rename(columns={"gpa": "gpa_t", katz: "katz_t", "in_degree": "indeg_t",
                             "out_degree": "outdeg_t", friend: "avg_friend_gpa_t"}).copy()
    cur["time_index_next"] = cur["time_index"] + 1
    nxt = df[["student_id", "time_index", "gpa"]].rename(
        columns={"gpa": "gpa_t1", "time_index": "time_index_next"})
    lag = cur.merge(nxt, on=["student_id", "time_index_next"], how="inner")
    for raw, z in [("katz_t", "katz_t_z"), ("gpa_t", "gpa_t_z"),
                   ("indeg_t", "indeg_t_z"), ("outdeg_t", "outdeg_t_z")]:
        lag[z] = zscore(lag[raw])
    return lag.dropna(subset=["gpa_t1", "avg_friend_gpa_t", "gpa_t_z"] + terms)


def fit(df, terms, base=BASE):
    formula = base + "".join(f" + {t}" for t in terms)
    return smf.ols(formula, data=df).fit(cov_type="cluster", cov_kwds={"groups": df["student_id"]})


def wald(model, terms):
    w = model.wald_test(", ".join(f"{t} = 0" for t in terms), scalar=True)
    return float(w.statistic), float(w.pvalue)


def load_06():
    spec = importlib.util.spec_from_file_location("robust06", ROOT / "scripts/friendship_gpa/06_school_robustness.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def cross_section(df, label, group_fe):
    d = df.dropna(subset=["gpa", "avg_friend_gpa", "katz_centrality", "in_degree", "out_degree"]).copy()
    for raw, z in [("katz_centrality", "katz_z"), ("in_degree", "in_z"), ("out_degree", "out_z")]:
        d[z] = d.groupby("group")[raw].transform(zscore)
    d["cluster"] = pd.factorize(d["group"] + "|" + d["student_id"].astype(str))[0]
    fe = " + C(group)" if group_fe else ""
    m = smf.ols("gpa ~ katz_z + in_z + out_z + avg_friend_gpa" + fe, data=d).fit(
        cov_type="cluster", cov_kwds={"groups": d["cluster"]})
    chi, p = wald(m, ["katz_z", "in_z", "out_z"])
    return {"sample": label, "design": "same period", "n": int(m.nobs), "chi2": chi, "joint_pval": p}


def main():
    panel = pd.read_csv(OUT / "panel_long.csv")
    school = panel[panel.group == "school"]
    lag = lagged(school)
    print(f"school panel: n={len(lag)}, students={lag.student_id.nunique()}")

    # ---- each specification -------------------------------------------------
    rows = []
    for name, terms in SPECS.items():
        m = fit(lag, terms)
        for t in terms:
            lo, hi = m.conf_int().loc[t]
            rows.append({"specification": name, "term": t, "coef": m.params[t], "se": m.bse[t],
                         "pval": m.pvalues[t], "ci_low": lo, "ci_high": hi, "n": int(m.nobs)})
    res = pd.DataFrame(rows)
    res.to_csv(OUT / "school_broad_position.csv", index=False)
    print(res.round(4).to_string(index=False))

    # ---- joint tests --------------------------------------------------------
    full = fit(lag, POSITION)
    tests = []
    for label, terms, design in [
        ("School panel: popularity, activity and reach", POSITION, "position(t) -> GPA(t+1)"),
        ("School panel: direct links (in- and out-degree)", ["indeg_t_z", "outdeg_t_z"], "position(t) -> GPA(t+1)"),
        ("School panel: reach beyond direct links (Katz)", ["katz_t_z"], "position(t) -> GPA(t+1)"),
    ]:
        chi, p = wald(full, terms)
        tests.append({"sample": label, "design": design, "n": int(full.nobs), "chi2": chi, "joint_pval": p})
    pooled = panel.copy()
    tests.append(cross_section(pooled, "Pooled, five cohorts", True))
    tests.append(cross_section(pooled[pooled.group != "school"], "University cohorts", True))
    tests.append(cross_section(pooled[pooled.group == "school"], "High school, same period", False))
    tdf = pd.DataFrame(tests)
    tdf.to_csv(OUT / "school_broad_position_tests.csv", index=False)
    print("\n", tdf.round(4).to_string(index=False))

    # ---- robustness: tie definitions and Katz attenuation ------------------
    rob = []
    r06 = load_06()
    for kind in ["outgoing", "incoming", "reciprocal"]:
        d = r06.build_panel(kind)
        terms = ["katz_t_z", "indeg_t_z"] if kind == "reciprocal" else POSITION  # symmetric ties: in = out
        l = lagged(d, katz="katz", friend="avg_contact_gpa", terms=terms)
        m = fit(l, terms)
        chi, p = wald(m, terms)
        ko = fit(l, ["katz_t_z"])
        rob.append({"check": "tie definition", "setting": kind, "n": int(m.nobs),
                    "joint_pval": p, "katz_only_coef": ko.params["katz_t_z"], "katz_only_pval": ko.pvalues["katz_t_z"]})
    sweep = pd.read_csv(OUT / "robustness_alpha_sweep_raw.csv")
    sweep = sweep[sweep.group == "school"]
    for frac in PHI_FRACTIONS:
        sub = sweep[sweep.alpha_frac == frac].rename(columns={"katz": "katz_centrality"})
        l = lagged(sub)
        m = fit(l, POSITION)
        chi, p = wald(m, POSITION)
        ko = fit(l, ["katz_t_z"])
        rob.append({"check": "Katz attenuation", "setting": frac, "n": int(m.nobs),
                    "joint_pval": p, "katz_only_coef": ko.params["katz_t_z"], "katz_only_pval": ko.pvalues["katz_t_z"]})
    rdf = pd.DataFrame(rob)
    rdf.to_csv(OUT / "school_broad_position_robustness.csv", index=False)
    print("\n", rdf.round(4).to_string(index=False))


if __name__ == "__main__":
    main()
