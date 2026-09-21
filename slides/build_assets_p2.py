"""
Figures for Presentation 2 (progress report / preliminary results).
Numbers are hard-coded from output/friendship_gpa/*.txt|csv -- see
progress_brief.pdf for the source of each.

    fig_p2_three_specs.png   naive vs pooled-headline vs corrected coefficient
    fig_p2_phi_compare.png   phi sweep: pooled (before fix) vs school-only (after fix)
    fig_p2_gpa_gap.png       why the pooled test couldn't control own-past-GPA
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyBboxPatch

ASSETS = Path(__file__).resolve().parent / "assets_p2"
ASSETS.mkdir(exist_ok=True)

INK = "#19180F"
GRAY = "#6B6656"
FAINT = "#CFC9BB"
BLUE = "#2A78D6"
ORANGE = "#EB6834"
GREEN = "#2E9E5B"
RED = "#D2413A"
BG = "#FAF9F6"

plt.rcParams["font.family"] = "DejaVu Sans"


def save(fig, name):
    fig.savefig(ASSETS / name, dpi=200, bbox_inches="tight", pad_inches=0.12,
                facecolor=BG)
    plt.close(fig)
    print("  wrote", name)


# ============================================================ 1. three specs
def fig_three_specs():
    specs = [
        ("Naive\n(no popularity control)", 0.093, 0.012, True, "+0.093"),
        ("Pooled headline\n(all 5 groups, no own-GPA)", -0.0415, 0.019, True, "−0.0415"),
        ("Corrected\n(school only, own-GPA in)", 0.0046, 0.006, False, "+0.0046"),
    ]
    fig, ax = plt.subplots(figsize=(11, 5.6))
    ax.axhline(0, color=GRAY, lw=1.2, zorder=1)
    xs = [0, 1.4, 2.8]
    for x, (label, coef, se, sig, txt) in zip(xs, specs):
        col = (RED if coef < 0 else GREEN) if sig else GRAY
        ci = 1.96 * se
        ax.errorbar([x], [coef], yerr=[[ci], [ci]], fmt="o", color=col,
                    ecolor=col, elinewidth=2.4, capsize=8, ms=14, zorder=3)
        ax.text(x, coef + ci + 0.014, txt, ha="center", fontsize=14,
                fontweight="bold", color=col)
        tag = "significant" if sig else "not significant"
        ax.text(x, coef - ci - 0.016, tag, ha="center", fontsize=11,
                color=col, style="italic")
    ax.set_xticks(xs)
    ax.set_xticklabels([s[0] for s in specs], fontsize=12.5, color=INK)
    ax.set_ylabel("Katz-Bonacich coefficient (standardized)", fontsize=12, color=INK)
    ax.set_ylim(-0.09, 0.14)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    ax.spines["left"].set_color(GRAY)
    ax.spines["bottom"].set_color(GRAY)
    ax.tick_params(colors=GRAY)
    ax.set_title("Three specifications, three different pictures",
                 fontsize=15, fontweight="bold", color=INK, pad=14)
    fig.subplots_adjust(left=0.12, right=0.97, top=0.88, bottom=0.14)
    save(fig, "fig_p2_three_specs.png")


# ============================================================ 2. phi compare
def fig_phi_compare():
    fracs = [0.05, 0.20, 0.40, 0.60, 0.80, 0.95]
    pooled = [0.0820, 0.0216, -0.0344, -0.0513, -0.0477, -0.0356]
    pooled_p = [0.012, 0.598, 0.407, 0.115, 0.031, 0.011]
    school = [-0.0042, -0.0019, 0.0009, 0.0029, 0.0044, 0.0048]
    school_p = [0.62, 0.84, 0.93, 0.74, 0.51, 0.36]

    fig, ax = plt.subplots(figsize=(11, 5.8))
    ax.axhline(0, color=GRAY, lw=1.1, zorder=1)

    ax.plot(fracs, pooled, color=ORANGE, lw=2.2, zorder=2, label="Pooled, all 5 groups (no own-GPA control)")
    for f, v, p in zip(fracs, pooled, pooled_p):
        ax.scatter([f], [v], s=110, facecolors=(ORANGE if p < 0.05 else "white"),
                   edgecolors=ORANGE, linewidths=2, zorder=4)

    ax.plot(fracs, school, color=BLUE, lw=2.2, zorder=2, label="School only, own-GPA controlled")
    for f, v, p in zip(fracs, school, school_p):
        ax.scatter([f], [v], s=110, facecolors=(BLUE if p < 0.05 else "white"),
                   edgecolors=BLUE, linewidths=2, zorder=4)

    ax.set_xlabel(r"$\phi$ (fraction of ceiling)", fontsize=12.5, color=INK)
    ax.set_ylabel("Katz-Bonacich coefficient", fontsize=12.5, color=INK)
    ax.set_xticks(fracs)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    ax.spines["left"].set_color(GRAY)
    ax.spines["bottom"].set_color(GRAY)
    ax.tick_params(colors=GRAY)
    ax.legend(loc="lower left", frameon=False, fontsize=11.5)
    ax.set_title("Filled marker = significant at 5%.  Once own past GPA is controlled, the line goes flat.",
                 fontsize=13, color=INK, pad=12)
    fig.subplots_adjust(left=0.11, right=0.97, top=0.88, bottom=0.13)
    save(fig, "fig_p2_phi_compare.png")


# ============================================================ 3. gpa gap
def fig_gpa_gap():
    groups = [("School", 6, True), ("Freshmen", 1, False), ("Sophomores", 1, False),
              ("Juniors", 1, False), ("Seniors", 1, False)]
    fig, ax = plt.subplots(figsize=(11, 5.2))
    ax.axis("off")
    y0 = len(groups)
    for i, (name, n_meas, varies) in enumerate(groups):
        y = y0 - i
        ax.text(-0.3, y, name, ha="right", va="center", fontsize=13,
                fontweight="bold", color=INK)
        col = GREEN if varies else GRAY
        if varies:
            for k in range(n_meas):
                ax.scatter([k * 0.55], [y], s=170, fc=col, ec=INK, lw=1, zorder=3)
                if k > 0:
                    ax.plot([(k - 1) * 0.55, k * 0.55], [y, y], color=col, lw=1.6, zorder=2)
            ax.text(3.4, y, "GPA measured 6 times  →  own past GPA exists",
                    va="center", fontsize=11.5, color=GREEN)
        else:
            ax.scatter([0], [y], s=170, fc=FAINT, ec=GRAY, lw=1, zorder=3)
            ax.text(3.4, y, "GPA measured once  →  own past GPA is undefined",
                    va="center", fontsize=11.5, color=GRAY)
    ax.set_xlim(-2.6, 9.5)
    ax.set_ylim(0.3, y0 + 0.8)
    fig.subplots_adjust(left=0.02, right=0.98, top=0.97, bottom=0.03)
    save(fig, "fig_p2_gpa_gap.png")


if __name__ == "__main__":
    print("building P2 assets ...")
    fig_three_specs()
    fig_phi_compare()
    fig_gpa_gap()
    print("done.")
