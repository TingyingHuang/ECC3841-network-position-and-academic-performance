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


def stat_bullets(s, left, top, width, height, items, size=15, gap=16, lead_size=None):
    """items: list of (lead, lead_color, rest) -- lead is the bolded, colored
    number/stat; rest is the short plain-language phrase after it."""
    lead_size = lead_size or size + 1
    box = s.shapes.add_textbox(Inches(left), Inches(top), Inches(width), Inches(height))
    tf = box.text_frame
    tf.word_wrap = True
    for i, (lead, lcolor, rest) in enumerate(items):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.space_after = Pt(gap)
        p.line_spacing = 1.2
        r1 = p.add_run(); r1.text = "  •  " + lead + "   "
        r1.font.size = Pt(lead_size); r1.font.bold = True
        r1.font.color.rgb = lcolor; r1.font.name = BODY
        r2 = p.add_run(); r2.text = rest
        r2.font.size = Pt(size); r2.font.color.rgb = DARK; r2.font.name = BODY
    return box


def eyebrow(s, t, color=ORANGE):
    text(s, 0.7, 0.42, 11.5, 0.4, t, size=13, bold=True, color=color)


def title(s, t, size=26):
    text(s, 0.7, 0.8, 11.9, 1.0, t, size=size, bold=True, color=DARK, font=HEAD, spacing=1.05)


LBLUE = RGBColor(0xE9, 0xF0, 0xFA)
LGREEN = RGBColor(0xE9, 0xF5, 0xEC)


def takeaway(s, t, kind="claim", top=6.55, height=0.65, size=14):
    fc, ec = (LBLUE, BLUE) if kind == "claim" else (CARD, BORDER)
    box(s, 0.7, top, 11.9, height, t, fc=fc, ec=ec, tcolor=DARK, size=size, bold=(kind == "claim"))


def pill(s, x, y, txt, fc=BLUE, w=None, h=0.32, size=11):
    w = w if w else 0.13 * len(txt) + 0.35
    c = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
    c.adjustments[0] = 0.5
    c.fill.solid(); c.fill.fore_color.rgb = fc
    c.line.fill.background(); c.shadow.inherit = False
    tf = c.text_frame; tf.word_wrap = False; tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    tf.margin_left = tf.margin_right = Inches(0.08)
    p = tf.paragraphs[0]; p.alignment = PP_ALIGN.CENTER
    r = p.add_run(); r.text = txt
    r.font.size = Pt(size); r.font.bold = True; r.font.color.rgb = WHITE; r.font.name = BODY
    return c


def accent_bar(s, x, y, h, w=0.09, color=ORANGE):
    r = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
    r.fill.solid(); r.fill.fore_color.rgb = color
    r.line.fill.background(); r.shadow.inherit = False
    return r


def figure(s, name, top=1.65, height=4.85, folder=A, left=None):
    pic = s.shapes.add_picture(str(folder / name), 0, Inches(top), height=Inches(height))
    pic.left = Inches(left) if left is not None else int((prs.slide_width - pic.width) / 2)
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
dec = s.shapes.add_picture(str(ROOT / "assets" / "decor_network.png"),
                            Inches(9.7), Inches(4.7), width=Inches(3.1))
dec.left = int(prs.slide_width - dec.width - Inches(0.35))
accent_bar(s, 0.55, 2.58, 1.55)
text(s, 0.9, 2.0, 11.5, 0.5, "ECC3841 NETWORK ECONOMICS  ·  PRESENTATION 2",
     size=13, bold=True, color=ORANGE)
text(s, 0.9, 2.55, 11.5, 1.9, "Network Position and\nAcademic Performance",
     size=42, bold=True, color=DARK, font=HEAD, spacing=1.05)
text(s, 0.9, 4.65, 11.2, 1.0, "Progress report: an initial result, then a model correction",
     size=20, color=GRAY, italic=True)
text(s, 0.9, 6.5, 9, 0.5, "Amy Bing   ·   Tingying Huang", size=13, color=GRAY)

# ===================================================== 2. recap + what we did
s = slide()
eyebrow(s, "RESEARCH PROGRESS")
title(s, "How the analysis changed")
text(s, 0.7, 1.75, 11.9, 0.7,
     "Our question remains: does outgoing network reach predict later grades beyond prior GPA and direct contacts? "
     "The important progress was discovering which data can answer it.",
     size=16, color=GRAY, spacing=1.3)

steps = [
    ("1", "Replicate", "Confirm known GPA\nand tie patterns."),
    ("2", "Initial result", "Estimate a pooled\nKatz--GPA association."),
    ("3", "Audit", "Check time order and\nwhat each cohort records."),
    ("4", "Corrected test", "Use the school panel\nwith prior GPA."),
]
x0, bw, gap = 0.7, 2.85, 0.28
for i, (n, head, desc) in enumerate(steps):
    x = x0 + i * (bw + gap)
    box(s, x, 3.1, bw, 0.85, n, fc=ORANGE, tcolor=WHITE, size=20, bold=True)
    text(s, x, 4.1, bw, 0.5, head, size=15, bold=True, color=DARK, align=PP_ALIGN.CENTER)
    text(s, x, 4.6, bw, 1.4, desc, size=12.5, color=GRAY, align=PP_ALIGN.CENTER, spacing=1.25)
takeaway(s, "The presentation reports the correction as part of the research process.", kind="fact", top=6.6)
pagenum(s, 2)

# ===================================================== 3. result 1
s = slide()
eyebrow(s, "RESULT 1")
title(s, "The replication holds")
stat_bullets(s, 0.7, 2.1, 5.7, 4.0, [
    ("0.955", GREEN, "own past GPA strongly predicts next GPA"),
    ("p = 0.557", GRAY, "friend's past GPA — no effect"),
    ("p < 0.001", DARK, "new friends more similar than friends about to leave "
     "(university; not sig. in school)"),
], size=14, gap=20)
figure(s, "fig_p2_result1_arrows.png", top=1.95, height=4.15, left=6.7)
takeaway(s, "Both match Smirnov & Thurner. This is the foundation everything else builds on.",
         kind="claim", top=6.6)
pagenum(s, 3)

# ===================================================== 4. result 2 (naive)
s = slide()
eyebrow(s, "INITIAL RESULT")
title(s, "The first pooled result looked significant")
stat_bullets(s, 0.7, 2.1, 5.7, 4.0, [
    ("+0.089", GREEN, "Katz alone: a positive pooled GPA association"),
    ("+0.012", GRAY, "after direct-degree controls"),
    ("p = 0.760", GRAY, "the adjusted Katz estimate is not significant"),
], size=14, gap=20)
figure(s, "fig_p2_naive_reveal.png", top=1.95, height=4.15, left=6.7)
takeaway(s, "This was a useful signal, but it was not yet a valid test of later academic performance.", kind="claim", top=6.6)
pagenum(s, 4)

# ===================================================== 5. the gap we found
s = slide()
eyebrow(s, "MODEL AUDIT")
title(s, "The pooled university comparison cannot identify a later-GPA effect")
figure(s, "fig_p2_gpa_gap.png", top=1.55, height=4.35)
takeaway(s, "University GPA is static: it cannot control baseline achievement or establish time order. Only school GPA repeats over time.",
         kind="claim", top=6.5, height=0.65)
pagenum(s, 5)

# ===================================================== 6. three specs
s = slide()
eyebrow(s, "CORRECTED PRIMARY TEST")
title(s, "After correcting the model, the effect is no longer significant")
figure(s, "fig_p2_three_specs.png", top=1.55, height=4.65)
takeaway(s, "School panel model: later GPA on prior GPA, outgoing Katz, direct links, contact GPA, and time effects. Katz = +0.009, p = 0.139.",
         kind="fact", top=6.35, height=0.7)
pagenum(s, 6)

# ===================================================== 7. phi sweep compare
s = slide()
eyebrow(s, "ROBUSTNESS")
title(s, "The school result remains non-significant across the φ range")
figure(s, "fig_p2_phi_compare.png", top=1.55, height=4.65)
takeaway(s, "Pooled results change with φ; the lagged school estimates are positive but never significant.",
         kind="fact", top=6.35, height=0.7)
pagenum(s, 7)

# ===================================================== 8. conclusion
s = slide()
eyebrow(s, "PRESENTATION 2 CONCLUSION")
title(s, "What we can conclude at this stage")
pill(s, 0.7, 1.68, "HEADLINE FINDING", fc=GREEN)
box(s, 0.7, 2.05, 11.9, 1.1,
    "The initial association did not survive the model audit. In the usable longitudinal sample, "
    "we find no statistically significant evidence that outgoing network reach predicts later grades.",
    fc=LGREEN, ec=GREEN, size=17, bold=True)

why = [
    ("t+1", "Time order", "The primary model predicts later GPA from the earlier network."),
    ("!", "Interpretation", "The university association remains descriptive, not causal."),
    ("P3", "Next step", "We will analyse incentives and mechanisms before making recommendations."),
]
x0, bw, gap = 0.7, 3.75, 0.35
for i, (badge, head, cap) in enumerate(why):
    x = x0 + i * (bw + gap)
    box(s, x, 3.55, bw, 0.65, badge, fc=GREEN, tcolor=WHITE, size=17, bold=True)
    text(s, x, 4.35, bw, 0.4, head, size=15, bold=True, color=DARK, align=PP_ALIGN.CENTER)
    text(s, x, 4.8, bw, 1.6, cap, size=12.5, color=GRAY, align=PP_ALIGN.CENTER, spacing=1.25)
pagenum(s, 8)

# ===================================================== 9. limitations / next
s = slide()
eyebrow(s, "PRESENTATION 3 SCOPE")
title(s, "Questions reserved for the final presentation")
stat_bullets(s, 0.7, 1.95, 11.9, 2.6, [
    ("Mechanism", DARK, "Why might students form academically useful links, and when would indirect reach matter?"),
    ("Incentives", GRAY, "Use a network-economics model to analyse link formation, information access, and peer effects."),
    ("Decision", GRAY, "Translate the final evidence into a cautious recommendation for a non-expert manager."),
], size=15, gap=14)
text(s, 0.7, 4.75, 11.9, 0.35,
     "Before then, the remaining empirical checks are incoming status and reciprocal ties; neither is significant in the current robustness results.",
     size=13, italic=True, color=GRAY)
figure(s, "fig_p2_reciprocal_ties.png", top=5.1, height=1.95)
pagenum(s, 9)

# ===================================================== 10. thanks
s = slide()
dec = s.shapes.add_picture(str(ROOT / "assets" / "decor_network.png"),
                            0, Inches(0.9), width=Inches(2.6))
dec.left = int(prs.slide_width - dec.width - Inches(0.5))
accent_bar(s, 0.55, 2.63, 0.95)
text(s, 0.9, 2.6, 11, 1.2, "Thank you", size=42, bold=True, color=DARK, font=HEAD)
text(s, 0.95, 4.0, 11, 0.6,
     "Presentation 3: network incentives, mechanism, and final recommendation.", size=15, color=GRAY)
text(s, 0.95, 6.4, 6, 0.5, "Questions?", size=16, bold=True, color=ORANGE)
pagenum(s, 10)

out = ROOT / "Presentation2.pptx"
prs.save(out)
print(f"Saved -> {out}  ({len(prs.slides._sldIdLst)} slides)")
