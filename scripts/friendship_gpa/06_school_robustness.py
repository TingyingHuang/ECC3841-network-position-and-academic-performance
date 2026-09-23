"""School-only robustness checks for the project's longitudinal headline test.

All specifications predict GPA at t+1 and control for GPA at t, direct degree,
average contact GPA, and snapshot fixed effects. They differ only in the network
object: outgoing reach, incoming status, or reciprocal ties.
"""
from pathlib import Path

import networkx as nx
import numpy as np
import pandas as pd
import scipy.io as sio
import statsmodels.formula.api as smf
from scipy.sparse.linalg import eigs

ROOT = Path(__file__).resolve().parent.parent.parent
MAT_PATH = ROOT / "data" / "friendship_gpa" / "data.mat"
OUT = ROOT / "output" / "friendship_gpa"
ALPHA_FRACTION = 0.85


def zscore(series):
    sd = series.std()
    return (series - series.mean()) / sd if sd > 0 else series * 0.0


def alpha_max(G):
    if G.number_of_edges() == 0:
        return 1.0
    A = nx.to_scipy_sparse_array(G, format="csr", dtype=float)
    value = eigs(A, k=1, which="LM", return_eigenvectors=False, maxiter=5000)[0]
    return 1.0 / max(abs(value), 1e-6)


def katz(G, direction):
    """Return outgoing-reach or incoming-status Katz centrality."""
    centrality_graph = G.reverse(copy=False) if direction == "outgoing" else G
    return nx.katz_centrality(
        centrality_graph,
        alpha=ALPHA_FRACTION * alpha_max(centrality_graph),
        max_iter=3000,
        tol=1e-6,
    )


def build_panel(kind):
    mat = sio.loadmat(MAT_PATH)
    networks = mat["networks_school"]
    gpas = mat["gpa_school"]
    rows = []
    for t in range(networks.shape[1]):
        A = np.asarray(networks[0, t]).astype(bool)
        if kind == "reciprocal":
            A = A & A.T
        G = nx.from_numpy_array(A.astype(int), create_using=nx.DiGraph)
        direction = "incoming" if kind == "incoming" else "outgoing"
        centrality = katz(G, direction)
        for i in G.nodes():
            contacts = list(G.predecessors(i)) if direction == "incoming" else list(G.successors(i))
            rows.append({
                "student_id": f"school_{i}",
                "time_index": t,
                "gpa": gpas[i, t],
                "katz": centrality[i],
                "in_degree": G.in_degree(i),
                "out_degree": G.out_degree(i),
                "avg_contact_gpa": float(np.mean(gpas[contacts, t])) if contacts else np.nan,
            })
    return pd.DataFrame(rows)


def lagged_regression(panel, reciprocal=False):
    current = panel.rename(columns={
        "gpa": "gpa_t", "katz": "katz_t", "in_degree": "indeg_t",
        "out_degree": "outdeg_t", "avg_contact_gpa": "avg_contact_gpa_t",
    }).copy()
    current["next_time"] = current["time_index"] + 1
    next_gpa = panel[["student_id", "time_index", "gpa"]].rename(
        columns={"time_index": "next_time", "gpa": "gpa_t1"}
    )
    reg = current.merge(next_gpa, on=["student_id", "next_time"], how="inner")
    for col in ["katz_t", "gpa_t", "indeg_t", "outdeg_t"]:
        reg[f"{col}_z"] = zscore(reg[col])
    reg = reg.dropna()
    degree_terms = "indeg_t_z" if reciprocal else "indeg_t_z + outdeg_t_z"
    # Reciprocal networks are symmetric, so in-degree and out-degree are identical.
    # Include one degree term there to avoid a singular design matrix.
    formula = (
        "gpa_t1 ~ katz_t_z + gpa_t_z + avg_contact_gpa_t + " + degree_terms
        + " + C(time_index)"
    )
    return smf.ols(formula, data=reg).fit(
        cov_type="cluster", cov_kwds={"groups": reg["student_id"]}
    ), len(reg), reg.student_id.nunique(), formula


def main():
    results, report = [], []
    for kind in ["outgoing", "incoming", "reciprocal"]:
        model, n, students, formula = lagged_regression(
            build_panel(kind), reciprocal=(kind == "reciprocal")
        )
        coef = model.params["katz_t_z"]
        ci_low, ci_high = model.conf_int().loc["katz_t_z"]
        results.append({
            "network_definition": kind, "n": n, "students": students,
            "katz_coef": coef, "katz_se": model.bse["katz_t_z"],
            "katz_pval": model.pvalues["katz_t_z"],
            "ci_95_low": ci_low, "ci_95_high": ci_high, "r2": model.rsquared,
        })
        report.extend([f"\n{'=' * 72}\n{kind.upper()}\n{formula}\nn={n}, students={students}\n", model.summary().as_text()])

    result = pd.DataFrame(results)
    result.to_csv(OUT / "school_direction_and_reciprocity_robustness.csv", index=False)
    (OUT / "school_direction_and_reciprocity_robustness.txt").write_text("\n".join(report))
    print(result.to_string(index=False))


if __name__ == "__main__":
    main()
