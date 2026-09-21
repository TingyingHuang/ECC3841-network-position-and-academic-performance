"""
Presentation 2 (progress report / preliminary results), visual-heavy,
same style as build_visual_deck.py. Numbers match progress_brief.pdf.

    python3 build_assets_p2.py       # generates the 3 result figures
    python3 build_presentation2_deck.py
"""
from pathlib import Path

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

ROOT = Path(__file__).resolve().parent
A = ROOT / "assets_p2"

BLUE = RGBColor(0x2A, 0x78, 0xD6)
ORANGE = RGBColor(0xEB, 0x68, 0x34)
GREEN = RGBColor(0x2E, 0x9E, 0x5B)
RED = RGBColor(0xD2, 0x41, 0x3A)
DARK = RGBColor(0x19, 0x18, 0x0F)
GRAY = RGBColor(0x55, 0x50, 0x3F)
BGCOL = RGBColor(0xFA, 0xF9, 0xF6)
CARD = RGBColor(0xF1, 0xEF, 0xE8)
BORDER = RGBColor(0xDD, 0xD8, 0xCD)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)

HEAD = "Georgia"
BODY = "Calibri"

prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)
BLANK = prs.slide_layouts[6]


def slide():
    s = prs.slides.add_slide(BLANK)
    r = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
    r.fill.solid(); r.fill.fore_color.rgb = BGCOL
    r.line.fill.background(); r.shadow.inherit = False
    s.shapes._spTree.remove(r._element)
    s.shapes._spTree.insert(2, r._element)
    return s


def text(s, left, top, width, height, body, size=18, bold=False, color=DARK,
         font=BODY, align=PP_ALIGN.LEFT, italic=False, spacing=1.18,
         anchor=MSO_ANCHOR.TOP):
    box = s.shapes.add_textbox(Inches(left), Inches(top), Inches(width), Inches(height))
    tf = box.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    for i, ln in enumerate(body.split("\n")):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = ln
        p.alignment = align
        p.line_spacing = spacing
        for run in p.runs:
            run.font.size = Pt(size)
            run.font.bold = bold
            run.font.italic = italic
            run.font.color.rgb = color
            run.font.name = font
    return box


def bullets(s, left, top, width, height, items, size=16, color=DARK, gap=10):
    box = s.shapes.add_textbox(Inches(left), Inches(top), Inches(width), Inches(height))
    tf = box.text_frame
    tf.word_wrap = True
    for i, it in enumerate(items):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.space_after = Pt(gap)
        p.line_spacing = 1.25
        r = p.add_run()
        r.text = "  •  " + it
        r.font.size = Pt(size)
        r.font.color.rgb = color
        r.font.name = BODY
    return box


def eyebrow(s, t, color=ORANGE):
    text(s, 0.7, 0.42, 11.5, 0.4, t, size=13, bold=True, color=color)


def title(s, t, size=26):
    text(s, 0.7, 0.8, 11.9, 1.0, t, size=size, bold=True, color=DARK, font=HEAD, spacing=1.05)


def takeaway(s, t, color=DARK, bold=True, top=6.75):
    text(s, 0.7, top, 11.9, 0.6, t, size=15, bold=bold, color=color)


def figure(s, name, top=1.65, height=4.85, folder=A):
    pic = s.shapes.add_picture(str(folder / name), 0, Inches(top), height=Inches(height))
    pic.left = int((prs.slide_width - pic.width) / 2)
    return pic


def pagenum(s, n):
    text(s, 12.5, 7.08, 0.7, 0.32, str(n), size=11, color=GRAY, align=PP_ALIGN.RIGHT)


def box(s, x, y, w, h, txt, fc=WHITE, ec=BORDER, tcolor=DARK, size=13, bold=False):
    c = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
    c.adjustments[0] = 0.08
    c.fill.solid(); c.fill.fore_color.rgb = fc
    c.line.color.rgb = ec; c.line.width = Pt(1.4); c.shadow.inherit = False
    tf = c.text_frame; tf.word_wrap = True; tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    tf.margin_left = tf.margin_right = Inches(0.12)
    p = tf.paragraphs[0]; p.alignment = PP_ALIGN.CENTER
    r = p.add_run(); r.text = txt
    r.font.size = Pt(size); r.font.bold = bold; r.font.color.rgb = tcolor; r.font.name = BODY
    return c


# ===================================================== 1. title
s = slide()
text(s, 0.9, 2.0, 11.5, 0.5, "ECC3841 NETWORK ECONOMICS  ·  PRESENTATION 2",
     size=13, bold=True, color=ORANGE)
text(s, 0.9, 2.55, 11.5, 1.9, "Network Position and\nAcademic Performance",
     size=42, bold=True, color=DARK, font=HEAD, spacing=1.05)
text(s, 0.9, 4.65, 11.2, 1.0, "What we found so far — a progress report",
     size=20, color=GRAY, italic=True)
text(s, 0.9, 6.5, 9, 0.5, "Amy Bing   ·   Tingying Huang", size=13, color=GRAY)

# ===================================================== 2. recap + what we did
s = slide()
eyebrow(s, "WHERE WE LEFT OFF")
title(s, "The plan from last time")
text(s, 0.7, 1.75, 11.9, 0.9,
     "Does a student's position in a friendship network predict their grades, on top of "
     "popularity and who their direct friends are? The plan: measure Katz-Bonacich "
     "centrality, sweep it across φ, and test it against that question.",
     size=16, color=GRAY, spacing=1.3)

steps = [
    ("1", "Replicate", "Confirm the data behaves\nthe way prior work found."),
    ("2", "Naive test", "Position alone,\nno popularity control."),
    ("3", "Planned test", "Add popularity, sweep φ,\npool all 5 groups."),
    ("4", "Check + fix", "Test the assumptions.\nFound one had failed."),
]
x0, bw, gap = 0.7, 2.85, 0.28
for i, (n, head, desc) in enumerate(steps):
    x = x0 + i * (bw + gap)
    box(s, x, 3.1, bw, 0.85, n, fc=ORANGE, tcolor=WHITE, size=20, bold=True)
    text(s, x, 4.1, bw, 0.5, head, size=15, bold=True, color=DARK, align=PP_ALIGN.CENTER)
    text(s, x, 4.6, bw, 1.4, desc, size=12.5, color=GRAY, align=PP_ALIGN.CENTER, spacing=1.25)
takeaway(s, "This brief reports what running that plan actually found.", bold=False, color=GRAY)
pagenum(s, 2)

# ===================================================== 3. result 1
s = slide()
eyebrow(s, "RESULT 1")
title(s, "The replication holds")
bullets(s, 0.7, 1.9, 11.9, 4.2, [
    "A student's own past GPA strongly predicts their next GPA (coefficient 0.955).",
    "Once that's controlled, a friend's past GPA does not predict your future GPA — "
    "not significant (p = 0.557).",
    "New friendships show a smaller GPA gap than friendships about to end, in the "
    "university sample (p < 0.001); same direction in high school, not significant.",
], size=17, gap=18)
takeaway(s, "Both match Smirnov & Thurner. This is the foundation everything else builds on.",
         color=ORANGE)
pagenum(s, 3)

# ===================================================== 4. result 2 (naive)
s = slide()
eyebrow(s, "RESULT 2")
title(s, "The naive effect is popularity, relabelled")
bullets(s, 0.7, 1.9, 11.9, 3.5, [
    "Katz-Bonacich alone, net of friend GPA: coefficient +0.093, p < 0.001. Looks like "
    "position matters.",
    "Add raw in-degree and out-degree to the same regression: the coefficient drops to "
    "−0.028, p = 0.446 — no longer significant.",
    "In-degree itself: +0.153, p < 0.001. That's what was driving the naive result.",
], size=17, gap=18)
takeaway(s, "The naive effect was popularity wearing a different name.", color=ORANGE)
pagenum(s, 4)

# ===================================================== 5. the gap we found
s = slide()
eyebrow(s, "RESULT 3")
title(s, "The planned test, and a gap we found in it")
figure(s, "fig_p2_gpa_gap.png", top=1.55, height=4.55)
takeaway(s, "Own past GPA can only be built for the school group — the other 80% of the "
             "pooled sample can't have it.", color=ORANGE)
pagenum(s, 5)

# ===================================================== 6. three specs
s = slide()
eyebrow(s, "COMPARING THE THREE TESTS")
title(s, "Three specifications, three different pictures")
figure(s, "fig_p2_three_specs.png", top=1.55, height=4.9)
takeaway(s, "The corrected test — the only one with own past GPA properly controlled — finds nothing.",
         bold=False, color=GRAY)
pagenum(s, 6)

# ===================================================== 7. phi sweep compare
s = slide()
eyebrow(s, "ROBUSTNESS")
title(s, "Checked across the whole φ range, not just one value")
figure(s, "fig_p2_phi_compare.png", top=1.55, height=4.9)
takeaway(s, "Before the fix, the line swings from significantly positive to significantly "
             "negative. After it, it's flat.", bold=False, color=GRAY)
pagenum(s, 7)

# ===================================================== 8. conclusion
s = slide()
eyebrow(s, "CONCLUSION")
title(s, "What this means")
box(s, 0.7, 1.75, 11.9, 1.1,
    "Net of popularity, friend GPA, and a student's own past performance, we find no "
    "evidence that network position independently predicts grades.",
    fc=RGBColor(0xE9, 0xF5, 0xEC), ec=GREEN, size=17, bold=True)
bullets(s, 0.7, 3.15, 11.9, 3.3, [
    "This is the first time this claim has been tested with a real time lag and an "
    "own-performance control — a cross-section could never support that.",
    "It shows a general risk: pooling groups with different data structures can "
    "manufacture a significant coefficient the correctly specified subsample doesn't support.",
    "It's a decision-relevant answer: interventions built around widening students' "
    "network reach aren't supported by this data once the obvious confounds are handled.",
], size=15.5, gap=14)
pagenum(s, 8)

# ===================================================== 9. limitations / next
s = slide()
eyebrow(s, "LIMITATIONS AND WHAT'S NEXT")
title(s, "Where this is still open")
bullets(s, 0.7, 1.9, 11.9, 4.4, [
    "The corrected test has n = 2,088 from 535 students — a much wider confidence "
    "interval than the pooled test's 36,696.",
    "It can't be extended to the university cohorts: their GPA is a single measurement, "
    "not a time series.",
    "Next: recompute centrality using only mutually-confirmed ties (the 24–27% that go "
    "both ways) — testing directly whether weak, one-way \"likes\" are the reason we see "
    "no effect.",
    "Betweenness and eigenvector centrality still need to go through the corrected, "
    "school-only design.",
], size=16, gap=16)
pagenum(s, 9)

# ===================================================== 10. thanks
s = slide()
text(s, 0.9, 2.6, 11, 1.2, "Thank you", size=42, bold=True, color=DARK, font=HEAD)
text(s, 0.95, 4.0, 11, 0.6,
     "Full numbers and setup: research_brief.pdf and progress_brief.pdf.", size=15, color=GRAY)
text(s, 0.95, 6.4, 6, 0.5, "Questions?", size=16, bold=True, color=ORANGE)
pagenum(s, 10)

out = ROOT / "Presentation2.pptx"
prs.save(out)
print(f"Saved -> {out}  ({len(prs.slides._sldIdLst)} slides)")
