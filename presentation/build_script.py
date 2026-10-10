"""Builds P3/scripts.pdf, the ~15-minute speaker script for Presentation 3.

'Slide N:' headings follow the deck: Slide 1 covers the title and 'where we are' pages,
Slides 2-14 match the page numbers, Slide 15 is the thank-you page. Numbers come from the
same loader as the deck (p3_results.py).
Run from anywhere: python3 presentation/build_script.py
"""
import sys
from pathlib import Path

from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.platypus import KeepTogether, Paragraph, SimpleDocTemplate

sys.path.insert(0, str(Path(__file__).resolve().parent))
from p3_helpers import P3  # noqa: E402
from p3_results import L7_DEGREE_SD, L7_FRIENDS, L7_KATZ_SD, load_results, pct, pval  # noqa: E402

R = load_results()
io, ii = R["iso_out"], R["iso_in"]
h3, h8 = R["hc"]("freshmen", 0.03, 3), R["hc"]("freshmen", 0.08, 3)
fr = -R["cohorts"].loc["freshmen", "diff"]

S = [
("Slide 1 (title + where we are):", [
"Welcome back. This is our third presentation on network position and academic performance, so let me first remind you where we are.",
"In Presentation 1 we asked whether a student's position in a friendship network predicts their later grades, beyond who their direct friends are. We based it on the peer-effort game from the course: students study harder when their friends do, so effort follows Katz-Bonacich centrality. The prediction was that Katz matters and simply counting friends adds nothing.",
f"In Presentation 2 that prediction did not hold. A student's own past GPA strongly predicts their later GPA, with a coefficient of {R['own_gpa']:.3f}, while their contacts' GPA adds nothing. And Katz, once we control for direct links, has an estimate of {R['katz_full'].coef:+.3f} with a p-value of {R['katz_full'].pval:.2f}: not significant.",
"So today we ask a practical question: if network position doesn't predict grades, what can a school still use its students' friendship network for? We look at three possible uses, each with one course model: flagging students who need support, organising study groups, and spreading a study habit. For each model we follow the lectures: the incentive, a small example, how it maps onto our data, the result, and what a school should do."]),
("Slide 2:", [
"Before the models, one honest point. Two of our tests are the same tests Smirnov and Thurner ran in the original paper, so this slide is a replication, not a new finding.",
f"Students' own past GPA predicts their later GPA, their contacts' past GPA does not, and in the university data new friendships join students whose GPAs are {abs(R['uni']['diff']):.3f} points closer than the friendships that break, over almost two hundred thousand ties. In short, students choose friends like themselves, and friends don't change each other's grades.",
f"Our extension is to split this by year. Among freshmen, new ties are {fr:.2f} GPA points closer than broken ones, {R['ratio_lo']} to {R['ratio_hi']} times more than in older years. Sorting happens mainly while friendships are still forming. We take all of this as given, and ask what the network is still good for."]),
("Slide 3:", [
"Use one: can a school use the network to flag students who need support? The model behind that idea is the effort game from Lectures 1, 3 and 7.",
"The players are students, the action is study effort, and the network records who likes whom. A student's payoff has three parts: a benefit from their own effort, a cost of effort that rises with effort, and an extra benefit when their friends also study. That last term makes efforts complements. Lecture 3 shows that in equilibrium, each student's effort is proportional to their Katz-Bonacich centrality.",
"Katz adds up all the walks starting from a student: one for the student, phi times their direct friends, phi squared times their friends' friends, and so on. So its first term is just a friend count; it differs from a friend count only through friends of friends.",
"In the small example, A and B both name two friends. A's friends name others; B's don't. With phi equal to 0.3, A's Katz is 1.96 and B's is 1.60. So P1's prediction is about those extra terms: reach beyond direct friends should raise effort, and so grades."]),
("Slide 4:", [
"To test that, we put Katz and both kinds of friend count into the same regression for next term's GPA, together with own and contacts' GPA this term. If the model is right, Katz stays significant and the friend counts add nothing.",
f"On its own, Katz predicts next term's GPA. But so does out-degree, the number of friends a student names, almost exactly as well. Being named by others does not. Put together, Katz loses its significance, our P2 result, and so does out-degree, with a p-value of {R['out_full'].pval:.2f}. The two are correlated at {R['corr_katz_out']:.2f}. Position as a whole is jointly significant, p equals {R['joint_p']:.3f}, but the regression cannot say whether it is reach or friend count. This holds for every phi we tried.",
f"The model itself tells us why. Our students name very few friends, a median of {R['median_out'][0]:.0f} in the high school, so the friends-of-friends terms are tiny and Katz is almost a friend count. Lecture 7's American students named about {L7_FRIENDS} friends each, which left room for Katz to differ."]),
("Slide 5:", [
f"So, can the network flag students who need support? We put the results in the units Lecture 7 uses: share of a standard deviation of GPA. A student's own past GPA moves next term's GPA by {pct(R['sd_own'])} of a standard deviation. Katz moves it by {100 * R['sd_katz']:.1f} percent, and friend count by {100 * R['sd_out']:.1f} percent. Lecture 7 found {L7_KATZ_SD} and {L7_DEGREE_SD}. Same model, same units: our Katz effect is about {round(7 / (100 * R['sd_katz']))} times smaller than the lecture's, and no bigger than a simple friend count.",
f"We also added a new check. P2's model drops students who name no one, because their contacts' GPA is undefined. Keeping all 655 students: students who name no one, {pct(io.share_of_student_terms)} of student-terms, do no worse next term. Students whom no one names do a little worse: {pct(ii.fell_share_if_1)} of them see their GPA fall, against {pct(ii.fell_share_if_0)} of others. But flagging that group would cover {pct(ii.share_of_student_terms)} of students and catch only {pct(ii.share_of_all_falls_flagged)} of all GPA falls, barely better than picking at random.",
"So the answer to use one is no. A school should flag students for support by their past grades, not their place in the friendship network."]),
("Slide 6:", [
"Use two: organising study groups. To know whether mixing students works, we first need to know why the network is sorted by grades. That is Model 2, network formation from Topic 2.",
"Each student keeps a set of friendships. Each friendship gives a benefit that falls as the GPA gap grows, because similar students work at the same pace and help each other more easily, and it costs time. A network is pairwise stable when no one gains by dropping a friend and no two students both gain by adding one. So a tie only exists where the benefit covers the cost for both.",
"In the example, the benefit is one minus the GPA gap and the cost is 0.5. The two same-level pairs, with gaps of 0.1, keep their ties. The cross-level ties, with gaps of 0.8 to 1, are worth less than they cost and get dropped. The stable network is two same-level pairs. And Schelling's model from Topic 8 adds that even a weak preference like this, repeated every term, sorts the whole network."]),
("Slide 7:", [
"In our data, the model predicts that new ties should have smaller GPA gaps than broken ties. That is exactly the pattern on slide 2, in every cohort, and strongest among freshmen.",
"So for use two: mixing won't happen by itself, because students keep re-sorting by grades. If a school wants students of different levels to learn from each other, it has to build that into the program, and do it in first year, while friendships are still forming. Lecture 7's Bangladesh experiment shows this can work: study groups raised low-ability girls' scores, friendship groups most of all, and the advice there was to let students group by friendship, but with a constraint on each group's average score. Our results point the same way: use the network to form groups, rather than wait for mixing to happen."]),
("Slide 8:", [
"Use three: spreading a study habit. Model 3 is the threshold game, the majority game from Lecture 3 and complex contagion from Topic 8.",
"Each student decides whether to adopt a habit. It has a cost, c, and each friend who already uses it adds a benefit, b. So a student adopts once at least r equals c over b friends have adopted; a harder habit has a larger r. This is a coordination game with many equilibria. Nobody adopting is one of them, and a group of starting students can tip the network into another. We count friends rather than a share, as in Lecture 1's threshold simulation.",
"In the example, r is two. A and B start. C has two adopting friends, so C adopts; then D has two, A and C, so D adopts. E has only one adopting friend and never adopts, and F has no friends, so nothing can ever reach F."]),
("Slide 9:", [
f"We run this on the real high-school and freshmen networks, where each student counts the classmates they named. We start with three or eight percent of students, chosen as the most active, the highest Katz, or at random, and try thresholds from one to five, three hundred times each.",
f"The data give a warning first: in the high-school snapshot we simulate on, {pct(R['never_school_r1'])} of students name no one, so no habit can ever reach them through friends. And if a habit needs four friends, {pct(R['never_r4'][0])} of high-school students and {pct(R['never_r4'][1])} of freshmen can never adopt it through friends."]),
("Slide 10:", [
"Along the bottom is the threshold, up the side the share of students who end up adopting. An easy habit, needing one friend, spreads widely whoever starts it. A hard habit, needing four or more, barely spreads. Only for habits of middle difficulty, around three friends, does the choice of starting students matter. This is the critical-mass idea from Lecture 1: the same rule can produce a cascade or almost nothing."]),
("Slide 11:", [
f"So who should a school start with? With {int(h3.k_seed)} freshmen as starters, starting with the most active students reaches {100 * h3.top_out_degree:.1f} percent, against {100 * h3.random:.1f} for random and {100 * h3.top_katz:.1f} for the highest Katz. That is about {h3.extra_vs_random_top_out_degree:.0f} more students than random, and {h3.extra_top_out_degree_vs_top_katz:.0f} more than the highest-Katz students. Notice that here, unlike in the regression, Katz and friend count finally come apart, and friend count wins.",
f"With more starters, {int(h8.k_seed)}, random does best, at {100 * h8.random:.0f} percent, likely because the top students sit in the same groups and reach the same people.",
"So for use three: with few starters, recruit the students who name the most friends; with more, spread them across groups; and reach students with no friends directly."]),
("Slide 12:", [
"Putting it together, here is the manager's decision. Flagging students for support by network position: not worth it, because the effects are tiny and a friendship-based flag barely beats random. Mixed-ability study groups in first year: worth testing, because students won't mix on their own and the course evidence says designed groups help. A peer-led campaign for a study habit: worth testing, with conditions: habits of middle difficulty, the right starters, and direct outreach to students with no friends."]),
("Slide 13:", [
f"So, back to our question from Presentation 1: does network position predict grades? Barely, about {100 * R['sd_katz']:.1f} percent of a standard deviation, and in this sparse network Katz reach can't be told apart from friend count. The reason is that students choose friends with similar grades, especially in first year: the network reflects grades rather than driving them. What the network is good for is organising study groups a school designs, and spreading habits through active students.",
"That also answers the course's core question for our setting: network structure explains why friends' grades look alike, through selection, and it decides who adopts a new habit, through thresholds."]),
("Slide 14:", [
"Some limits. We show what predicts grades, not what causes them. Katz and friend count are too correlated here to separate. The first-year pattern compares different cohorts, not one cohort followed over four years. And the simulation is a sketch, not a forecast."]),
("Slide 15:", [
"Our last slide shows what each of us contributed. Thank you, and we're happy to take questions."]),
]


class Numbered(canvas.Canvas):
    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        self.pages = []

    def showPage(self):
        self.pages.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        n = len(self.pages)
        for st in self.pages:
            self.__dict__.update(st)
            self.setFont("Helvetica", 8.5); self.setFillColor(HexColor("#6F6C67"))
            self.drawString(20 * mm, 12 * mm, "ECC3841 Presentation 3 speaker script")
            self.drawRightString(A4[0] - 20 * mm, 12 * mm, f"Page {self._pageNumber} of {n}")
            self.setFillColor(HexColor("#C4602F")); self.setFont("Helvetica-Bold", 8.5)
            self.drawString(20 * mm, A4[1] - 12 * mm, "ECC3841 NETWORK ECONOMICS  |  PRESENTATION 3")
            super().showPage()
        super().save()


def main():
    words = sum(len(p.split()) for _, ps in S for p in ps)
    h = ParagraphStyle("h", fontName="Helvetica-Bold", fontSize=13, textColor=HexColor("#C4602F"), spaceBefore=10, spaceAfter=4)
    b = ParagraphStyle("b", fontName="Helvetica", fontSize=10.8, leading=15.2, textColor=HexColor("#262522"), spaceAfter=6)
    out = P3 / "scripts.pdf"
    doc = SimpleDocTemplate(str(out), pagesize=A4, leftMargin=20 * mm, rightMargin=20 * mm, topMargin=20 * mm, bottomMargin=20 * mm)
    story = []
    for title, paras in S:
        story.append(KeepTogether([Paragraph(title, h), Paragraph(paras[0], b)]))
        story += [Paragraph(p, b) for p in paras[1:]]
    doc.build(story, canvasmaker=Numbered)
    print(out, f"({words} words, about {words / 130:.0f} minutes at 130 words a minute)")


if __name__ == "__main__":
    main()
