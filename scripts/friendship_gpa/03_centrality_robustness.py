"""
Robustness/diagnostic suite for the Layer-2 "does higher-order network
position add anything beyond raw popularity (degree)" question.

1. Add betweenness & eigenvector centrality to the panel (in addition to
   Katz-Bonacich and in/out-degree already in panel_long.csv), and horse-race
   all of them together against GPA.
2. Alpha-sensitivity sweep: recompute Katz-Bonacich at several attenuation
   levels (as a fraction of the safe alpha_max = 1/lambda_max) and track,
   at each level:
     - its raw correlation with in-degree
     - its own coefficient/significance in a horse race against in/out-degree
   This tells us whether the "missing" information is simply not present
   at any decay radius (i.e. these networks are locally dominated by
   first-order popularity) or whether it appears at some specific alpha.
3. Per-group (per class-year) horse race, to check whether any single
   cohort shows a robust independent Katz effect that is being averaged
   away in the pooled regression.
"""
import time
from pathlib import Path

import networkx as nx
import numpy as np
import pandas as pd
import scipy.io as sio
import statsmodels.formula.api as smf
from scipy.sparse.linalg import eigs

ROOT = Path(__file__).resolve().parent.parent.parent
MAT_PATH = ROOT / "data" / "friendship_gpa" / "data.mat"
PANEL_CSV = ROOT / "output" / "friendship_gpa" / "panel_long.csv"
OUT = ROOT / "output" / "friendship_gpa"

_T0 = time.time()


def log(msg):
    print(f"[{time.time() - _T0:6.1f}s] {msg}", flush=True)


GROUPS = ["school", "freshmen", "sophomores", "juniors", "seniors"]
ALPHA_FRACTIONS = [0.05, 0.2, 0.4, 0.6, 0.8, 0.95]  # fraction of alpha_max=1/lambda_max


def lambda_max_of(G: nx.DiGraph) -> float:
    if G.number_of_edges() == 0:
        return 1.0
    A = nx.to_scipy_sparse_array(G, format="csr", dtype=float)
    try:
        eigval = eigs(A, k=1, which="LM", return_eigenvectors=False, maxiter=5000)
        return max(abs(eigval[0]), 1e-6)
    except Exception:
        return max(1.0, A.sum(axis=1).max())


def katz_at_alpha(G, alpha):
    try:
        return nx.katz_centrality(G, alpha=alpha, max_iter=3000, tol=1e-6)
    except nx.PowerIterationFailedConvergence:
        return nx.katz_centrality_numpy(G, alpha=alpha)


# ---------------------------------------------------------------------------
# STEP 1: extend panel with betweenness + eigenvector
# ---------------------------------------------------------------------------
def build_extended_panel(mat):
    rows = []
    for group_name in GROUPS:
        nets = mat[f"networks_{group_name}"]
        gpa_mat = mat[f"gpa_{group_name}"]
        time_varying = gpa_mat.shape[1] > 1
        n_tp = nets.shape[1]

        for t in range(n_tp):
            A = np.asarray(nets[0, t])
            G = nx.from_numpy_array(A, create_using=nx.DiGraph)
            lam_max = lambda_max_of(G)
            alpha_safe = 0.85 / lam_max

            katz = katz_at_alpha(G, alpha_safe)
            try:
                eig = nx.eigenvector_centrality(G, max_iter=2000, tol=1e-06)
            except nx.PowerIterationFailedConvergence:
                eig = {n: np.nan for n in G.nodes()}
            btw = nx.betweenness_centrality(G, normalized=True)

            in_deg = dict(G.in_degree())
            out_deg = dict(G.out_degree())
            gpa_t = gpa_mat[:, t] if time_varying else gpa_mat[:, 0]

            for i in G.nodes():
                alters = list(G.successors(i))
                afg = float(np.mean(gpa_t[alters])) if alters else np.nan
                rows.append(
                    {
                        "group": group_name,
                        "level": "high_school" if group_name == "school" else "university",
                        "student_id": f"{group_name}_{i}",
                        "time_index": t,
                        "gpa": gpa_t[i],
                        "avg_friend_gpa": afg,
                        "katz_centrality": katz.get(i, np.nan),
                        "eigenvector": eig.get(i, np.nan),
                        "betweenness": btw.get(i, np.nan),
                        "in_degree": in_deg.get(i, 0),
                        "out_degree": out_deg.get(i, 0),
                    }
                )
            log(f"  {group_name} t={t}: betweenness+eigenvector done "
                f"({G.number_of_nodes()} nodes)")

    df = pd.DataFrame(rows)
    out_csv = OUT / "panel_long_extended.csv"
    df.to_csv(out_csv, index=False)
    log(f"Saved extended panel -> {out_csv}")
    return df


# ---------------------------------------------------------------------------
# STEP 2: full horse race with all centrality measures
# ---------------------------------------------------------------------------
def full_horse_race(panel: pd.DataFrame):
    log("FULL HORSE RACE: degree + katz + betweenness + eigenvector")
    reg = panel.dropna(
        subset=["gpa", "katz_centrality", "eigenvector", "betweenness",
                "avg_friend_gpa", "in_degree", "out_degree"]
    ).copy()

    for col in ["katz_centrality", "eigenvector", "betweenness", "in_degree", "out_degree"]:
        reg[f"{col}_z"] = reg.groupby("group")[col].transform(
            lambda s: (s - s.mean()) / s.std() if s.std() > 0 else 0.0
        )

    formula = (
        "gpa ~ katz_centrality_z + eigenvector_z + betweenness_z "
        "+ in_degree_z + out_degree_z + avg_friend_gpa + C(group)"
    )
    m = smf.ols(formula, data=reg).fit(
        cov_type="cluster", cov_kwds={"groups": reg["student_id"]}
    )
    print(m.summary())
    with open(OUT / "robustness_full_horse_race.txt", "w") as f:
        f.write(f"{formula}\nSEs clustered by student.\n\n")
        f.write(m.summary().as_text())
    log("  saved -> robustness_full_horse_race.txt")

    log("Correlation matrix among centrality measures (pooled, z-scored within group):")
    corr = reg[["katz_centrality_z", "eigenvector_z", "betweenness_z",
                "in_degree_z", "out_degree_z"]].corr()
    print(corr.round(3))
    corr.to_csv(OUT / "robustness_centrality_correlations.csv")
    return m


# ---------------------------------------------------------------------------
# STEP 3: alpha-sensitivity sweep
# ---------------------------------------------------------------------------
def alpha_sweep(mat):
    log("ALPHA SENSITIVITY SWEEP")
    records = []
    for group_name in GROUPS:
        nets = mat[f"networks_{group_name}"]
        gpa_mat = mat[f"gpa_{group_name}"]
        time_varying = gpa_mat.shape[1] > 1
        n_tp = nets.shape[1]

        for t in range(n_tp):
            A = np.asarray(nets[0, t])
            G = nx.from_numpy_array(A, create_using=nx.DiGraph)
            lam_max = lambda_max_of(G)
            in_deg = dict(G.in_degree())
            out_deg = dict(G.out_degree())
            gpa_t = gpa_mat[:, t] if time_varying else gpa_mat[:, 0]

            in_deg_arr = np.array([in_deg[i] for i in G.nodes()])

            for frac in ALPHA_FRACTIONS:
                alpha = frac * (1.0 / lam_max)
                katz = katz_at_alpha(G, alpha)
                katz_arr = np.array([katz[i] for i in G.nodes()])
                corr_with_indeg = (
                    np.corrcoef(katz_arr, in_deg_arr)[0, 1]
                    if np.std(katz_arr) > 0 else np.nan
                )
                for i in G.nodes():
                    records.append(
                        {
                            "group": group_name,
                            "time_index": t,
                            "alpha_frac": frac,
                            "student_id": f"{group_name}_{i}",
                            "gpa": gpa_t[i],
                            "katz": katz[i],
                            "in_degree": in_deg[i],
                            "out_degree": out_deg[i],
                            "corr_katz_indeg_snapshot": corr_with_indeg,
                        }
                    )
            log(f"  {group_name} t={t}: alpha sweep done")

    df = pd.DataFrame(records)
    df.to_csv(OUT / "robustness_alpha_sweep_raw.csv", index=False)

    # Summary: avg correlation(katz, in_degree) by alpha_frac
    corr_summary = df.groupby("alpha_frac")["corr_katz_indeg_snapshot"].mean()
    log("Avg corr(katz, in_degree) across snapshots, by alpha (fraction of alpha_max):")
    print(corr_summary)

    # Horse race coefficient on katz at each alpha level (pooled, clustered SE)
    log("Katz coefficient in horse-race-vs-degree regression, at each alpha level:")
    coef_rows = []
    for frac in ALPHA_FRACTIONS:
        sub = df[df["alpha_frac"] == frac].dropna(subset=["gpa", "katz", "in_degree", "out_degree"]).copy()
        sub["katz_z"] = sub.groupby("group")["katz"].transform(
            lambda s: (s - s.mean()) / s.std() if s.std() > 0 else 0.0
        )
        sub["indeg_z"] = sub.groupby("group")["in_degree"].transform(
            lambda s: (s - s.mean()) / s.std() if s.std() > 0 else 0.0
        )
        sub["outdeg_z"] = sub.groupby("group")["out_degree"].transform(
            lambda s: (s - s.mean()) / s.std() if s.std() > 0 else 0.0
        )
        m = smf.ols(
            "gpa ~ katz_z + indeg_z + outdeg_z + C(group)", data=sub
        ).fit(cov_type="cluster", cov_kwds={"groups": sub["student_id"]})
        coef_rows.append(
            {
                "alpha_frac": frac,
                "avg_corr_katz_indeg": corr_summary.get(frac, np.nan),
                "katz_coef": m.params.get("katz_z", np.nan),
                "katz_se": m.bse.get("katz_z", np.nan),
                "katz_pval": m.pvalues.get("katz_z", np.nan),
                "r2": m.rsquared,
            }
        )
    coef_df = pd.DataFrame(coef_rows)
    print(coef_df.to_string(index=False))
    coef_df.to_csv(OUT / "robustness_alpha_sweep_summary.csv", index=False)
    log("  saved -> robustness_alpha_sweep_summary.csv")
    return coef_df


# ---------------------------------------------------------------------------
# STEP 4: per-group horse race
# ---------------------------------------------------------------------------
def per_group_horse_race(panel: pd.DataFrame):
    log("PER-GROUP HORSE RACE (katz vs in/out-degree, within each cohort)")
    reg = panel.dropna(
        subset=["gpa", "katz_centrality", "avg_friend_gpa", "in_degree", "out_degree"]
    ).copy()

    rows = []
    for group_name in GROUPS:
        sub = reg[reg["group"] == group_name].copy()
        for col in ["katz_centrality", "in_degree", "out_degree"]:
            sub[f"{col}_z"] = (sub[col] - sub[col].mean()) / sub[col].std() if sub[col].std() > 0 else 0.0
        m = smf.ols(
            "gpa ~ katz_centrality_z + in_degree_z + out_degree_z + avg_friend_gpa",
            data=sub,
        ).fit(cov_type="cluster", cov_kwds={"groups": sub["student_id"]})
        rows.append(
            {
                "group": group_name,
                "n": len(sub),
                "katz_coef": m.params.get("katz_centrality_z", np.nan),
                "katz_se": m.bse.get("katz_centrality_z", np.nan),
                "katz_pval": m.pvalues.get("katz_centrality_z", np.nan),
                "indeg_coef": m.params.get("in_degree_z", np.nan),
                "indeg_pval": m.pvalues.get("in_degree_z", np.nan),
                "r2": m.rsquared,
            }
        )
    res = pd.DataFrame(rows)
    print(res.to_string(index=False))
    res.to_csv(OUT / "robustness_per_group_horse_race.csv", index=False)
    log("  saved -> robustness_per_group_horse_race.csv")
    return res


def main():
    log("Loading raw .mat file...")
    mat = sio.loadmat(MAT_PATH)

    panel = build_extended_panel(mat)
    full_horse_race(panel)
    alpha_sweep(mat)
    per_group_horse_race(panel)

    log("ALL DONE.")


if __name__ == "__main__":
    main()
