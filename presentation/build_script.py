"""Builds P3/scripts.pdf, the ~15-minute speaker script for Presentation 3.

'Slide N:' headings follow the 15-slide deck: Slide 1 covers the title and recap pages,
Slides 2-13 match the page numbers, Slide 14 is the contributions page. Numbers come from the
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
"Welcome back. This is our third presentation on network position and academic performance.",
f"Presentation 1 asked whether a student's position in a friendship network predicts later grades, beyond their direct friends, using the peer-effort game, which says Katz centrality should matter. Presentation 2 found it doesn't. Own past GPA predicts later GPA at {R['own_gpa']:.3f}, contacts' GPA adds nothing, and Katz falls from {R['pooled_katz']:+.3f} to {R['pooled_katz_ctrl']:+.3f} once direct links are counted; in the school panel it is {R['katz_full'].coef:+.3f}, p equals {R['katz_full'].pval:.2f}.",
"So today's question is practical. Schools run peer programs that assume the friendship network helps. If position barely predicts grades, what can a school still use the network for?"]),
("Slide 2:", [
"We look at three uses, each with a model from the course that analyses students' incentives. Model 1, the effort game: can the network flag students who need support? Model 2, network formation: how should a school organise study groups? Model 3, threshold contagion: who should start a study-habit campaign? For each one: the incentive, a small example, our data, and what a school should do.",
"These three uses are the decisions a school actually faces with peer programs: who to help, how to group students, and how to spread good habits. So each model ends with a recommendation a manager could act on."]),
("Slide 3:", [
"Model 1 is the effort game from Lectures 1, 3 and 7. Each student chooses how hard to study. Effort pays off, it has a rising cost, and it pays off more when friends also study, so efforts are complements. Lecture 3 shows that in equilibrium each student's effort is proportional to their Katz-Bonacich centrality. In plain words: you study harder when your friends study harder, and they study harder when their friends do, so your friends' friends matter too. If that held here, the most central students would be the ones to watch, and the least central the ones to worry about.",
"Katz adds up walks: one, plus phi times direct friends, plus phi squared times friends of friends, and so on. Its first term is just a friend count. In the example, A and B both name two friends, but A's friends name others, so A's Katz is 1.96 and B's is 1.60. The model's real claim is about those extra terms: reach beyond direct friends."]),
("Slide 4:", [
"So we put Katz and both friend counts into one regression for next term's GPA, holding own and contacts' GPA fixed. If the model is right, Katz stays significant and friend counts add nothing.",
f"On its own, Katz predicts next term's GPA, but so does out-degree, the number of friends a student names. Together, neither survives. They correlate at {R['corr_katz_out']:.2f}, because our students name a median of {R['median_out'][0]:.0f} friend, so the friends-of-friends terms are tiny and Katz is almost a friend count. Lecture 7's US students named about {L7_FRIENDS} friends each, which is why Katz could stand out there."]),
("Slide 5:", [
f"How much does position matter in practice? In Lecture 7's units, Katz moves next term's GPA by {100 * R['sd_katz']:.1f} percent of a standard deviation, about {round(7 / (100 * R['sd_katz']))} times less than the lecture's {L7_KATZ_SD}, while own past GPA moves it by {pct(R['sd_own'])}.",
f"We also checked students P2's model left out, those with no ties. Flagging everyone whom no one names would cover {pct(ii.share_of_student_terms)} of students and catch only {pct(ii.share_of_all_falls_flagged)} of GPA falls, barely better than picking at random. So for use one, the answer is no: flag students by their past grades, not their place in the network."]),
("Slide 6:", [
"Use two is study groups, and for that we need to know why the network looks the way it does. Model 2 is network formation from Topic 2. Each friendship gives a benefit that falls as the GPA gap grows, because similar students work at the same pace, and it costs time. A network is pairwise stable when nobody gains by dropping a friend and no pair gains by adding one, so ties survive only where both sides gain. The incentive is simple: a friendship is worth your time only if it helps you, and that is easier with someone at your own level.",
"In the example, with benefit one minus the gap and cost 0.5, the same-level pairs keep their ties and the cross-level ties are dropped. And Schelling's model from Topic 8 adds that even a weak preference like this, repeated every term, sorts a whole network."]),
("Slide 7:", [
f"The model predicts that new ties should join students with closer grades than the ties that break. On the left is Smirnov and Thurner's own test, which we replicate: across almost two hundred thousand university ties, new ties are {abs(R['uni']['diff']):.3f} GPA points closer, and the high school points the same way.",
f"On the right is our extension. Split by year, freshmen sort {R['ratio_lo']} to {R['ratio_hi']} times more than older students, while friendships are still forming."]),
("Slide 8:", [
"This explains two things. It explains P2's baseline: contacts' GPA added nothing because friends are chosen for similar grades, so it is selection, not influence. And it explains why position adds little: a well-connected student mostly reaches peers with similar grades.",
"For use two, it means mixing won't happen by itself. A school should form mixed-ability study groups, and do it in first year. Lecture 7's Bangladesh experiment supports this: friendship groups with a cap on each group's average score raised scores."]),
("Slide 9:", [
"Use three is spreading a study habit, for example joining a weekly revision group. Model 3 is the threshold game: the majority game from Lecture 3 and complex contagion from Topic 8. A habit costs c and each friend using it adds b, so a student adopts once at least r equals c over b friends have adopted. If the group costs two evenings a week and each friend in it makes it more useful and more fun, a student joins once enough friends are already there; the more demanding the habit, the more friends it takes. It is a coordination game: nobody adopting is an equilibrium, and a few starting students can tip the network into another.",
f"In the example, with r equal to two, A and B start, C follows, then D; E, with one adopting friend, and F, with none, never adopt. We simulate this on our real networks, and the isolated case is common: {pct(R['never_school_r1'])} of high-school students name no one, so friends can never reach them."]),
("Slide 10:", [
"This chart shows the result for both networks. Along the bottom is the threshold, how many friends a student needs to see before joining; up the side is the share of students who end up adopting, starting from three percent of students. An easy habit spreads whoever starts it; a hard one barely spreads. Only for habits of middle difficulty, about three friends, does the choice of starters matter. That is the critical-mass idea from Lecture 1."]),
("Slide 11:", [
f"In that window, with {int(h3.k_seed)} freshmen starting, the most active students reach {100 * h3.top_out_degree:.1f} percent, against {100 * h3.random:.1f} for random and {100 * h3.top_katz:.1f} for the highest Katz: about {h3.extra_vs_random_top_out_degree:.0f} more students than random. Here, unlike in the regression, Katz and friend count come apart, and friend count wins. With {int(h8.k_seed)} starters, random does best, likely because top students reach the same people.",
"So for use three: with few starters, recruit the students who name the most friends; with more, spread them out; and reach isolated students directly."]),
("Slide 12:", [
"For a manager, this comes down to one decision about where to put resources. Flagging students by network position is not worth it, because position tells you almost nothing that last term's grades don't already tell you. Mixed-ability study groups in first year are worth testing, because students will not mix on their own, and the course evidence says designed groups help. A peer-led study-habit campaign is worth testing, under the conditions we just saw: a habit that is neither too easy nor too hard, the right starting students for the budget, and direct outreach to students with no friends.",
"In one line: use grades to decide who needs help, and use the network to organise and spread, not to rank students."]),
("Slide 13:", [
"Back to the course's core question: how does network structure shape what students do and the outcomes we see? It explains an outcome, why friends' grades look alike: students choose similar friends, rather than peers raising each other's effort. And it decides a choice, who adopts a new habit, because each student waits for enough friends.",
"What we cannot claim is cause: these are predictions, and in a network this sparse Katz and friend count cannot be separated. So our answer to Presentation 1 is that position follows grades more than grades follow position."]),
("Slide 14:", [
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
