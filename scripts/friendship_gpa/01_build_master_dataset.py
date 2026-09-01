"""
Load Smirnov & Thurner (2017) replication data (data.mat) and build a
long-format panel: one row per (group, student, time snapshot) with
- gpa (time-varying for the 'school' group, static/repeated for university groups)
- avg_friend_gpa (from that snapshot's directed "like" network)
- katz-bonacich centrality (from that snapshot's network)
- in_degree / out_degree
- level: 'high_school' vs 'university'
- group: school / freshmen / sophomores / juniors / seniors

Networks are directed ("i gave a like to j" -> A[i,j] = 1), asymmetric.
Katz-Bonacich centrality is computed on each snapshot's directed network
using networkx.katz_centrality with alpha set conservatively below
1/largest-eigenvalue for guaranteed convergence.
"""
import time
from pathlib import Path

import networkx as nx
import numpy as np
import pandas as pd
import scipy.io as sio

ROOT = Path(__file__).resolve().parent.parent.parent
MAT_PATH = ROOT / "data" / "friendship_gpa" / "data.mat"
OUT = ROOT / "output" / "friendship_gpa"
OUT.mkdir(parents=True, exist_ok=True)

_T0 = time.time()


def log(msg):
    print(f"[{time.time() - _T0:6.1f}s] {msg}", flush=True)


GROUPS = ["school", "freshmen", "sophomores", "juniors", "seniors"]
LEVEL = {
    "school": "high_school",
    "freshmen": "university",
    "sophomores": "university",
    "juniors": "university",
    "seniors": "university",
}


def katz_centrality_safe(G: nx.DiGraph) -> dict:
    """Katz-Bonacich centrality with alpha chosen safely below 1/lambda_max."""
    if G.number_of_edges() == 0:
        return {n: 0.0 for n in G.nodes()}
    A = nx.to_scipy_sparse_array(G, format="csr", dtype=float)
    try:
        from scipy.sparse.linalg import eigs

        eigval = eigs(A, k=1, which="LM", return_eigenvectors=False, maxiter=5000)
        lam_max = abs(eigval[0])
    except Exception:
        lam_max = max(1.0, A.sum(axis=1).max())
    if lam_max <= 0:
        lam_max = 1.0
    alpha = 0.85 / lam_max  # conservative safety margin below 1/lambda_max
    try:
        return nx.katz_centrality(G, alpha=alpha, max_iter=2000, tol=1e-6)
    except nx.PowerIterationFailedConvergence:
        return nx.katz_centrality_numpy(G, alpha=alpha)


def process_group(mat, group_name):
    nets = mat[f"networks_{group_name}"]
    gpa = mat[f"gpa_{group_name}"]
    n_timepoints = nets.shape[1]
    n_students = gpa.shape[0]
    time_varying_gpa = gpa.shape[1] > 1

    rows = []
    for t in range(n_timepoints):
        A = np.asarray(nets[0, t])
        G = nx.from_numpy_array(A, create_using=nx.DiGraph)

        katz = katz_centrality_safe(G)
        in_deg = dict(G.in_degree())
        out_deg = dict(G.out_degree())

        # average GPA of friends: mean GPA among out-neighbors ("who I liked")
        gpa_t = gpa[:, t] if time_varying_gpa else gpa[:, 0]
        avg_friend_gpa = {}
        for i in range(n_students):
            alters = list(G.successors(i))
            avg_friend_gpa[i] = float(np.mean(gpa_t[alters])) if alters else np.nan

        for i in range(n_students):
            rows.append(
                {
                    "group": group_name,
                    "level": LEVEL[group_name],
                    "student_id": f"{group_name}_{i}",
                    "time_index": t,
                    "n_timepoints": n_timepoints,
                    "gpa": gpa_t[i],
                    "gpa_time_varying": time_varying_gpa,
                    "avg_friend_gpa": avg_friend_gpa[i],
                    "katz_centrality": katz.get(i, np.nan),
                    "in_degree": in_deg.get(i, 0),
                    "out_degree": out_deg.get(i, 0),
                }
            )
        log(f"  {group_name} t={t}: {G.number_of_nodes()} nodes, "
            f"{G.number_of_edges()} edges, katz done")

    return pd.DataFrame(rows)


def main():
    log(f"Loading {MAT_PATH.name} ...")
    mat = sio.loadmat(MAT_PATH)

    all_dfs = []
    for group_name in GROUPS:
        log(f"Processing group: {group_name}")
        df = process_group(mat, group_name)
        all_dfs.append(df)

    panel = pd.concat(all_dfs, ignore_index=True)
    out_csv = OUT / "panel_long.csv"
    panel.to_csv(out_csv, index=False)
    log(f"Saved panel ({len(panel):,} rows) -> {out_csv}")

    log("Summary by group:")
    print(panel.groupby("group").agg(
        n_students=("student_id", "nunique"),
        n_timepoints=("time_index", "nunique"),
        mean_gpa=("gpa", "mean"),
        mean_katz=("katz_centrality", "mean"),
        mean_indeg=("in_degree", "mean"),
    ))
    log("DONE.")


if __name__ == "__main__":
    main()
