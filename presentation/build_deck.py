"""Builds P3/ECC3841 Presentation 3.pptx.

Built on Amy's Canva revision of the deck (P3/old.pptx.pdf): her slide titles, recap,
literature, conclusion and references are kept; content is corrected to the final logic chain.

Story: P1 asked whether network position predicts grades; P2 found it barely does.
P3 asks what a school can still use its friendship network for, with one course model
per use, each told the way the lectures apply a model: players, actions and payoffs,
equilibrium, a small worked example, the model mapped onto our data, the result, and
what it means in practice.

Every number on the slides is read from output/friendship_gpa/ (scripts 01-09), except
the Lecture 7 benchmarks, which are quoted from the lecture slides.
Run from anywhere: python3 presentation/build_deck.py
"""
import os
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from p3_helpers import *  # noqa: E402,F401,F403
from p3_results import L7_DEGREE_SD, L7_FRIENDS, L7_KATZ_SD, load_results, pct, pval  # noqa: E402


R = load_results()
PAGE = iter(range(1, 100))


def cards3(s, y, h, items, title_h=0.85, size=12):
    for i, (t, d, col) in enumerate(items):
        x = 0.8 + i * 4.1
        box(s, x, y, 3.8, h, WHITE, LINE, adj=0.09)
        text(s, x + 0.25, y + 0.2, 3.3, title_h, t, 15, col, True, HEAD)
        text(s, x + 0.25, y + 0.25 + title_h, 3.3, h - title_h - 0.4, d, size, DARK)


def panel(s, x, y, w, h, kicker, col=ORANGE):
    box(s, x, y, w, h, WHITE, LINE, adj=0.05)
    text(s, x + 0.25, y + 0.12, w - 0.5, 0.3, kicker, 10.5, col, True)


def mapping(s, y, rows, h=0.5):
    """Theory -> our data, one row per pair, the way Lecture 7 sets theory beside its empirical counterpart."""
    text(s, 0.8, y, 5.5, 0.3, "IN THE MODEL", 10, GREY, True)
    text(s, 6.95, y, 5.6, 0.3, "IN OUR DATA", 10, GREEN, True)
    for i, (a, b) in enumerate(rows):
        yy = y + 0.32 + i * (h + 0.08)
        box(s, 0.8, yy, 5.7, h, WHITE, LINE, adj=0.15)
        text(s, 0.95, yy, 5.4, h, a, 11.5, DARK, anchor=MSO_ANCHOR.MIDDLE)
        text(s, 6.5, yy, 0.45, h, "→", 16, ORANGE, True, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
        box(s, 6.95, yy, 5.6, h, SAND, LINE, adj=0.15)
        text(s, 7.1, yy, 5.3, h, b, 11.5, DARK, anchor=MSO_ANCHOR.MIDDLE)


# ================================================================ title
s = new_slide()
text(s, 0.9, 1.0, 9, 0.3, "ECC3841 NETWORK ECONOMICS  ·  PRESENTATION 3", 11, ORANGE, True)
box(s, 0.62, 1.6, 0.17, 1.9, ORANGE, None, MSO_SHAPE.RECTANGLE)
text(s, 1.0, 1.47, 7.4, 2.3, "Network Position and\nAcademic Performance", 36, DARK, True, HEAD, spacing=1.05)
text(s, 0.9, 3.95, 7.0, 1.1, "What can a school use its students' friendship network for?", 16, DARK, True, BODY, italic=True)
text(s, 0.9, 5.65, 4, 1.0, "Group members:\nAmy Bing\nTingying Huang", 13, DARK)
art = {i: (x, y, "", c) for i, (x, y, c) in enumerate([
    (9.2, 1.4, GREY), (10.4, 1.1, GREEN), (11.7, 1.6, GREEN), (9.6, 2.6, ORANGE), (10.9, 2.4, GREEN),
    (12.2, 2.8, GREY), (9.1, 3.9, GREEN), (10.3, 3.6, ORANGE), (11.6, 3.9, GREEN), (12.4, 4.6, GREY),
    (9.7, 5.0, GREY), (11.0, 5.1, GREEN)])}
network(s, art, [(0, 1), (1, 2), (0, 3), (1, 4), (3, 4), (4, 2), (2, 5), (3, 6), (3, 7), (4, 7), (7, 8),
                 (5, 8), (8, 9), (6, 10), (7, 10), (7, 11), (8, 11), (10, 11)], r=0.22)
pagenum(s, "")

# ================================================================ recap (Amy's slide, P2's own numbers)
s = new_slide(); header(s, "Where we left off", "Recap of presentation 2")
stat(s, 0.8, 1.9, 2.75, 1.9, "Baseline", f"{R['own_gpa']:.3f}", "own past GPA, p < 0.001", GREEN, 30)
stat(s, 3.7, 1.9, 2.75, 1.9, "Contacts' past GPA", pval(R["contact_p"]), "no effect on later GPA", GREY, 26)
stat(s, 6.6, 1.9, 2.75, 1.9, "Pooled Katz", f"{R['pooled_katz']:+.3f}", f"→ {R['pooled_katz_ctrl']:+.3f} once direct links counted", ORANGE, 30)
stat(s, 9.5, 1.9, 3.05, 1.9, "School panel, Katz", f"{R['katz_full'].coef:+.3f}", f"beyond direct links, {pval(R['katz_full'].pval)}", ORANGE, 30)
callout(s, 4.1, "", "P1's prediction, that Katz reach matters beyond direct friends, did not hold.", 0.9, size=14.5)
text(s, 0.8, 5.35, 11.7, 0.7, "So today's question: if position barely predicts grades, what can a school still use its students' friendship network for?",
     14, GREY, italic=True, align=PP_ALIGN.CENTER)
pagenum(s, next(PAGE))

# ================================================================ plan (Amy's 'different models' slide, now three)
s = new_slide(); header(s, "Today", "Three course models, three possible uses", two_line=False)
cards3(s, 1.95, 3.85, [
    ("Model 1 · Effort game & Katz", "Lectures 1, 3, 7.\n\nUse 1: can the network flag students who need support?", ORANGE),
    ("Model 2 · Network formation", "Pairwise stability (Topic 2), homophily and Schelling (Topic 8).\n\nUse 2: how should a school organise study groups?", GREEN),
    ("Model 3 · Threshold contagion", "Majority game (Lecture 3), complex contagion (Topic 8).\n\nUse 3: who should start a study-habit campaign?", ORANGE)],
    title_h=0.6, size=12.5)
callout(s, 6.05, "", "Each model: the incentive, a small example, how it maps onto our data, the result, and what a school should do.", 0.8, size=13.5)
pagenum(s, next(PAGE))

# ================================================================ 3 model 1: the game
s = new_slide(); header(s, "Model 1 · effort game and Katz (Lectures 1, 3, 7)", "Why reach should matter, in theory")
panel(s, 0.8, 1.8, 6.6, 4.1, "THE GAME")
text(s, 1.05, 2.2, 6.1, 0.5, "Players: students.  Action: study effort x_i.  Network: g_ij = 1 if i likes j.", 12, DARK)
text(s, 1.05, 2.65, 6.1, 0.5, "u_i = a·x_i  −  ½x_i²  +  φ Σ_j g_ij x_i x_j", 17, DARK, True, HEAD, align=PP_ALIGN.CENTER)
text(s, 1.05, 3.2, 6.1, 0.9, "a·x_i: benefit from own effort   ·   ½x_i²: cost of effort\nφ Σ g_ij x_i x_j: extra benefit when friends also study (complements)", 11, GREY)
text(s, 1.05, 4.05, 6.1, 0.3, "EQUILIBRIUM (Lecture 3, Ballester et al. 2006)", 10, ORANGE, True)
text(s, 1.05, 4.35, 6.1, 0.45, "x* = a (I − φG)⁻¹ 1  =  a × Katz-Bonacich centrality", 14, DARK, True, HEAD)
text(s, 1.05, 4.85, 6.1, 0.9, "Katz = 1 + φ·(friends named) + φ²·(their friends) + …\nIts first term is just a friend count; it differs only through friends of friends.", 12, DARK)
panel(s, 7.6, 1.8, 4.95, 4.1, "A SMALL EXAMPLE (φ = 0.3)", GREEN)
G = np.zeros((10, 10))
for a, b in [(0, 1), (0, 2), (1, 3), (1, 4), (2, 5), (2, 6), (7, 8), (7, 9)]:
    G[a, b] = 1
katz = np.linalg.solve(np.eye(10) - 0.3 * G, np.ones(10))
toy = {0: (8.4, 3.05, "A", ORANGE), 1: (9.4, 2.55, "", GREEN), 2: (9.4, 3.55, "", GREEN),
       3: (10.3, 2.3, "", GREY), 4: (10.3, 2.8, "", GREY), 5: (10.3, 3.3, "", GREY), 6: (10.3, 3.8, "", GREY),
       7: (8.4, 4.75, "B", ORANGE), 8: (9.4, 4.4, "", GREEN), 9: (9.4, 5.1, "", GREEN)}
network(s, toy, [(0, 1), (0, 2), (1, 3), (1, 4), (2, 5), (2, 6), (7, 8), (7, 9)], r=0.17)
text(s, 10.75, 2.75, 1.75, 0.7, f"Katz A\n= {katz[0]:.2f}", 13, ORANGE, True, HEAD)
text(s, 10.75, 4.4, 1.75, 0.7, f"Katz B\n= {katz[7]:.2f}", 13, ORANGE, True, HEAD)
text(s, 7.85, 5.35, 4.5, 0.5, "Both name 2 friends. A's friends name others, B's don't.", 11, GREY, italic=True)
callout(s, 6.1, "", "P1's prediction: reach beyond direct friends (the φ² terms and beyond) raises effort, so it should raise grades.", 0.8, size=13.5)
pagenum(s, next(PAGE))

# ================================================================ 4 model 1: our data and result
s = new_slide(); header(s, "Model 1 · model to data", "In our network, Katz and friend count are the same thing")
mapping(s, 1.65, [("Effort x_i follows Katz-Bonacich centrality", "GPA next term on Katz, in- and out-degree, own and contacts' GPA this term"),
                  ("Prediction: Katz matters beyond direct links", "Katz significant, degrees not  (φ = 0.85 / λmax, set in P1)")], h=0.48)
forest(s, 0.8, 3.25, 11.75, [
    ("Katz alone", R["katz_only"].coef, R["katz_only"].ci_low, R["katz_only"].ci_high, pval(R["katz_only"].pval), GREEN),
    ("Out-degree alone (names others)", R["out_only"].coef, R["out_only"].ci_low, R["out_only"].ci_high, pval(R["out_only"].pval), GREEN),
    ("In-degree alone (named by others)", R["in_only"].coef, R["in_only"].ci_low, R["in_only"].ci_high, pval(R["in_only"].pval), GREY),
    ("Katz, with in- and out-degree (P2)", R["katz_full"].coef, R["katz_full"].ci_low, R["katz_full"].ci_high, pval(R["katz_full"].pval), ORANGE)],
    -0.01, 0.03, 0.01, row_h=0.42, label_w=4.0, note_w=1.5, cap=False, fs=12)
stat(s, 0.8, 5.25, 5.75, 1.15, "Katz vs out-degree", f"r = {R['corr_katz_out']:.2f}", "almost the same measure in our network", ORANGE, 20)
stat(s, 6.8, 5.25, 5.75, 1.15, "Katz and out-degree together", "neither significant",
     f"Katz {pval(R['katz_full'].pval)}, out-degree {pval(R['out_full'].pval)}", GREY, 20)
text(s, 0.8, 6.5, 11.7, 0.5, f"Why: students name few friends (median {R['median_out'][0]:.0f} in the high school), so the friends-of-friends terms are tiny. "
     f"Lecture 7's US students named about {L7_FRIENDS} each, leaving room for Katz to differ.", 11, DARK, italic=True, align=PP_ALIGN.CENTER)
pagenum(s, next(PAGE))

# ================================================================ 5 use 1
ii = R["iso_in"]
s = new_slide(); header(s, "Use 1 · flag students who need support?", "No: the network adds almost nothing to past grades")
panel(s, 0.8, 1.8, 5.6, 3.6, "SIZE, IN LECTURE 7'S UNITS (SHARE OF A GPA S.D.)", ORANGE)
stat(s, 1.05, 2.25, 2.5, 1.5, "Katz, our data", f"{100 * R['sd_katz']:.1f}%", "per s.d. of Katz", ORANGE, 30)
stat(s, 3.65, 2.25, 2.5, 1.5, "Katz, Lecture 7", L7_KATZ_SD, "US schools (AddHealth)", GREY, 30)
text(s, 1.05, 4.0, 5.1, 1.2, f"Same model, same units: our effect is about {round(7 / (100 * R['sd_katz']))} times smaller.", 13, DARK, True)
panel(s, 6.6, 1.8, 5.95, 3.6, "NEW CHECK: STUDENTS P2'S MODEL LEFT OUT", GREEN)
stat(s, 6.85, 2.25, 2.65, 1.5, "Flag 'named by no one'", f"{pct(ii.share_of_student_terms)}", "of students would be flagged", ORANGE, 30)
stat(s, 9.65, 2.25, 2.65, 1.5, "It would catch", f"{pct(ii.share_of_all_falls_flagged)}", "of all GPA falls", ORANGE, 30)
text(s, 6.85, 4.0, 5.5, 1.2, "Barely better than picking students at random.", 13, DARK, True)
callout(s, 5.65, "", "A school should flag students for support by their past grades, not by their place in the friendship network.", 0.85, size=14)
text(s, 0.8, 6.6, 11.7, 0.4, "A GPA fall means a drop of more than 0.1 points from one term to the next.",
     10, GREY, italic=True, align=PP_ALIGN.CENTER)
pagenum(s, next(PAGE))

# ================================================================ 6 model 2: the game
s = new_slide(); header(s, "Model 2 · network formation (Topic 2, Topic 8)", "A simple incentive to link with similar peers")
panel(s, 0.8, 1.8, 6.6, 4.1, "THE GAME")
text(s, 1.05, 2.2, 6.1, 0.5, "Players: students.  Action: which friendships to keep.  Type: GPA.", 12, DARK)
text(s, 1.05, 2.65, 6.1, 0.5, "u_i(g) = Σ_{j: ij ∈ g} [ b(|GPA_i − GPA_j|) − c ]", 16, DARK, True, HEAD, align=PP_ALIGN.CENTER)
text(s, 1.05, 3.2, 6.1, 0.7, "b falls as the GPA gap grows (same pace, easier to help each other); c is the time a friendship takes.", 11, GREY)
text(s, 1.05, 3.95, 6.1, 0.3, "PAIRWISE STABILITY (Topic 2)", 10, ORANGE, True)
text(s, 1.05, 4.25, 6.1, 1.5, "No one gains by dropping a friend, and no two students both gain by adding one.\n"
     "So a tie exists only where b(gap) ≥ c for both.\n\nSchelling (Topic 8): even a weak preference, repeated, sorts a whole network.", 12, DARK)
panel(s, 7.6, 1.8, 4.95, 4.1, "A SMALL EXAMPLE: b(gap) = 1 − gap, c = 0.5", GREEN)
toy = {0: (8.6, 2.95, "3.9", GREEN), 1: (11.4, 2.95, "3.8", GREEN), 2: (8.6, 4.55, "3.0", GREY), 3: (11.4, 4.55, "2.9", GREY)}
network(s, toy, [(0, 1, GREEN), (2, 3, GREEN), (1, 2, NODE, True), (0, 3, NODE, True), (0, 2, NODE, True), (1, 3, NODE, True)], r=0.32, size=12)
text(s, 7.85, 2.25, 4.5, 0.35, "Same-level pairs: gap 0.1, b = 0.9 ≥ 0.5, kept", 10.5, GREEN, True, align=PP_ALIGN.CENTER)
text(s, 7.85, 5.05, 4.5, 0.8, "Dashed: gap 0.8–1.0, b ≤ 0.2 < 0.5, dropped.\nStable network: two same-level pairs.", 11, GREY, italic=True, align=PP_ALIGN.CENTER)
callout(s, 6.1, "", "Prediction: ties that form should join closer-GPA students than ties that break.", 0.8, size=14)
pagenum(s, next(PAGE))

# ================================================================ model 2: our data (replicated test + our by-year extension)
c = R["cohorts"]
hs = R["cohorts"].loc["school"]
s = new_slide(); header(s, "Model 2 · model to data", "New ties join closer-GPA students, most of all in first year")
panel(s, 0.8, 1.8, 5.2, 3.75, "SMIRNOV & THURNER'S TEST, REPLICATED", GREY)
stat(s, 1.05, 2.25, 4.75, 1.45, "New vs broken ties, university", f"{R['uni']['diff']:+.3f}",
     f"gap {R['uni'].mean_gap_new:.3f} new vs {R['uni'].mean_gap_dropped:.3f} broken, {pval(R['uni'].p_value)}, {int(R['uni'].n_new_ties + R['uni'].n_dropped_ties):,} ties", GREEN, 26)
stat(s, 1.05, 3.85, 4.75, 1.45, "Same test, high school", f"{hs['diff']:+.3f}", f"same direction, {pval(hs.p_value)} (smaller sample)", GREY, 26)
panel(s, 6.2, 1.8, 6.35, 3.75, "OUR EXTENSION: HOW MUCH CLOSER NEW TIES ARE, BY YEAR", GREEN)
bars(s, 6.45, 2.3, 4.7, [(lab, -c.loc[g, "diff"], GREEN if c.loc[g, "p_value"] < 0.05 else GREY, f"{-c.loc[g, 'diff']:.3f}")
                         for g, lab in [("freshmen", "Freshmen"), ("sophomores", "Sophomores"),
                                        ("juniors", "Juniors"), ("seniors", "Seniors")]],
     0.13, row_h=0.62, label_w=1.6, fs=12.5)
for i, g in enumerate(["freshmen", "sophomores", "juniors", "seniors"]):
    text(s, 11.25, 2.3 + i * 0.62, 1.2, 0.52, pval(c.loc[g, "p_value"]), 11, GREY, anchor=MSO_ANCHOR.MIDDLE)
text(s, 6.45, 4.85, 5.9, 0.6, f"Freshmen sort {R['ratio_lo']} to {R['ratio_hi']} times more than older students, while friendships are still forming.",
     11.5, DARK, True)
callout(s, 5.8, "", "The prediction holds: ties form and break by GPA gap, as pairwise stability says.", 0.85, size=14)
pagenum(s, next(PAGE))

# ================================================================ model 2 takeaway + use 2 (Amy's slide)
s = new_slide(); header(s, "Model 2 · takeaway, and use 2", "This is why “selection” keeps winning")
cards3(s, 2.3, 3.4, [
    ("Explains P2's baseline", "Contacts' GPA added nothing in P2 because friends are chosen for similar grades: selection, not influence.", GREEN),
    ("Explains why position adds little", "A well-connected student mostly reaches similar-GPA peers, so position mostly mirrors grades the student already has.", ORANGE),
    ("Use 2: design study groups, early", "Mixing won't happen by itself. Form mixed-ability groups in first year. Lecture 7 (Bangladesh RCT): ability-balanced groups raised scores, friendship groups most. Advice: let friends group, but cap each group's average score.", GREEN)],
    size=12)
pagenum(s, next(PAGE))

# ================================================================ 8 model 3: the game
s = new_slide(); header(s, "Model 3 · setup (Watts 2002; Lecture 3, Topic 8)", "Threshold contagion on the real network")
panel(s, 0.8, 1.8, 6.6, 4.1, "THE GAME")
text(s, 1.05, 2.2, 6.1, 0.5, "Players: students.  Action: join a study group (1) or not (0).", 12, DARK)
text(s, 1.05, 2.65, 6.1, 0.5, "adopt  ⇔  b × (friends who adopted) ≥ c  ⇔  at least r = c/b", 14.5, DARK, True, HEAD, align=PP_ALIGN.CENTER)
text(s, 1.05, 3.2, 6.1, 0.7, "c: the time the group takes; b: benefit per friend already in it (shared notes, a study partner). Harder habit → larger r.", 11, GREY)
text(s, 1.05, 3.95, 6.1, 0.3, "EQUILIBRIUM (Lecture 3 majority game)", 10, ORANGE, True)
text(s, 1.05, 4.25, 6.1, 1.6, "A coordination game with many equilibria: 'nobody joins' is one. Starting students (seeds) can tip the network into another.\n"
     f"Simulated on the real school ({R['n_nodes'][0]:,}) and freshmen ({R['n_nodes'][1]:,}) networks: seeds are 3% or 8% of students "
     "(highest Katz, most active, or random), r = 1 to 5, 300 runs each.", 12, DARK)
panel(s, 7.6, 1.8, 4.95, 4.1, "A SMALL EXAMPLE: r = 2", GREEN)
toy = {"A": (8.3, 2.7, "A", ORANGE), "B": (8.3, 4.1, "B", ORANGE), "C": (9.6, 3.4, "C", GREEN),
       "D": (10.9, 2.7, "D", GREEN), "E": (12.0, 3.6, "E", GREY), "F": (10.9, 4.8, "F", GREY)}
network(s, toy, [("A", "C"), ("B", "C"), ("A", "D"), ("C", "D"), ("D", "E")], r=0.27, size=12)
text(s, 7.85, 5.05, 4.5, 0.8, "Seeds A, B → C joins (2 friends) → D joins (A, C).\nE has 1 friend in the group: never. F has none: never.", 10.5, DARK, align=PP_ALIGN.CENTER)
callout(s, 6.1, "", f"Who starts, how hard the habit is, and who has no friends ({pct(R['never_school_r1'])} of high-schoolers name no one) decide how far it spreads.", 0.8, size=13)
pagenum(s, next(PAGE))

# ================================================================ 10 model 3: result
s = new_slide(); header(s, "Model 3 · result", "A critical window where seeding strategy matters")
legend(s, 0.8, 1.72, [("Highest Katz", ORANGE), ("Most active", GREEN), ("Random", GREY)])
for x, g, title in [(0.8, "school", f"High school (N = {R['n_nodes'][0]:,})"), (7.0, "freshmen", f"Freshmen (N = {R['n_nodes'][1]:,})")]:
    line_chart(s, x, 2.15, 5.5, 4.1, [("Katz", R["curve"](g, "top_katz"), ORANGE), ("Active", R["curve"](g, "top_out_degree"), GREEN),
                                      ("Random", R["curve"](g, "random"), GREY)],
               [1, 2, 3, 4, 5], title=title, xlab="r = friends needed before a student adopts")
text(s, 0.8, 6.35, 11.7, 0.5, "Share of students who end up adopting (%), starting with 3% of students, 300 simulations per point. Easy habit (r = 1): spreads anyway. Hard habit (r ≥ 4): barely spreads. Critical mass (Lecture 1).",
     10, GREY, italic=True, align=PP_ALIGN.CENTER)
pagenum(s, next(PAGE))

# ================================================================ 11 use 3
h3, h8 = R["hc"]("freshmen", 0.03, 3), R["hc"]("freshmen", 0.08, 3)
s = new_slide(); header(s, "Model 3 · takeaway, and use 3", "Out-degree beats Katz for seeding too")
text(s, 0.8, 1.75, 11.5, 0.3, "Share who adopt at r = 3, freshmen network", 11.5, GREY)
for x, h, kick, col in [(0.8, h3, f"FEW STARTERS · {int(h3.k_seed)} students (3%)", GREEN), (7.0, h8, f"MORE STARTERS · {int(h8.k_seed)} students (8%)", ORANGE)]:
    text(s, x, 2.15, 5.6, 0.35, kick, 10.5, col, True)
    bars(s, x, 2.55, 5.6, [("Most active", 100 * h.top_out_degree, GREEN, f"{100 * h.top_out_degree:.1f}%"),
                           ("Random", 100 * h.random, GREY, f"{100 * h.random:.1f}%"),
                           ("Highest Katz", 100 * h.top_katz, ORANGE, f"{100 * h.top_katz:.1f}%")],
         50, row_h=0.58, label_w=1.9, fs=12.5)
stat(s, 0.8, 4.45, 3.7, 1.25, "Most active vs random", f"+{h3.extra_vs_random_top_out_degree:.0f}", f"more students reached, {int(h3.k_seed)} starters", GREEN, 24)
stat(s, 4.75, 4.45, 3.7, 1.25, "Most active vs highest Katz", f"+{h3.extra_top_out_degree_vs_top_katz:.0f}", "Katz and friend count finally differ", ORANGE, 24)
stat(s, 8.7, 4.45, 3.85, 1.25, "With 8% starters", f"random {100 * h8.random:.0f}%", "top students reach the same people", GREY, 24)
callout(s, 5.95, "", "Few starters: recruit the students who name the most friends. More starters: spread them across groups. Reach students with no friends directly.", 0.95, size=13.5)
pagenum(s, next(PAGE))

# ================================================================ 12 decision
s = new_slide(); header(s, "The manager decision", "Which peer-support idea is worth testing?")
rows = [("Idea", "What the evidence says", "Verdict"),
        ("Flag students for support by network position", f"Model 1: position effects are ~{100 * R['sd_katz']:.1f}% of a GPA s.d.; a 'no one names them' flag barely beats random.", "Not worth it"),
        ("Mixed-ability study groups in first year", "Model 2: students sort by grades on their own, most in first year. Lecture 7 RCT: designed groups raised scores.", "Worth testing"),
        ("Peer-led study-habit campaign", f"Model 3: works for habits of middle difficulty; start with active students if few starters; {pct(R['never_school_r1'])} need direct outreach.", "Worth testing, with conditions")]
cols = [(0.8, 3.6), (4.5, 6.0), (10.6, 1.95)]
for r_, row in enumerate(rows):
    y = 1.8 + (0 if r_ == 0 else 0.5 + (r_ - 1) * 1.3)
    h = 0.45 if r_ == 0 else 1.15
    if r_: box(s, 0.8, y, 11.75, h, WHITE, LINE, adj=0.1)
    for c_, (x, w) in enumerate(cols):
        col = GREY if r_ == 0 else (DARK if c_ < 2 else [ORANGE, GREEN, GREEN][r_ - 1])
        text(s, x + 0.2, y, w - 0.3, h, row[c_], 10.5 if r_ == 0 else (13 if c_ != 1 else 11.5), col,
             r_ == 0 or c_ != 1, HEAD if (r_ and c_ != 1) else BODY, anchor=MSO_ANCHOR.MIDDLE)
callout(s, 6.15, "", "Use the network to organise study and spread habits through direct ties. Use grades, not position, to target support.", 0.75, size=13.5)
pagenum(s, next(PAGE))

# ================================================================ answer (Amy's 'Bringing it together')
s = new_slide(); header(s, "Bringing it together", "Answering the core question")
cards3(s, 1.95, 3.6, [
    ("What structure explains", "Why friends' grades look alike: students choose similar friends (Model 2), rather than peers raising effort (Model 1).", GREEN),
    ("What structure decides", "Who adopts a new habit: each student waits for enough adopting friends, so who starts and who is isolated matter (Model 3).", ORANGE),
    ("What we cannot claim", "Causes: these are predictions. And in this sparse network, Katz reach and friend count cannot be separated.", GREY)],
    size=13)
callout(s, 5.8, "", "Our answer to P1: position follows grades more than grades follow position.", 0.9, size=14.5)
pagenum(s, next(PAGE))

# ================================================================ thank you + contributions
s = new_slide()
text(s, 0.8, 1.0, 11.7, 0.9, "Thank you", 36, DARK, True, HEAD, align=PP_ALIGN.CENTER)
text(s, 0.8, 2.05, 11.7, 0.4, "TEAM CONTRIBUTIONS", 12, ORANGE, True, align=PP_ALIGN.CENTER)
for i, name in enumerate(["Amy Bing", "Tingying Huang"]):
    x = 0.8 + i * 6.0
    box(s, x, 2.6, 5.75, 3.6, WHITE, LINE, adj=0.07)
    text(s, x + 0.3, 2.8, 5.15, 0.5, name, 18, DARK, True, HEAD)
    text(s, x + 0.3, 3.45, 5.15, 2.6, "• [contribution]\n• [contribution]\n• [contribution]", 13, GREY)

out = Path(os.environ.get("P3_DECK_OUT", P3 / "ECC3841 Presentation 3.pptx"))
prs.save(out)
print(out)
