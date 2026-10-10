"""Reads every number the P3 deck and speaker script quote from output/friendship_gpa/
(scripts 01-09), so the slides cannot drift from the analysis."""
import re

import numpy as np
import pandas as pd

from p3_helpers import OUT

# Lecture 7 (Calvó-Armengol, Patacchini & Zenou, AddHealth), quoted from the slides
L7_KATZ_SD, L7_DEGREE_SD, L7_FRIENDS = "7%", "2.1%", "5.5"


def load_results():
    r = {}
    txt = (OUT / "layer1_check1_lagged_regression.txt").read_text()
    r["own_gpa"] = float(re.search(r"^gpa_lag\s+([-\d.]+)", txt, re.M).group(1))
    r["contact_p"] = float(re.search(r"^avg_friend_gpa_lag\s+(?:[-\d.]+\s+){3}([-\d.]+)", txt, re.M).group(1))

    # Presentation 2's pooled result: Katz alone, then with degree and other centralities
    l2 = (OUT / "layer2_pooled_regression.txt").read_text()
    r["pooled_katz"] = float(re.search(r"^katz_z\s+([-\d.]+)", l2, re.M).group(1))
    hr = (OUT / "robustness_full_horse_race.txt").read_text()
    m = re.search(r"^katz_centrality_z\s+([-\d.]+)\s+[-\d.]+\s+[-\d.]+\s+([-\d.]+)", hr, re.M)
    r["pooled_katz_ctrl"], r["pooled_katz_ctrl_p"] = float(m.group(1)), float(m.group(2))

    bp = pd.read_csv(OUT / "school_broad_position.csv")
    get = lambda spec, term: bp[(bp.specification == spec) & (bp.term == term)].iloc[0]
    r["katz_only"] = get("Katz only", "katz_t_z")
    r["out_only"] = get("Out-degree only", "outdeg_t_z")
    r["in_only"] = get("In-degree only", "indeg_t_z")
    r["katz_full"] = get("Katz + in- + out-degree", "katz_t_z")
    r["out_full"] = get("Katz + in- + out-degree", "outdeg_t_z")
    tests = pd.read_csv(OUT / "school_broad_position_tests.csv")
    r["joint_p"] = tests.loc[tests["sample"].str.startswith("School panel: popularity"), "joint_pval"].iloc[0]
    r["phi_min_p"] = pd.read_csv(OUT / "school_headline_phi_sweep.csv").katz_pval.min()
    corr = pd.read_csv(OUT / "school_headline_rhs_correlations.csv", index_col=0)
    r["corr_katz_out"] = corr.loc["katz_t_z", "outdeg_t_z"]

    sd = pd.read_csv(OUT / "position_effect_in_gpa_sd.csv")
    pick = lambda spec, term: sd[(sd.specification == spec) & (sd.term == term)].share_of_gpa_sd.iloc[0]
    r["sd_katz"], r["sd_out"] = pick("Katz only", "katz_t_z"), pick("Out-degree only", "outdeg_t_z")
    r["sd_own"] = pick("baseline", "gpa_t_z")

    iso = pd.read_csv(OUT / "isolation_check.csv")
    isel = lambda ind, out: iso[(iso.indicator == ind) & (iso.outcome == out)].iloc[0]
    r["iso_out"], r["iso_in"] = isel("names_no_one", "gpa_t1"), isel("named_by_no_one", "gpa_fell")

    nd = pd.read_csv(OUT / "layer1_check2_new_vs_dropped.csv").set_index("group")
    r["cohorts"] = nd
    r["uni"] = pd.read_csv(OUT / "layer1_check2_pooled_by_level.csv").set_index("level").loc["university"]
    gaps = -nd.loc[["sophomores", "juniors", "seniors"], "diff"]
    fr = -nd.loc["freshmen", "diff"]
    r["ratio_lo"], r["ratio_hi"] = int(fr / gaps.max()), int(fr / gaps.min())

    ns = pd.read_csv(OUT / "contagion_network_stats.csv")
    nsel = lambda g, k: ns[(ns.group == g) & (ns.threshold_r == k)].iloc[0]
    r["never_school_r1"] = nsel("school", 1).share_can_never_be_triggered
    r["never_r4"] = (nsel("school", 4).share_can_never_be_triggered, nsel("freshmen", 4).share_can_never_be_triggered)
    r["median_out"] = (nsel("school", 1).median_out_degree, nsel("freshmen", 1).median_out_degree)
    r["n_nodes"] = (int(nsel("school", 1).n_nodes), int(nsel("freshmen", 1).n_nodes))

    sim = pd.read_csv(OUT / "contagion_seed_comparison.csv")
    r["curve"] = lambda g, strat, frac=0.03: [
        100 * v for v in sim[(sim.group == g) & (sim.seed_strategy == strat) & np.isclose(sim.seed_fraction, frac)]
        .sort_values("threshold_r").mean_adoption_share]
    hc = pd.read_csv(OUT / "contagion_seed_headcount.csv")
    r["hc"] = lambda g, frac, k: hc[(hc.group == g) & np.isclose(hc.seed_fraction, frac) & (hc.threshold_r == k)].iloc[0]
    return r


def pct(v):
    return f"{100 * v:.0f}%"


def pval(p):
    return "p < 0.001" if p < 0.001 else f"p = {p:.2f}" if p >= 0.01 else f"p = {p:.3f}"
