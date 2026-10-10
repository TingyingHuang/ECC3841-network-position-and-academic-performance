"""Presentation 3, model 3: threshold contagion on the real friendship networks
(course: Lecture 3 majority game, Topic 8 complex contagion).

This is a simulation exercise, not an empirical test on GPA. It asks a different
question from scripts 01-07: if some costly behaviour (e.g. extra study effort,
joining a study group) spread by peer threshold -- a student adopts once enough
of the people *they* like have already adopted -- how much would a student's
network position matter for whether that behaviour takes off?

We use Watts's (2002) integer threshold model: student i adopts once at least r
of i's out-neighbours (the students i liked -- i's declared reference group,
same direction as the Katz measure in 01_build_master_dataset.py) have already
adopted. r is the same for every student in a given run; we sweep it from 1
(one friend is enough) to 5 (need five on board) to trace out the cascade
window -- the point at which a behaviour stops reaching most of the network.
Out-degree is sparse here (median 1 in the school network, 3 among freshmen),
so r moves from "almost everyone can be triggered" to "only well-connected
students can be triggered" quickly; that sparsity is itself part of the result.

Starting from a small seed set, we simulate the cascade to convergence and
compare seeding strategies: the highest-Katz students, the highest-out-degree
students, and random students of the same number (averaged over many random
draws of which particular students are seeded). The gap between strategies
shows what network position could plausibly buy as a diffusion mechanism --
independent of whether scripts 01-07 can detect a GPA effect in the data.

Outputs (output/friendship_gpa/):
  contagion_seed_comparison.csv   mean adoption share by group, seed strategy, threshold r, k
  contagion_tipping_point.csv     cascade size swept over r (seed = top-Katz vs top-out-degree vs random)
  contagion_network_stats.csv     out-degree distribution context (why r matters as much as it does)
"""
import importlib.util
import time
from pathlib import Path

import networkx as nx
import numpy as np
import pandas as pd
import scipy.io as sio

ROOT = Path(__file__).resolve().parent.parent.parent
MAT_PATH = ROOT / "data" / "friendship_gpa" / "data.mat"
OUT = ROOT / "output" / "friendship_gpa"

RNG = np.random.default_rng(20251009)
N_REPS = 300             # Monte Carlo repetitions per (group, strategy, r, k) -- randomises the seed draw
R_GRID = [1, 2, 3, 4, 5]        # Watts (2002) integer threshold: friends needed before i adopts
SEED_FRACTIONS = [0.03, 0.08]   # seed set size, as a share of the network
GROUPS = {"school": "high_school", "freshmen": "university"}


def load_01():
    spec = importlib.util.spec_from_file_location("build01", ROOT / "scripts/friendship_gpa/01_build_master_dataset.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def simulate(G: nx.DiGraph, seeds: set, r: int, max_rounds: int) -> tuple[int, int]:
    """Synchronous Watts (2002) integer-threshold update.

    Student i adopts once at least r of the people i liked have adopted.
    Returns (final number of adopters, rounds to stabilise).
    """
    adopted = set(seeds)
    for round_n in range(max_rounds):
        new_adopters = set()
        for i in G.nodes():
            if i in adopted:
                continue
            if sum(1 for j in G.successors(i) if j in adopted) >= r:
                new_adopters.add(i)
        if not new_adopters:
            return len(adopted), round_n
        adopted |= new_adopters
    return len(adopted), max_rounds


def seed_sets(G: nx.DiGraph, katz: dict, k: int):
    nodes = list(G.nodes())
    out_deg = dict(G.out_degree())
    by_katz = sorted(nodes, key=lambda n: katz[n], reverse=True)[:k]
    by_outdeg = sorted(nodes, key=lambda n: out_deg[n], reverse=True)[:k]
    return {"top_katz": set(by_katz), "top_out_degree": set(by_outdeg)}


def run_group(name, mat, b01):
    nets = mat[f"networks_{name}"]
    A = np.asarray(nets[0, 0])
    G = nx.from_numpy_array(A, create_using=nx.DiGraph)
    n = G.number_of_nodes()
    katz = b01.katz_centrality_safe(G)
    max_rounds = n

    rows = []
    for frac in SEED_FRACTIONS:
        k = max(1, round(frac * n))
        strategies = seed_sets(G, katz, k)
        for r_thresh in R_GRID:
            results = {name: [] for name in list(strategies) + ["random"]}
            rounds = {name: [] for name in results}
            for _ in range(N_REPS):
                random_seed = set(RNG.choice(n, size=k, replace=False).tolist())
                for strat_name, seeds in {**strategies, "random": random_seed}.items():
                    final_n, rounds_used = simulate(G, seeds, r_thresh, max_rounds)
                    results[strat_name].append(final_n / n)
                    rounds[strat_name].append(rounds_used)
            for strat_name in results:
                share = np.array(results[strat_name])
                rows.append({
                    "group": name, "level": GROUPS[name], "n_nodes": n, "k_seed": k,
                    "seed_fraction": frac, "threshold_r": r_thresh, "seed_strategy": strat_name,
                    "mean_adoption_share": share.mean(), "se_adoption_share": share.std(ddof=1) / np.sqrt(len(share)),
                    "mean_rounds": float(np.mean(rounds[strat_name])), "n_reps": N_REPS,
                })
    return pd.DataFrame(rows)


def network_stats(name, mat):
    A = np.asarray(mat[f"networks_{name}"][0, 0])
    G = nx.from_numpy_array(A, create_using=nx.DiGraph)
    out_deg = np.array([d for _, d in G.out_degree()])
    rows = []
    for r in R_GRID:
        rows.append({
            "group": name, "level": GROUPS[name], "n_nodes": G.number_of_nodes(),
            "threshold_r": r, "share_can_never_be_triggered": float(np.mean(out_deg < r)),
            "mean_out_degree": float(out_deg.mean()), "median_out_degree": float(np.median(out_deg)),
        })
    return rows


def main():
    t0 = time.time()
    b01 = load_01()
    mat = sio.loadmat(MAT_PATH)

    all_rows, stat_rows = [], []
    for name in GROUPS:
        print(f"[{time.time()-t0:6.1f}s] simulating {name} ...")
        df = run_group(name, mat, b01)
        all_rows.append(df)
        print(df.round(3).to_string(index=False))
        stat_rows += network_stats(name, mat)

    full = pd.concat(all_rows, ignore_index=True)
    full.to_csv(OUT / "contagion_seed_comparison.csv", index=False)
    print(f"[{time.time()-t0:6.1f}s] saved -> contagion_seed_comparison.csv")

    pd.DataFrame(stat_rows).to_csv(OUT / "contagion_network_stats.csv", index=False)
    print(f"[{time.time()-t0:6.1f}s] saved -> contagion_network_stats.csv")

    # Tipping-point view: fix the smaller seed fraction, show advantage of top-Katz
    # (and top-out-degree) seeding over random seeding as r sweeps from loose to tight.
    small = full[full.seed_fraction == SEED_FRACTIONS[0]].copy()
    piv = small.pivot_table(index=["group", "level", "threshold_r"], columns="seed_strategy",
                             values="mean_adoption_share").reset_index()
    piv["advantage_top_katz_vs_random"] = piv["top_katz"] - piv["random"]
    piv["advantage_top_outdeg_vs_random"] = piv["top_out_degree"] - piv["random"]
    piv.to_csv(OUT / "contagion_tipping_point.csv", index=False)
    print(piv.round(3).to_string(index=False))
    print(f"[{time.time()-t0:6.1f}s] saved -> contagion_tipping_point.csv")


if __name__ == "__main__":
    main()
