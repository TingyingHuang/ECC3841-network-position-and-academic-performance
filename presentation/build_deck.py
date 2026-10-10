"""Builds P3/ECC3841 Presentation 3.pptx.

Story: P1 asked whether network position predicts grades; P2 found it barely does.
P3 asks what a school can still use its friendship network for, with one course model
per use, each told the way the lectures apply a model: players, actions and payoffs,
equilibrium, a small worked example, the model mapped onto our data, the result, and
what it means in practice.

Every number on the slides is read from output/friendship_gpa/ (scripts 01-09), except
the Lecture 7 benchmarks, which are quoted from the lecture slides.
Run from anywhere: python3 presentation/build_deck.py
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from p3_helpers import *  # noqa: E402,F401,F403
from p3_results import L7_DEGREE_SD, L7_FRIENDS, L7_KATZ_SD, load_results, pct, pval  # noqa: E402


R = load_results()


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

# ================================================================ 1 where we are
s = new_slide(); header(s, "Where we are", "From question, to evidence, to use")
for i, (kick, t, d, col) in enumerate([
        ("PRESENTATION 1 · QUESTION", "Does network position predict grades, beyond direct friends?",
         "Model: the peer-effort game. Students study harder when friends do, so effort follows Katz-Bonacich centrality.\n\nPrediction: Katz matters; counting friends adds nothing.", GREY),
        ("PRESENTATION 2 · EVIDENCE", "The prediction did not hold",
         f"Own past GPA predicts later GPA (β = {R['own_gpa']:.3f}); contacts' GPA does not ({pval(R['contact_p'])}).\n\n"
         f"Katz beyond direct links: {R['katz_full'].coef:+.3f}, {pval(R['katz_full'].pval)}.", GREEN),
        ("PRESENTATION 3 · TODAY", "So what can a school use the network for?",
         "One course model per use:\n1. Flag students who need support?\n   (effort game & Katz)\n2. Organise study groups?\n   (network formation)\n3. Spread a study habit?\n   (threshold contagion)", ORANGE)]):
    x = 0.8 + i * 4.1
    box(s, x, 1.85, 3.8, 4.35, WHITE, LINE, adj=0.07)
    text(s, x + 0.25, 2.0, 3.3, 0.3, kick, 9.5, col, True)
    text(s, x + 0.25, 2.35, 3.3, 1.0, t, 15.5, DARK, True, HEAD)
    text(s, x + 0.25, 3.4, 3.3, 2.7, d, 12, DARK)
callout(s, 6.35, "", "Each model: the incentive, a small example, how it maps onto our data, the result, and what a school should do.", 0.7, size=13.5)
pagenum(s, 1)

# ================================================================ 2 confirmed (replication)
c = R["cohorts"]
s = new_slide(); header(s, "Replication of Smirnov & Thurner (2017), plus our extension", "Before the models: what we confirmed")
panel(s, 0.8, 1.8, 5.2, 3.75, "REPLICATED: SAME TESTS AS THE ORIGINAL PAPER", GREY)
stat(s, 1.05, 2.25, 2.3, 1.45, "Own past GPA", f"{R['own_gpa']:.3f}", "predicts later GPA", GREEN, 26)
stat(s, 3.5, 2.25, 2.3, 1.45, "Contacts' past GPA", pval(R["contact_p"]), "no effect on later GPA", GREY, 24)
stat(s, 1.05, 3.85, 4.75, 1.45, "New vs broken ties, university", f"{R['uni']['diff']:+.3f}",
     f"GPA gap of new ties is smaller, {pval(R['uni'].p_value)}, {int(R['uni'].n_new_ties + R['uni'].n_dropped_ties):,} ties", GREEN, 26)
panel(s, 6.2, 1.8, 6.35, 3.75, "OUR EXTENSION: HOW MUCH CLOSER NEW TIES ARE, BY YEAR", GREEN)
bars(s, 6.45, 2.3, 4.7, [(lab, -c.loc[g, "diff"], GREEN if c.loc[g, "p_value"] < 0.05 else GREY, f"{-c.loc[g, 'diff']:.3f}")
                         for g, lab in [("freshmen", "Freshmen"), ("sophomores", "Sophomores"),
                                        ("juniors", "Juniors"), ("seniors", "Seniors")]],
     0.13, row_h=0.62, label_w=1.6, fs=12.5)
for i, g in enumerate(["freshmen", "sophomores", "juniors", "seniors"]):
    text(s, 11.25, 2.3 + i * 0.62, 1.2, 0.52, pval(c.loc[g, "p_value"]), 11, GREY, anchor=MSO_ANCHOR.MIDDLE)
text(s, 6.45, 4.85, 5.9, 0.6, f"Freshmen sort {R['ratio_lo']} to {R['ratio_hi']} times more than older students, while friendships are still forming.",
     11.5, DARK, True)
callout(s, 5.8, "", "Students choose friends like themselves; friends don't change each other's grades. We take this as given and ask what the network is still good for.", 0.95, size=13.5)
pagenum(s, 2)

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
pagenum(s, 3)

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
stat(s, 0.8, 5.25, 2.85, 1.15, "Katz vs out-degree", f"r = {R['corr_katz_out']:.2f}", "almost the same measure", ORANGE, 20)
stat(s, 3.8, 5.25, 2.85, 1.15, "Out-degree, with Katz", pval(R["out_full"].pval), "loses significance too", GREY, 20)
stat(s, 6.8, 5.25, 2.85, 1.15, "All three together", pval(R["joint_p"]), "position as a whole", GREEN, 20)
stat(s, 9.8, 5.25, 2.75, 1.15, "Any φ tested", f"p ≥ {R['phi_min_p']:.2f}", "Katz beyond degree", GREY, 20)
text(s, 0.8, 6.5, 11.7, 0.5, f"Why: students name few friends (median {R['median_out'][0]:.0f} in the high school), so the friends-of-friends terms are tiny. "
     f"Lecture 7's US students named about {L7_FRIENDS} each, leaving room for Katz to differ.", 11, DARK, italic=True, align=PP_ALIGN.CENTER)
pagenum(s, 4)

# ================================================================ 5 use 1
io, ii = R["iso_out"], R["iso_in"]
s = new_slide(); header(s, "Use 1 · flag students who need support?", "No: the network adds almost nothing to past grades")
panel(s, 0.8, 1.8, 5.6, 3.6, "SIZE, IN LECTURE 7'S UNITS (SHARE OF A GPA S.D.)", ORANGE)
stat(s, 1.05, 2.2, 5.1, 1.15, "Own past GPA, per s.d.", pct(R["sd_own"]), "of a s.d. of next term's GPA", GREEN, 22)
stat(s, 1.05, 3.45, 2.5, 1.15, "Katz, per s.d.", f"{100 * R['sd_katz']:.1f}%", f"Lecture 7: {L7_KATZ_SD}", ORANGE, 22)
stat(s, 3.65, 3.45, 2.5, 1.15, "Friend count, per s.d.", f"{100 * R['sd_out']:.1f}%", f"Lecture 7: {L7_DEGREE_SD}", ORANGE, 22)
text(s, 1.05, 4.7, 5.1, 0.7, f"Same model, same units: our Katz effect is about {round(7 / (100 * R['sd_katz']))} times smaller than the lecture's, and no bigger than friend count.", 11.5, DARK)
panel(s, 6.6, 1.8, 5.95, 3.6, "NEW CHECK: STUDENTS WITH NO TIES (ALL 655 STUDENTS)", GREEN)
text(s, 6.85, 2.2, 5.5, 0.3, "Same GPA this term → GPA next term", 10.5, GREY)
stat(s, 6.85, 2.5, 2.65, 1.3, "Name no one", f"{pct(io.share_of_student_terms)} of terms", f"no difference, {pval(io.pval)}", GREY, 20)
stat(s, 9.65, 2.5, 2.65, 1.3, "Named by no one", f"{pct(ii.share_of_student_terms)} of terms",
     f"GPA falls: {pct(ii.fell_share_if_1)} vs {pct(ii.fell_share_if_0)}, {pval(ii.pval)}", ORANGE, 20)
text(s, 6.85, 3.95, 5.5, 1.3, f"Flagging everyone named by no one would cover {pct(ii.share_of_student_terms)} of students "
     f"and catch {pct(ii.share_of_all_falls_flagged)} of all GPA falls: barely better than picking at random.", 12, DARK, True)
callout(s, 5.65, "", "A school should flag students for support by their past grades, not by their place in the friendship network.", 0.85, size=14)
text(s, 0.8, 6.6, 11.7, 0.4, "P2's model drops students with no contacts (contacts' GPA is undefined); this check keeps them. A GPA fall means more than 0.1 points.",
     10, GREY, italic=True, align=PP_ALIGN.CENTER)
pagenum(s, 5)

# ================================================================ 6 model 2: the game
s = new_slide(); header(s, "Model 2 · network formation (Topic 2, Topic 8)", "Friendships last when both sides gain")
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
pagenum(s, 6)

# ================================================================ 7 model 2: data and use 2
s = new_slide(); header(s, "Model 2 · model to data, and Use 2", "Study groups have to be designed, and early")
mapping(s, 1.65, [("A tie exists only where b(gap) ≥ c for both", "Compare GPA gaps of ties formed vs ties broken between snapshots"),
                  ("Prediction: new ties have smaller gaps", f"Confirmed in every cohort; freshmen {R['ratio_lo']}–{R['ratio_hi']}× older years (slide 2)")], h=0.5)
panel(s, 0.8, 3.25, 11.75, 2.45, "USE 2 · ORGANISE STUDY GROUPS?", GREEN)
for i, (t, d) in enumerate([
        ("Mixing won't happen by itself", "Students keep re-sorting by grades, so mixed-ability contact has to be built into the program."),
        ("Do it in first year", "That is when sorting is strongest and friendships are still forming."),
        ("Course evidence that it works", "Lecture 7, Bangladesh RCT: study groups raised low-ability girls' scores; friendship groups worked best. Advice: let students group by friendship, with a constraint on each group's average score.")]):
    x = 1.05 + i * 3.85
    text(s, x, 3.65, 3.6, 0.4, t, 13.5, DARK, True, HEAD)
    text(s, x, 4.1, 3.6, 1.5, d, 11.5, DARK)
callout(s, 5.95, "", "Use the network to form groups (friends together, mixed in ability), not to wait for mixing to happen.", 0.85, size=14)
pagenum(s, 7)

# ================================================================ 8 model 3: the game
s = new_slide(); header(s, "Model 3 · threshold contagion (Lecture 3, Topic 8)", "A habit spreads only when enough friends have it")
panel(s, 0.8, 1.8, 6.6, 4.1, "THE GAME")
text(s, 1.05, 2.2, 6.1, 0.5, "Players: students.  Action: adopt a study habit (1) or not (0).", 12, DARK)
text(s, 1.05, 2.65, 6.1, 0.5, "adopt  ⇔  b × (friends who adopted) ≥ c  ⇔  at least r = c/b", 14.5, DARK, True, HEAD, align=PP_ALIGN.CENTER)
text(s, 1.05, 3.2, 6.1, 0.7, "c: cost of the habit; b: benefit per friend who uses it (shared notes, a study partner). Harder habit → larger r.", 11, GREY)
text(s, 1.05, 3.95, 6.1, 0.3, "EQUILIBRIUM (Lecture 3 majority game)", 10, ORANGE, True)
text(s, 1.05, 4.25, 6.1, 1.6, "A coordination game with many equilibria: 'nobody adopts' is one. Starting students (seeds) can tip the network into another.\n"
     "We count friends, not a share, as in Lecture 1's threshold simulation (thresholds 1 to 5).", 12, DARK)
panel(s, 7.6, 1.8, 4.95, 4.1, "A SMALL EXAMPLE: r = 2", GREEN)
toy = {"A": (8.3, 2.7, "A", ORANGE), "B": (8.3, 4.1, "B", ORANGE), "C": (9.6, 3.4, "C", GREEN),
       "D": (10.9, 2.7, "D", GREEN), "E": (12.0, 3.6, "E", GREY), "F": (10.9, 4.8, "F", GREY)}
network(s, toy, [("A", "C"), ("B", "C"), ("A", "D"), ("C", "D"), ("D", "E")], r=0.27, size=12)
text(s, 7.85, 5.05, 4.5, 0.8, "Seeds A, B → C adopts (2 friends) → D adopts (A, C).\nE has 1 adopting friend: never. F has none: never.", 10.5, DARK, align=PP_ALIGN.CENTER)
callout(s, 6.1, "", "Who starts, how hard the habit is, and who has no friends at all decide how far it spreads.", 0.8, size=14)
pagenum(s, 8)

# ================================================================ 9 model 3: data
s = new_slide(); header(s, "Model 3 · model to data", "Simulated on the real networks")
mapping(s, 1.65, [("Network g", f"Who likes whom: high school ({R['n_nodes'][0]:,} students), freshmen ({R['n_nodes'][1]:,})"),
                  ("A student counts friends who adopted", "Counts the classmates they named (outgoing ties)"),
                  ("Seeds", "3% or 8% of students: the most active (out-degree), highest Katz, or random"),
                  ("Threshold r", "r = 1 to 5; 300 simulations per setting")], h=0.45)
text(s, 0.8, 4.1, 11.7, 0.3, "A WARNING FROM THE DATA: MANY STUDENTS NAME FEW OR NO FRIENDS", 10.5, ORANGE, True)
stat(s, 0.8, 4.45, 3.7, 1.6, "High school", pct(R["never_school_r1"]), "name no one in the simulated snapshot: unreachable", ORANGE, 30)
stat(s, 4.75, 4.45, 3.7, 1.6, "Typical student", f"{R['median_out'][0]:.0f} / {R['median_out'][1]:.0f}", "friends named: high school / freshmen", DARK, 30)
stat(s, 8.7, 4.45, 3.85, 1.6, "If r = 4", f"{pct(R['never_r4'][0])} / {pct(R['never_r4'][1])}", "can never adopt via friends (school / freshmen)", ORANGE, 30)
pagenum(s, 9)

# ================================================================ 10 model 3: result
s = new_slide(); header(s, "Model 3 · result", "Who starts matters only for habits of middle difficulty")
legend(s, 0.8, 1.72, [("Highest Katz", ORANGE), ("Most active", GREEN), ("Random", GREY)])
for x, g, title in [(0.8, "school", f"High school (N = {R['n_nodes'][0]:,})"), (7.0, "freshmen", f"Freshmen (N = {R['n_nodes'][1]:,})")]:
    line_chart(s, x, 2.15, 5.5, 4.1, [("Katz", R["curve"](g, "top_katz"), ORANGE), ("Active", R["curve"](g, "top_out_degree"), GREEN),
                                      ("Random", R["curve"](g, "random"), GREY)],
               [1, 2, 3, 4, 5], title=title, xlab="r = friends needed before a student adopts")
text(s, 0.8, 6.35, 11.7, 0.5, "Share of students who end up adopting (%), starting with 3% of students, 300 simulations per point. Easy habit (r = 1): spreads anyway. Hard habit (r ≥ 4): barely spreads.",
     10, GREY, italic=True, align=PP_ALIGN.CENTER)
pagenum(s, 10)

# ================================================================ 11 use 3
h3, h8 = R["hc"]("freshmen", 0.03, 3), R["hc"]("freshmen", 0.08, 3)
s = new_slide(); header(s, "Use 3 · spread a study habit?", "Yes, if you start with the right students")
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
pagenum(s, 11)

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
pagenum(s, 12)

# ================================================================ 13 answer
s = new_slide(); header(s, "Answering our P1 question", "Grades shape the network more than the network shapes grades", two_line=True)
cards3(s, 2.3, 3.3, [
    ("Does position predict grades?", f"Barely: about {100 * R['sd_katz']:.1f}% of a GPA s.d., and in this sparse network Katz reach can't be told apart from friend count.", ORANGE),
    ("Why not?", "Students choose friends with similar grades, most of all in first year. The network reflects grades; it doesn't drive them.", GREEN),
    ("What is the network for?", "Organising study groups a school designs, and spreading habits of middle difficulty through active students.", ORANGE)],
    size=13)
callout(s, 5.85, "", "Course question: network structure explains why friends' grades look alike (selection) and decides who adopts a new habit (thresholds).", 0.9, size=13.5)
pagenum(s, 13)

# ================================================================ 14 limitations
s = new_slide(); header(s, "Limitations", "What we cannot claim")
for i, (t, d) in enumerate([
        ("Prediction, not cause", "Students who name more friends may also be more motivated. We show what predicts grades, not what causes them."),
        ("Katz vs friend count", f"They are highly correlated here (r = {R['corr_katz_out']:.2f}), so our network cannot separate them."),
        ("Cohorts, not the same students", "The first-year pattern compares different cohorts; one cohort followed for four years would be cleaner."),
        ("Simulation is a sketch", "Equal thresholds, one snapshot, and the best starting rule depends on how many starters there are.")]):
    y = 1.9 + i * 1.18
    box(s, 0.8, y, 11.75, 1.0, WHITE, LINE, adj=0.14)
    text(s, 1.1, y + 0.1, 3.5, 0.8, t, 13.5, ORANGE, True, HEAD, anchor=MSO_ANCHOR.MIDDLE)
    text(s, 4.8, y, 7.55, 1.0, d, 12, DARK, anchor=MSO_ANCHOR.MIDDLE)
pagenum(s, 14)

# ================================================================ thank you + contributions
s = new_slide()
text(s, 0.8, 1.0, 11.7, 0.9, "Thank you", 36, DARK, True, HEAD, align=PP_ALIGN.CENTER)
text(s, 0.8, 2.05, 11.7, 0.4, "TEAM CONTRIBUTIONS", 12, ORANGE, True, align=PP_ALIGN.CENTER)
for i, name in enumerate(["Amy Bing", "Tingying Huang"]):
    x = 0.8 + i * 6.0
    box(s, x, 2.6, 5.75, 3.6, WHITE, LINE, adj=0.07)
    text(s, x + 0.3, 2.8, 5.15, 0.5, name, 18, DARK, True, HEAD)
    text(s, x + 0.3, 3.45, 5.15, 2.6, "• [contribution]\n• [contribution]\n• [contribution]", 13, GREY)

out = P3 / "ECC3841 Presentation 3.pptx"
prs.save(out)
print(out)
