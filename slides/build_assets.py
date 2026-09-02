"""
Regenerate the image assets for Presentation 1 so the deck matches the
current research_brief.pdf notation:

    u_i = a x_i - 1/2 x_i^2 + phi * sum_j g_ij x_i x_j
    x_i = a + phi * sum_j g_ij x_j
    x   = a (I - phi G)^{-1} 1 = a b(g, phi)
    phi < 1 / lambda_max

Plus two new conceptual figures:
    phi_dial.png        -- phi as a dial from "popularity" to "reach"
    timeline_snapshots.png -- the longitudinal t -> t+1 design

Run this before build_presentation1.py.
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Rectangle, Circle, FancyArrowPatch

ASSETS = Path(__file__).resolve().parent / "assets"
ASSETS.mkdir(exist_ok=True)

INK = "#19180F"
GRAY = "#55503F"
BLUE = "#2A78D6"
ORANGE = "#EB6834"
BG = "#FAF9F6"

plt.rcParams["font.family"] = "DejaVu Sans"
plt.rcParams["mathtext.fontset"] = "dejavusans"


# --------------------------------------------------------------- equations
def render_eq(tex_lines, fname, fontsize=30):
    fig = plt.figure(figsize=(9, 1.25 * len(tex_lines)))
    fig.patch.set_alpha(0)
    body = "\n".join(f"${ln}$" for ln in tex_lines)
    fig.text(0.5, 0.5, body, fontsize=fontsize, ha="center", va="center",
             color=INK, linespacing=1.9)
    fig.savefig(ASSETS / fname, dpi=300, bbox_inches="tight",
                pad_inches=0.10, transparent=True)
    plt.close(fig)
    print("  wrote", fname)


render_eq([r"u_i \;=\; a\,x_i \;-\; \frac{1}{2}\,x_i^{2}"
           r"\;+\; \phi \sum_j g_{ij}\,x_i x_j"], "eq_utility.png")

render_eq([r"x_i \;=\; a \;+\; \phi \sum_j g_{ij}\,x_j"], "eq_bestresponse.png")

render_eq([r"\mathbf{x} \;=\; a\,(\mathbf{I}-\phi\mathbf{G})^{-1}\mathbf{1}"
           r"\;=\; a\;\mathbf{b}(g,\phi)"], "eq_equilibrium.png")

render_eq([r"\phi \;<\; 1/\lambda_{\mathrm{max}}"], "eq_condition.png", fontsize=30)

render_eq([
    r"\mathrm{GPA}_{i,\,t+1} \;=\; \beta_0 \;+\; \beta_1\,\mathrm{Katz}_{i,t}(\phi)"
    r"\;+\; \beta_2\,\mathrm{GPA}_{i,t}\;+\; \beta_3\,\overline{\mathrm{GPA}}^{\,\mathrm{friends}}_{i,t}",
    r"\;+\;\beta_4\,\mathrm{InDeg}_{i,t}\;+\;\beta_5\,\mathrm{OutDeg}_{i,t}"
    r"\;+\;\gamma_{\mathrm{group}}\;+\;\varepsilon_{i,t}",
], "eq_regression.png", fontsize=24)


# --------------------------------------------------------------- phi dial
def _hub(ax, cx, cy, r=0.42):
    ang = np.linspace(0, 2 * np.pi, 7)[:-1]
    for a in ang:
        x, y = cx + r * np.cos(a), cy + r * np.sin(a)
        ax.plot([cx, x], [cy, y], color="#B9B3A4", lw=1.1, zorder=1)
        ax.add_patch(Circle((x, y), 0.085, fc="#E7E2D6", ec="#8A8574", lw=0.8, zorder=2))
    ax.add_patch(Circle((cx, cy), 0.13, fc=BLUE, ec=INK, lw=1.0, zorder=3))


def _bridge(ax, cx, cy):
    left = [(cx - 0.62, cy + 0.28), (cx - 0.72, cy - 0.10), (cx - 0.42, cy - 0.34)]
    right = [(cx + 0.62, cy + 0.28), (cx + 0.72, cy - 0.10), (cx + 0.42, cy - 0.34)]
    for grp in (left, right):
        for i in range(len(grp)):
            for j in range(i + 1, len(grp)):
                ax.plot([grp[i][0], grp[j][0]], [grp[i][1], grp[j][1]],
                        color="#B9B3A4", lw=1.0, zorder=1)
    ax.plot([left[1][0], cx], [left[1][1], cy], color="#B9B3A4", lw=1.1, zorder=1)
    ax.plot([right[1][0], cx], [right[1][1], cy], color="#B9B3A4", lw=1.1, zorder=1)
    for grp in (left, right):
        for (x, y) in grp:
            ax.add_patch(Circle((x, y), 0.085, fc="#E7E2D6", ec="#8A8574", lw=0.8, zorder=2))
    ax.add_patch(Circle((cx, cy), 0.13, fc=ORANGE, ec=INK, lw=1.0, zorder=3))


fig, ax = plt.subplots(figsize=(12.8, 4.5))
fig.patch.set_alpha(0)
ax.set_xlim(0, 12.8)
ax.set_ylim(0, 4.5)
ax.axis("off")

bar_x0, bar_x1, bar_y0, bar_y1 = 2.7, 10.9, 2.45, 2.95
bar_mid = (bar_x0 + bar_x1) / 2
grad = np.linspace(0, 1, 256).reshape(1, -1)
ax.imshow(grad, extent=[bar_x0, bar_x1, bar_y0, bar_y1], aspect="auto",
          cmap="RdYlBu_r", alpha=0.80, zorder=1)
ax.add_patch(Rectangle((bar_x0, bar_y0), bar_x1 - bar_x0, bar_y1 - bar_y0,
                       fill=False, ec="#6B6656", lw=1.1, zorder=2))

# title above the bar
ax.text(bar_mid, 4.15, r"Katz$-$Bonacich centrality   $b(g,\phi)$",
        fontsize=17, ha="center", fontweight="bold", color=BLUE)
# end labels, clearly above the bar
ax.text(bar_x0, 3.35, r"$\phi \to 0$", fontsize=22, ha="left", fontweight="bold", color=INK)
ax.text(bar_x1, 3.35, r"$\phi \to 1/\lambda_{\mathrm{max}}$", fontsize=22, ha="right", fontweight="bold", color=INK)

# tick marks + c values, just below the bar
for c in [0.05, 0.20, 0.40, 0.60, 0.80, 0.95]:
    xx = bar_x0 + (bar_x1 - bar_x0) * c
    ax.plot([xx, xx], [bar_y0, bar_y1], color="#3A3730", lw=1.0, zorder=4)
    ax.text(xx, bar_y0 - 0.14, f"{c:g}", fontsize=9.5, ha="center", va="top", color=GRAY)

# short two-line meanings, below the ticks, hugging each end
ax.text(bar_x0, 1.75, "popularity", fontsize=13, ha="left", fontweight="bold", color=INK)
ax.text(bar_x0, 1.42, "only direct friends count", fontsize=11.5, ha="left", va="center", color=GRAY)
ax.text(bar_x1, 1.75, "reach", fontsize=13, ha="right", fontweight="bold", color=INK)
ax.text(bar_x1, 1.42, "long, indirect paths count", fontsize=11.5, ha="right", va="center", color=GRAY)

ax.text(bar_mid, 0.78, r"we compute $b(g,\phi)$ at 6 values:  $\phi = c \times (1/\lambda_{\mathrm{max}})$",
        fontsize=11.5, ha="center", va="center", color=GRAY, style="italic")

# node glyphs, well outside the bar
_hub(ax, 1.15, 2.70)
_bridge(ax, 11.75, 2.70)

fig.savefig(ASSETS / "phi_dial.png", dpi=300, bbox_inches="tight",
            pad_inches=0.12, transparent=True)
plt.close(fig)
print("  wrote phi_dial.png")


# --------------------------------------------------------- timeline / snapshots
fig, ax = plt.subplots(figsize=(11.6, 2.7))
fig.patch.set_alpha(0)
ax.set_xlim(0, 11.6)
ax.set_ylim(0, 2.7)
ax.axis("off")

ax.add_patch(FancyArrowPatch((0.4, 1.0), (10.9, 1.0), arrowstyle="-|>",
                             mutation_scale=18, lw=1.6, color="#6B6656"))
xs = np.linspace(1.0, 9.6, 10)
for x in xs:
    ax.plot([x, x], [0.86, 1.14], color="#A7A192", lw=1.1)
ax.text(11.0, 1.0, "time", fontsize=11, va="center", color=GRAY, style="italic")

xt, xt1 = xs[4], xs[5]
ax.scatter([xt], [1.0], s=150, color=BLUE, ec=INK, lw=1.0, zorder=5)
ax.scatter([xt1], [1.0], s=150, color=ORANGE, ec=INK, lw=1.0, zorder=5)
ax.text(xt, 1.62, "measure\nnetwork position", fontsize=12, ha="center",
        color=BLUE, fontweight="bold", linespacing=1.25)
ax.text(xt1, 0.42, "observe\nnext-term GPA", fontsize=12, ha="center", va="top",
        color=ORANGE, fontweight="bold", linespacing=1.25)
ax.add_patch(FancyArrowPatch((xt + 0.06, 1.30), (xt1 - 0.06, 1.30),
                             arrowstyle="-|>", mutation_scale=15, lw=1.8, color=INK,
                             connectionstyle="arc3,rad=-0.45"))
ax.text((xt + xt1) / 2, 2.35, "2–14 snapshots per group   ·   38 in total",
        fontsize=12, ha="center", color=GRAY, style="italic")

fig.savefig(ASSETS / "timeline_snapshots.png", dpi=300, bbox_inches="tight",
            pad_inches=0.12, transparent=True)
plt.close(fig)
print("  wrote timeline_snapshots.png")

print("done.")
