"""Builds P3/scripts.pdf, the ~15-minute speaker script for Presentation 3.

'Slide N:' headings follow the deck: Slide 1 covers the title and recap pages,
Slides 2-17 match the page numbers, Slide 18 is the thank-you page (references follow as an appendix). Numbers come from the
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

S = [
("Slide 1 (title + recap of Presentation 2):", [
"Welcome back. This is our third presentation on network position and academic performance. First, a quick recap.",
f"In Presentation 1 we asked whether a student's position in a friendship network predicts their later grades, beyond their direct friends, using the peer-effort game, which says Katz centrality should matter. In Presentation 2, a student's own past GPA predicted later GPA with a coefficient of {R['own_gpa']:.3f}, and contacts' GPA added nothing. Pooled Katz looked strong at {R['pooled_katz']:+.3f}, but fell to {R['pooled_katz_ctrl']:+.3f} once direct links were counted, and in the school panel Katz beyond direct links was {R['katz_full'].coef:+.3f}, p equals {R['katz_full'].pval:.2f}. So P1's prediction did not hold.",
"That leaves a practical question for today. Many schools run peer programs, such as study buddies, peer mentors and student ambassadors, that assume the friendship network helps. If position barely predicts grades, what can a school still use its students' friendship network for?"]),
("Slide 2:", [
"We look at three possible uses, each with one model from the course. Model 1, the effort game and Katz centrality: can the network flag students who need support? Model 2, network formation: how should a school organise study groups? Model 3, threshold contagion: who should start a study-habit campaign? Each time we follow the lectures: the incentive, a small example, how it maps onto our data, the result, and what a school should do."]),
("Slide 3:", [
"First, one honest point. Two of our tests are the same ones Smirnov and Thurner ran in the original paper, so the left side is a replication. Own past GPA predicts later GPA, contacts' GPA does not, and new university friendships join students whose GPAs are closer than the friendships that break.",
f"Our extension is on the right: split by year, freshmen sort {R['ratio_lo']} to {R['ratio_hi']} times more than older students, while friendships are still forming. So students choose friends like themselves, and friends don't change each other's grades. We take that as given, and ask what the network is still good for."]),
("Slide 4:", [
"Use one: could a school use the network to flag students who need support? The model behind that idea is the effort game from Lectures 1, 3 and 7. The players are students, and each chooses how hard to study. The payoff has three parts: a benefit from their own effort, a cost that rises with effort, and an extra benefit when their friends also study, which makes efforts complements. Lecture 3 shows that in equilibrium, each student's effort is proportional to their Katz-Bonacich centrality. If that were true here, central students would be the ones to watch.",
"Katz adds up walks: one, plus phi times direct friends, plus phi squared times friends of friends, and so on. Its first term is just a friend count. In the example, A and B both name two friends, but A's friends name others: A's Katz is 1.96, B's is 1.60. P1's prediction is about those extra terms: reach beyond direct friends should raise effort, and so grades."]),
("Slide 5:", [
f"To test it, we map the model onto our data: the network is who likes whom, and we regress next term's GPA on Katz and both friend counts, controlling for own and contacts' GPA this term. If the model is right, Katz stays significant and the friend counts add nothing.",
f"Alone, Katz predicts next term's GPA, and so does out-degree, the number of friends a student names. Together, neither is significant: Katz p equals {R['katz_full'].pval:.2f}, out-degree {R['out_full'].pval:.2f}. They are correlated at {R['corr_katz_out']:.2f}. Position as a whole is jointly significant, but we can't say whether it is reach or friend count, for any phi we tried.",
f"The model tells us why: students name a median of {R['median_out'][0]:.0f} friend in the high school, so friends-of-friends terms are tiny and Katz is almost a friend count. Lecture 7's US students named about {L7_FRIENDS} each."]),
("Slide 6:", [
f"How big is this? In Lecture 7's units, own past GPA moves next term's GPA by {pct(R['sd_own'])} of a standard deviation; Katz by {100 * R['sd_katz']:.1f} percent, against {L7_KATZ_SD} in the lecture, about {round(7 / (100 * R['sd_katz']))} times smaller.",
f"Our new check keeps students P2 dropped. Students who name no one do no worse next term. Students whom no one names are a little more likely to see their GPA fall, {pct(ii.fell_share_if_1)} against {pct(ii.fell_share_if_0)}, but flagging them would cover {pct(ii.share_of_student_terms)} of students to catch {pct(ii.share_of_all_falls_flagged)} of falls, barely better than random. So for use one: no. A school should flag students for support by their past grades, not by their place in the friendship network."]),
("Slide 7:", [
"Use two is organising study groups. To know whether mixing students can work, we first need to know why the network is sorted by grades. Model 2 is network formation from Topic 2. Each friendship's benefit falls as the GPA gap grows, because similar students work at the same pace and help each other more easily, and every friendship costs time. In a pairwise stable network nobody gains by dropping a friend and no pair gains by adding one, so ties survive only where both sides gain.",
"In the example, with benefit one minus the gap and cost 0.5, same-level pairs keep their ties and cross-level ties are dropped. Schelling's model from Topic 8 adds that even a weak preference, repeated every term, sorts a whole network."]),
("Slide 8:", [
"That prediction matches what we saw on slide 3, in every cohort. It explains the baseline: similar students keep re-matching, so it is selection, not influence. It explains why position adds little: a well-connected student mostly reaches peers with similar grades.",
"And it gives use two: mixing won't happen by itself, so a school should form mixed-ability study groups, early, in first year. Lecture 7's Bangladesh experiment supports this: friendship groups with a cap on each group's average score raised scores."]),
("Slide 9:", [
"Use three. Model 3 is the threshold game: the majority game from Lecture 3 and complex contagion from Topic 8. A habit costs c; each friend using it adds b; so a student adopts once at least r equals c over b friends have. It is a coordination game: nobody adopting is an equilibrium, and starting students can tip the network into another.",
"In the example, with r equal to two, A and B start. C has two adopting friends, so C adopts; then D has two, A and C, so D adopts. E has only one adopting friend, and F has none, so neither ever adopts. Who starts, how hard the habit is, and who has no friends at all decide how far it spreads."]),
("Slide 10:", [
f"We simulate this on the real high-school and freshmen networks, starting with 3 or 8 percent of students: the most active, the highest Katz, or random. A warning first: {pct(R['never_school_r1'])} of high-school students in the snapshot name no one, so friends can never reach them, and if a habit needs four friends, {pct(R['never_r4'][0])} of high-school students and {pct(R['never_r4'][1])} of freshmen can never adopt it. We try thresholds from one to five, three hundred times each."]),
("Slide 11:", [
"Along the bottom is the threshold, up the side the share of students who end up adopting. An easy habit, needing one friend, spreads widely whoever starts it; a hard one, needing four or more, barely spreads. Only for habits of middle difficulty, about three friends, does the choice of starters matter. This is the critical-mass idea from Lecture 1: the same rule can produce a large cascade or almost nothing, depending on the network and the habit."]),
("Slide 12:", [
f"There, with {int(h3.k_seed)} freshmen starting, the most active students reach {100 * h3.top_out_degree:.1f} percent, against {100 * h3.random:.1f} for random and {100 * h3.top_katz:.1f} for highest Katz: about {h3.extra_vs_random_top_out_degree:.0f} more students than random. Here Katz and friend count finally come apart, and friend count wins. With {int(h8.k_seed)} starters, random does best, likely because top students reach the same people.",
"So for use three: with few starters, recruit students who name the most friends; with more, spread them out; and reach students with no friends directly."]),
("Slide 13:", [
"Putting the three uses together gives the manager's decision. Flagging students for support by network position: not worth it, because the effects are tiny and a friendship-based flag barely beats random. Mixed-ability study groups in first year: worth testing, because students won't mix on their own and the course evidence says designed groups help. A peer-led study-habit campaign: worth testing, with conditions: habits of middle difficulty, the right starters for the budget, and direct outreach to students with no friends."]),
("Slide 14:", [
f"Back to our core question. Does position predict grades? Barely, about {100 * R['sd_katz']:.1f} percent of a standard deviation, and here Katz can't be told apart from friend count. Why does the network look like this? Students choose friends with similar grades, especially in first year. What is the network for? Organising study groups a school designs, and spreading habits through active students. In course terms, network structure explains why friends' grades look alike, and decides who adopts a new habit."]),
("Slide 15:", [
"The literature supports this reading. Manski's reflection problem warns that similar grades among friends don't prove influence. Sacerdote shows that random assignment would allow a causal reading, but our friendships are chosen. And Calvó-Armengol and co-authors, Lecture 7, found Katz beats degree in US schools; our students name far fewer friends, which is why the two coincide here."]),
("Slide 16:", [
"The limits: we show prediction, not cause; Katz and friend count are too correlated to separate here; the first-year pattern compares different cohorts; and the simulation is a sketch. A stronger next test would add time-varying controls, school-by-time effects, and ideally random assignment or a natural experiment."]),
("Slide 17:", [
"To conclude: P1 asked the question, P2 gave a small, direct-link-driven answer, and P3 explains it with course models and turns it into three practical uses: target support by grades, design study groups early, and seed habits through active students. That is a more complete and more honest answer than either the regression or the theory alone."]),
("Slide 18:", [
"Our last slide shows what each of us contributed. Thank you, and we're happy to take questions. Our references are in the appendix."]),
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
