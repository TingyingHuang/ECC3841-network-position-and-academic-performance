"""
Conceptual figures for the visual-heavy Presentation 1.
Each figure carries one idea so the slide needs almost no text.

Run before build_visual_deck.py.
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import networkx as nx
from matplotlib.patches import Circle, FancyBboxPatch

ASSETS = Path(__file__).resolve().parent / "assets"
ASSETS.mkdir(exist_ok=True)

INK = "#19180F"
GRAY = "#6B6656"
FAINT = "#E1DBCD"
BLUE = "#2A78D6"
ORANGE = "#EB6834"
GREEN = "#2E9E5B"
RED = "#D2413A"
BG = "#FAF9F6"

plt.rcParams["font.family"] = "DejaVu Sans"
plt.rcParams["mathtext.fontset"] = "dejavusans"


def save(fig, name):
    fig.savefig(ASSETS / name, dpi=200, bbox_inches="tight", pad_inches=0.10,
                facecolor=BG)
    plt.close(fig)
    print("  wrote", name)


def line(ax, a, b, color=FAINT, lw=1.2, z=1, alpha=1.0):
    ax.plot([a[0], b[0]], [a[1], b[1]], color=color, lw=lw, zorder=z, alpha=alpha,
            solid_capstyle="round")


# ============================================================ 1. puzzle
def fig_puzzle():
    EDGE = "#B9B3A4"
    BGN = "#EAE5DA"
    BGE = "#8A8574"
    PEACH = "#F0B48A"
    REDO = "#D84A1E"
    fig, axes = plt.subplots(1, 2, figsize=(13, 5.3))
    for ax in axes:
        ax.set_aspect("equal"); ax.axis("off")

    # ---- left: one tight circle (many mutual links, no reach) ----
    ax = axes[0]
    ax.set_xlim(-2.2, 2.2); ax.set_ylim(-2.5, 2.4)
    ego = (0.0, 0.05)
    ang = np.linspace(np.pi / 2, np.pi / 2 + 2 * np.pi, 6)[:-1]
    fr = [(1.35 * np.cos(a), 1.35 * np.sin(a)) for a in ang]
    for i in range(5):
        line(ax, fr[i], fr[(i + 1) % 5], color=EDGE, lw=1.6)
        line(ax, ego, fr[i], color=EDGE, lw=1.6)
    ax.scatter(*zip(*fr), s=440, fc=BGN, ec=BGE, lw=1.1, zorder=3)
    ax.scatter([ego[0]], [ego[1]], s=600, c=BLUE, ec=INK, lw=1.2, zorder=4)
    ax.text(0, -2.25, "Student 1   ·   5 friends, one tight circle",
            ha="center", fontsize=13, fontweight="bold", color=INK)

    # ---- right: same 5 friends, wide reach across groups ----
    ax = axes[1]
    ax.set_xlim(-3.1, 3.1); ax.set_ylim(-2.5, 2.4)
    ego = (0.0, -0.35)
    fr = [(-1.6, 0.55), (-0.7, 1.0), (0.2, 1.05), (1.05, 0.6), (1.75, -0.35)]
    far = {0: [(-2.6, -0.05), (-2.25, 1.25)], 1: [(-0.95, 1.75)],
           2: [(0.4, 1.75), (1.2, 1.45)], 3: [(1.55, 1.3)],
           4: [(2.7, 0.2), (2.4, -1.2)]}
    for f in fr:
        line(ax, ego, f, color=EDGE, lw=1.6)
    allfar = []
    for i, f in enumerate(fr):
        for g in far.get(i, []):
            line(ax, f, g, color=EDGE, lw=1.4)
            allfar.append(g)
    ax.scatter(*zip(*allfar), s=320, fc=BGN, ec=BGE, lw=1.0, zorder=3)
    ax.scatter(*zip(*fr), s=400, c=PEACH, ec=INK, lw=1.0, zorder=4)
    ax.scatter([ego[0]], [ego[1]], s=600, c=REDO, ec=INK, lw=1.2, zorder=5)
    ax.text(0, -2.25, "Student 2   ·   5 friends, reach across the school",
            ha="center", fontsize=13, fontweight="bold", color=INK)

    fig.text(0.5, 0.97, "Same 5 friends.   Same average friend GPA.   Same grade?",
             ha="center", va="top", fontsize=15, color=ORANGE, fontweight="bold")
    fig.subplots_adjust(left=0.02, right=0.98, top=0.88, bottom=0.03, wspace=0.05)
    save(fig, "fig_puzzle.png")


# ============================================================ 2. data
def fig_data():
    rng = np.random.default_rng(4)
    sizes = [22, 20, 20, 18, 16, 14]
    probs = (np.eye(6) * 0.34 + 0.004).tolist()
    G = nx.stochastic_block_model(sizes, probs, seed=4)
    lab, idx = {}, 0
    for b, s in enumerate(sizes):
        for _ in range(s):
            lab[idx] = b; idx += 1
    block_gpa = np.array([-1.35, -0.8, -0.15, 0.4, 0.9, 1.4])
    gpa = np.array([block_gpa[lab[n]] + rng.normal(0, 0.26) for n in G.nodes()])
    pos = nx.spring_layout(G, seed=4, k=0.9, iterations=250)

    fig, ax = plt.subplots(figsize=(12.5, 6.4))
    ax.axis("off"); ax.set_aspect("equal", adjustable="datalim")
    for u, v in G.edges():
        line(ax, pos[u], pos[v], color="#D8D2C4", lw=0.6, alpha=0.7)
    deg = dict(G.degree())
    ax.scatter([pos[n][0] for n in G.nodes()], [pos[n][1] for n in G.nodes()],
               s=[40 + 22 * deg[n] for n in G.nodes()], c=gpa, cmap="RdYlBu",
               vmin=-1.7, vmax=1.7, edgecolors=INK, linewidths=0.5, zorder=3)
    ax.text(0.5, 1.05, "One school network   ·   colour = GPA   ·   size = number of ties",
            transform=ax.transAxes, ha="center", fontsize=13, fontweight="bold", color=INK)
    ax.text(0.5, -0.04, "friends cluster by GPA  —  and we watch it over 38 snapshots",
            transform=ax.transAxes, ha="center", fontsize=12, color=GRAY, style="italic")
    fig.subplots_adjust(left=0.02, right=0.98, top=0.95, bottom=0.06)
    save(fig, "fig_data.png")


# ============================================================ 3. identification
def fig_identification():
    fig, ax = plt.subplots(figsize=(13, 4.4))
    ax.axis("off"); ax.set_xlim(0, 13); ax.set_ylim(0, 4.4)

    ax.annotate("", xy=(12.4, 1.0), xytext=(0.6, 1.0),
                arrowprops=dict(arrowstyle="-|>", color=GRAY, lw=2))
    for x, lb in [(3.2, "t"), (9.8, "t + 1")]:
        ax.plot([x, x], [0.85, 1.15], color=GRAY, lw=2)
        ax.text(x, 0.55, lb, ha="center", fontsize=13, color=GRAY)

    def box(x, txt, fc, ec):
        ax.add_patch(FancyBboxPatch((x - 1.8, 1.9), 3.6, 0.9,
                                    boxstyle="round,pad=0.08", fc=fc, ec=ec, lw=1.6))
        ax.text(x, 2.35, txt, ha="center", va="center", fontsize=13,
                fontweight="bold", color=INK)

    box(3.2, "network position", "#E9F0FA", BLUE)
    box(9.8, "GPA", "#E9F5EC", GREEN)
    ax.annotate("", xy=(7.8, 2.35), xytext=(5.2, 2.35),
                arrowprops=dict(arrowstyle="-|>", color=GREEN, lw=3))
    ax.text(6.5, 1.75, "does it predict later grades?", ha="center", fontsize=12,
            color=GREEN, fontweight="bold")

    ax.annotate("", xy=(4.4, 3.5), xytext=(8.6, 3.5),
                arrowprops=dict(arrowstyle="-|>", color="#BDB7A8", lw=2,
                                linestyle=(0, (5, 4))))
    ax.plot([6.5], [3.5], marker="x", ms=14, mew=3, color=RED, zorder=5)
    ax.text(6.5, 4.05, "reverse story: good grades → more friends   (ruled out by time order)",
            ha="center", fontsize=11.5, color=GRAY)
    ax.text(6.5, 0.05, "we also hold past GPA fixed — compare students at the same starting grade",
            ha="center", fontsize=11.5, color=INK, style="italic")
    fig.subplots_adjust(left=0.02, right=0.98, top=0.99, bottom=0.02)
    save(fig, "fig_identification.png")


# ============================================================ 4a. S&T formula (standalone)
def fig_st_formula():
    fig, ax = plt.subplots(figsize=(10.5, 2.15))
    ax.axis("off"); ax.set_xlim(0, 13); ax.set_ylim(0, 2.6)
    cx = 3.5
    ax.text(cx, 1.95, "sum of your friends' GPAs", fontsize=18, ha="center",
            va="center", color=INK, fontweight="bold")
    ax.plot([cx - 3.0, cx + 3.0], [1.42, 1.42], color=INK, lw=2.2)
    ax.text(cx, 0.9, "number of friends", fontsize=18, ha="center",
            va="center", color=INK, fontweight="bold")
    ax.text(7.3, 1.42, "=", fontsize=26, ha="center", va="center", color=INK)
    ax.text(8.0, 1.42, "average friend GPA", fontsize=18, ha="left",
            va="center", color=INK, fontweight="bold")
    ax.text(6.3, 0.12,
            r"$s_i = (\sum_j g_{ij}\,\mathrm{GPA}_j)\,/\,(\sum_j g_{ij})$"
            + "        network * gpa ./ sum(network, 2)",
            fontsize=11.5, ha="center", va="center", color=INK)
    fig.subplots_adjust(left=0.02, right=0.98, top=0.98, bottom=0.02)
    save(fig, "fig_st_formula.png")


# ============================================================ 4b. prior work: first ring
def fig_priorwork():
    rng = np.random.default_rng(5)
    fig, ax = plt.subplots(figsize=(10.5, 5.4))
    ax.axis("off")
    ax.set_xlim(-4.6, 4.6); ax.set_ylim(-2.9, 2.6)
    ax.set_aspect("equal", adjustable="datalim")
    ego = (0.0, 0.0)
    fa = np.linspace(0, 2 * np.pi, 4, endpoint=False) + 0.6
    fr = [(ego[0] + 0.95 * np.cos(a), ego[1] + 0.95 * np.sin(a)) for a in fa]
    ba = rng.uniform(0, 2 * np.pi, 32)
    brd = rng.uniform(2.2, 4.0, 32)
    bg = [(r * np.cos(a), r * np.sin(a)) for a, r in zip(ba, brd)]
    for f in fr:
        for b in bg:
            if rng.random() < 0.13:
                line(ax, f, b, color="#EAE5D9", lw=0.7)
    for f in fr:
        line(ax, ego, f, color=GRAY, lw=2)
    ax.scatter(*zip(*bg), s=110, fc="#EAE5D9", ec="#D3CDBE", lw=0.6, zorder=2)
    ax.scatter(*zip(*fr), s=300, c=BLUE, ec=INK, lw=1, zorder=3)
    ax.scatter(*ego, s=480, c=ORANGE, ec=INK, lw=1.4, zorder=4)
    ax.add_patch(Circle(ego, 1.55, fill=False, ec=ORANGE, lw=2.2,
                        linestyle=(0, (7, 5)), zorder=5))
    ax.text(0, 2.15, "what Smirnov & Thurner's measure sees",
            ha="center", fontsize=13.5, color=ORANGE, fontweight="bold")
    ax.text(0, -2.7, "everything beyond the first ring is ignored",
            ha="center", fontsize=13, color=GRAY, style="italic")
    fig.subplots_adjust(left=0.03, right=0.97, top=0.97, bottom=0.03)
    save(fig, "fig_priorwork.png")


# ============================================================ 5. the idea
def fig_idea():
    fig, ax = plt.subplots(figsize=(12.5, 6.2))
    ax.axis("off"); ax.set_xlim(-3.7, 3.7); ax.set_ylim(-3.1, 3.4)
    ax.set_aspect("equal", adjustable="datalim")
    ego = (0.0, 0.35)
    rings = [(1.0, "ring 1  ·  × 1", INK, 6, 340),
             (2.0, "ring 2  ·  × φ", "#6C7C9A", 11, 230),
             (3.0, "ring 3  ·  × φ²", "#A7ADBA", 15, 150)]
    for rad, lab, col, count, sz in rings:
        ang = np.linspace(0, 2 * np.pi, count, endpoint=False) + np.pi / count
        pts = [(ego[0] + rad * np.cos(a), ego[1] + rad * np.sin(a)) for a in ang]
        for p in pts:
            line(ax, ego, p, color="#E6E1D4", lw=0.6)
        ax.scatter([p[0] for p in pts], [p[1] for p in pts], s=sz,
                   fc="white", ec=col, lw=1.4, zorder=3)
    ax.scatter(*ego, s=520, c=ORANGE, ec=INK, lw=1.4, zorder=4)

    # legend box top-left
    for i, (rad, lab, col, *_ ) in enumerate(rings):
        yy = 2.95 - i * 0.42
        ax.scatter([-3.4], [yy], s=110, fc="white", ec=col, lw=1.5)
        ax.text(-3.15, yy, lab, ha="left", va="center", fontsize=12,
                color=col, fontweight="bold")
    ax.text(0.5, 1.0, "Katz-Bonacich centrality  =  weighted count over every ring",
            transform=ax.transAxes, ha="center", fontsize=14, color=BLUE, fontweight="bold")

    x0, x1, y = -3.3, 3.3, -2.75
    grad = np.linspace(0, 1, 256).reshape(1, -1)
    ax.imshow(grad, extent=[x0, x1, y - 0.18, y + 0.18], aspect="auto",
              cmap="RdYlBu_r", alpha=0.85, zorder=2)
    ax.add_patch(plt.Rectangle((x0, y - 0.18), x1 - x0, 0.36, fill=False,
                               ec="#6B6656", lw=1))
    ax.text(x0, y + 0.52, "φ small  →  just ring 1  =  popularity",
            ha="left", fontsize=12, color=INK)
    ax.text(x1, y + 0.52, "φ large  →  all rings  =  reach / position",
            ha="right", fontsize=12, color=INK)
    fig.subplots_adjust(left=0.03, right=0.97, top=0.95, bottom=0.04)
    save(fig, "fig_idea.png")


# ============================================================ 6. filter
def fig_filter():
    fig, ax = plt.subplots(figsize=(11.5, 6.6))
    ax.axis("off"); ax.set_xlim(0, 11.5); ax.set_ylim(0, 6.6)
    cx = 5.75

    ax.add_patch(FancyBboxPatch((cx - 3.1, 5.75 - 0.42), 6.2, 0.84,
                                boxstyle="round,pad=0.05", fc="#E9F0FA", ec=BLUE, lw=1.8))
    ax.text(cx, 5.75, "a student's network position   (Katz-Bonacich)",
            ha="center", va="center", fontsize=13, fontweight="bold", color=INK)
    ax.annotate("", xy=(cx, 5.05), xytext=(cx, 5.3),
                arrowprops=dict(arrowstyle="-|>", color=GRAY, lw=2))

    bands = [
        (4.55, "−  was always a strong student    (past GPA)"),
        (3.35, "−  has high-GPA friends    (average friend GPA)"),
        (2.15, "−  is simply popular    (in / out-degree)"),
    ]
    for y, txt in bands:
        ax.add_patch(FancyBboxPatch((cx - 4.4, y - 0.42), 8.8, 0.84,
                                    boxstyle="round,pad=0.05", fc="#F3EFE6",
                                    ec="#C9C2B1", lw=1.3))
        ax.text(cx, y, txt, ha="center", va="center", fontsize=12.5, color=INK)

    ax.annotate("", xy=(cx, 1.35), xytext=(cx, 1.6),
                arrowprops=dict(arrowstyle="-|>", color=GRAY, lw=2))
    ax.add_patch(FancyBboxPatch((cx - 3.5, 0.6 - 0.42), 7.0, 0.84,
                                boxstyle="round,pad=0.05", fc="#E9F5EC", ec=GREEN, lw=1.8))
    ax.text(cx, 0.6, "what is left   =   the structural effect   β₁",
            ha="center", va="center", fontsize=13.5, fontweight="bold", color=INK)
    fig.subplots_adjust(left=0.02, right=0.98, top=0.98, bottom=0.02)
    save(fig, "fig_filter.png")


# ============================================================ 7. predictions
def fig_predictions():
    fig, ax = plt.subplots(figsize=(12.5, 5.0))
    ax.axis("off"); ax.set_xlim(0, 12.5); ax.set_ylim(0, 5.0)
    ax.add_patch(Circle((1.7, 2.5), 0.5, fc="#E9F0FA", ec=BLUE, lw=1.8))
    ax.text(1.7, 2.5, "β₁ ?", ha="center", va="center", fontsize=16,
            fontweight="bold", color=INK)
    rows = [
        (4.2, GREEN, "β₁ > 0", "position helps — information, study support"),
        (2.5, GRAY, "β₁ = 0", "the help and the time cost cancel out"),
        (0.8, RED, "β₁ < 0", "reaching wide takes time from studying"),
    ]
    for y, col, tag, desc in rows:
        ax.annotate("", xy=(4.3, y), xytext=(2.3, 2.5),
                    arrowprops=dict(arrowstyle="-|>", color=col, lw=2.6))
        ax.add_patch(FancyBboxPatch((4.5, y - 0.42), 2.0, 0.84,
                                    boxstyle="round,pad=0.05", fc="white", ec=col, lw=1.8))
        ax.text(5.5, y, tag, ha="center", va="center", fontsize=14,
                fontweight="bold", color=col)
        ax.text(6.9, y, desc, ha="left", va="center", fontsize=12.5, color=INK)
    fig.subplots_adjust(left=0.02, right=0.98, top=0.98, bottom=0.02)
    save(fig, "fig_predictions.png")


if __name__ == "__main__":
    print("building visual assets ...")
    fig_puzzle()
    fig_data()
    fig_identification()
    fig_st_formula()
    fig_priorwork()
    fig_idea()
    fig_filter()
    fig_predictions()
    print("done.")
