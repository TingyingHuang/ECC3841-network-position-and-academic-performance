"""
Build Presentation 1 (Week 6-7, 10 minutes): define the area/focus of the
project, what we're trying to understand, and how we plan to go about it.

Structure follows the instructor's feedback: build on a model and explain
it, derive predictions from the theory, THEN bring in data. No regression
results appear here -- those are Presentation 2's job.

Trimmed to 9 slides for a 10-minute talk (~1 min/slide): title -> the gap
in prior work -> puzzle+question -> theory (model) -> theory (equilibrium)
-> predictions -> data -> plan -> questions. Related-studies detail lives
in research_brief.pdf; mention it verbally if time allows.
"""
from pathlib import Path

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE, MSO_CONNECTOR
from pptx.oxml.ns import qn

ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / "assets"

BLUE = RGBColor(0x2A, 0x78, 0xD6)
ORANGE = RGBColor(0xEB, 0x68, 0x34)
DARK = RGBColor(0x19, 0x18, 0x0F)
GRAY_TEXT = RGBColor(0x55, 0x50, 0x3F)
LIGHT_BG = RGBColor(0xFA, 0xF9, 0xF6)
CARD_BG = RGBColor(0xF1, 0xEF, 0xE8)
BORDER = RGBColor(0xDD, 0xD8, 0xCD)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
BLUE_TINT = RGBColor(0xE9, 0xF0, 0xFA)

FONT_HEAD = "Georgia"
FONT_BODY = "Calibri"

prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)
BLANK = prs.slide_layouts[6]


def add_slide(bg_color=LIGHT_BG):
    slide = prs.slides.add_slide(BLANK)
    bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
    bg.fill.solid()
    bg.fill.fore_color.rgb = bg_color
    bg.line.fill.background()
    bg.shadow.inherit = False
    spTree = slide.shapes._spTree
    spTree.remove(bg._element)
    spTree.insert(2, bg._element)
    return slide


def add_text(slide, left, top, width, height, text, size=18, bold=False,
             color=DARK, font=FONT_BODY, align=PP_ALIGN.LEFT, italic=False,
             line_spacing=1.15, anchor=MSO_ANCHOR.TOP):
    box = slide.shapes.add_textbox(left, top, width, height)
    tf = box.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    lines = text.split("\n")
    for i, line in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = line
        p.alignment = align
        p.line_spacing = line_spacing
        for run in p.runs:
            run.font.size = Pt(size)
            run.font.bold = bold
            run.font.italic = italic
            run.font.color.rgb = color
            run.font.name = font
    return box


def add_bullets(slide, left, top, width, height, items, size=16, color=DARK,
                 font=FONT_BODY, space_after=10):
    box = slide.shapes.add_textbox(left, top, width, height)
    tf = box.text_frame
    tf.word_wrap = True
    for i, item in enumerate(items):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.space_after = Pt(space_after)
        p.line_spacing = 1.2
        run = p.add_run()
        run.text = "  •  " + item
        run.font.size = Pt(size)
        run.font.color.rgb = color
        run.font.name = font
    return box


def add_pagenum(slide, n, color=GRAY_TEXT):
    add_text(slide, Inches(12.5), Inches(7.08), Inches(0.7), Inches(0.35),
              str(n), size=11, color=color, align=PP_ALIGN.RIGHT)


def eyebrow(slide, text, color=ORANGE):
    add_text(slide, Inches(0.7), Inches(0.4), Inches(9), Inches(0.4), text,
              size=13, bold=True, color=color, font=FONT_BODY)


def title(slide, text, top=Inches(0.75), size=28, width=Inches(11.9), color=DARK):
    add_text(slide, Inches(0.7), top, width, Inches(1.0), text, size=size,
              bold=True, color=color, font=FONT_HEAD)


def rounded_box(slide, left, top, width, height, text, fill=WHITE,
                 text_color=DARK, size=14, bold=False, border=BORDER,
                 align=PP_ALIGN.CENTER, font=FONT_BODY):
    shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    shape.adjustments[0] = 0.12
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill
    shape.line.color.rgb = border
    shape.line.width = Pt(1.25)
    shape.shadow.inherit = False
    tf = shape.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    tf.margin_left = Inches(0.12)
    tf.margin_right = Inches(0.12)
    p = tf.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    run.text = text
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = text_color
    run.font.name = font
    return shape


def arrow(slide, x1, y1, x2, y2, color=GRAY_TEXT, width=Pt(2)):
    conn = slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, x1, y1, x2, y2)
    conn.line.color.rgb = color
    conn.line.width = width
    line = conn.line._get_or_add_ln()
    tail = line.makeelement(qn('a:tailEnd'), {'type': 'triangle', 'w': 'med', 'len': 'med'})
    line.append(tail)
    return conn


def add_eq(slide, fname, left, top, width):
    return slide.shapes.add_picture(str(ASSETS / fname), left, top, width=width)


# ============================================================= SLIDE 1 -- title
s = add_slide()
s.shapes.add_picture(str(ASSETS / "decor_network.png"), Inches(9.0), Inches(0.3), height=Inches(4.1))
add_text(s, Inches(0.9), Inches(2.1), Inches(11.5), Inches(0.5),
          "ECC3841 NETWORK ECONOMICS  ·  PRESENTATION 1",
          size=13, bold=True, color=ORANGE, font=FONT_BODY)
add_text(s, Inches(0.9), Inches(2.7), Inches(11.5), Inches(2.0),
          "Network Position and\nAcademic Performance",
          size=44, bold=True, color=DARK, font=FONT_HEAD, line_spacing=1.05)
add_text(s, Inches(0.9), Inches(4.55), Inches(11), Inches(0.7),
          "Extending Smirnov & Thurner (2017) with network centrality",
          size=19, color=GRAY_TEXT, italic=True, font=FONT_BODY)
add_text(s, Inches(0.9), Inches(6.5), Inches(9), Inches(0.5),
          "Team [names] · [Date]", size=13, color=GRAY_TEXT)

# ============================================================= SLIDE 2 -- the gap in prior work
s = add_slide()
eyebrow(s, "WHY THIS QUESTION  ·  PRIOR WORK")
title(s, "The gap in Smirnov & Thurner (2017)")
add_text(s, Inches(0.7), Inches(1.7), Inches(11.9), Inches(0.6),
          "Grades depend on more than effort — but how the social world around a student matters is still debated.",
          size=16, italic=True, color=GRAY_TEXT)

y = Inches(2.55)
bw, bh, gap = Inches(3.1), Inches(1.0), Inches(0.55)
x1 = Inches(0.9)
rounded_box(s, x1, y, bw, bh, "Friend selection", fill=WHITE, size=15, bold=True)
x2 = x1 + bw + gap
rounded_box(s, x2, y, bw, bh, "Friend-group GPA\nsimilarity", fill=WHITE, size=15, bold=True)
x3 = x2 + bw + gap
rounded_box(s, x3, y, bw, bh, "Observed homophily\nin GPA", fill=WHITE, size=15, bold=True)
arrow(s, x1 + bw, y + bh/2, x2, y + bh/2)
arrow(s, x2 + bw, y + bh/2, x3, y + bh/2)
add_text(s, Inches(0.9), Inches(3.85), Inches(11.3), Inches(0.5),
          "A real, changing “who-likes-who” network of Russian students, matched to GPA.",
          size=16, color=GRAY_TEXT)

add_text(s, Inches(0.9), Inches(4.6), Inches(11.3), Inches(1.4),
          "Their method asks one question: who is this student connected to, and what "
          "is the average GPA of those specific people? It never asks where a student "
          "sits inside the wider network.",
          size=16, color=GRAY_TEXT, line_spacing=1.35)
add_text(s, Inches(0.9), Inches(6.15), Inches(11.3), Inches(0.8),
          "→ Two students with identical friends get an identical score, no matter how "
          "different those friends' own social worlds are.",
          size=17, bold=True, color=ORANGE)

# ============================================================= SLIDE 3 -- puzzle + research question
s = add_slide()
eyebrow(s, "THE PUZZLE → OUR QUESTION")
title(s, "Same friends, same average friend GPA — same outcome?")
s.shapes.add_picture(str(ASSETS / "student_comparison.png"), Inches(2.4), Inches(1.7), width=Inches(8.5))
add_text(s, Inches(0.9), Inches(5.55), Inches(11.5), Inches(1.6),
          "Does your position in a friendship network affect your grades?",
          size=32, bold=True, color=DARK, font=FONT_HEAD, line_spacing=1.1, align=PP_ALIGN.CENTER)

# ============================================================= SLIDE 4 -- THEORY 1: the model
s = add_slide()
eyebrow(s, "THE MODEL", color=BLUE)
title(s, "Peer effects in effort choice")
add_text(s, Inches(0.7), Inches(1.85), Inches(11.9), Inches(0.6),
          "Calvó-Armengol, Patacchini & Zenou (2009); Ballester, Calvó-Armengol & Zenou (2006)",
          size=13, italic=True, color=GRAY_TEXT)

rounded_box(s, Inches(1.55), Inches(2.55), Inches(10.2), Inches(1.55), "", fill=CARD_BG)
add_eq(s, "eq_utility.png", Inches(2.35), Inches(2.7), Inches(8.6))

add_text(s, Inches(0.9), Inches(4.45), Inches(11.5), Inches(0.5),
          "Each student i chooses effort zᵢ. Two peer channels:",
          size=17, bold=True, color=DARK)
add_bullets(s, Inches(1.1), Inches(5.0), Inches(11.0), Inches(2.3), [
    "Private return to effort is concave — diminishing returns to studying alone (the  −½zᵢ²  term).",
    "μ scales the baseline value of simply having friends (μgᵢzᵢ); φ scales the strategic complementarity with friends' own effort (gᵢⱼ = 1 if i and j are linked).",
], size=16, color=GRAY_TEXT, space_after=14)

# ============================================================= SLIDE 5 -- THEORY 2: equilibrium
s = add_slide()
eyebrow(s, "THE MODEL", color=BLUE)
title(s, "Equilibrium effort = Katz-Bonacich centrality", size=28)

add_text(s, Inches(0.9), Inches(1.8), Inches(2.8), Inches(0.4), "Best response:", size=15, bold=True, color=GRAY_TEXT)
add_eq(s, "eq_foc.png", Inches(3.8), Inches(1.7), Inches(4.4))

add_text(s, Inches(0.9), Inches(3.05), Inches(2.8), Inches(0.4), "Nash equilibrium:", size=15, bold=True, color=GRAY_TEXT)
add_eq(s, "eq_equilibrium.png", Inches(3.8), Inches(2.85), Inches(6.3))

add_text(s, Inches(0.9), Inches(4.2), Inches(2.8), Inches(0.4), "Exists only if:", size=15, bold=True, color=GRAY_TEXT)
add_eq(s, "eq_condition.png", Inches(3.8), Inches(4.0), Inches(2.5))

rounded_box(s, Inches(0.9), Inches(5.1), Inches(11.5), Inches(2.0), "",
             fill=BLUE_TINT, border=BLUE)
add_text(s, Inches(1.25), Inches(5.3), Inches(10.9), Inches(1.65),
          "The theory's prediction is precise: equilibrium effort (and so, achievement) "
          "should be proportional to Katz-Bonacich centrality b(g,φ) — not to raw "
          "popularity, not to any other network measure. φ is exactly the decay "
          "parameter we test empirically. In the original paper's own AddHealth test, "
          "a 1-SD rise in centrality raised school performance by 7% of a SD.",
          size=15, color=DARK, line_spacing=1.3)

# ============================================================= SLIDE 6 -- predictions
s = add_slide()
eyebrow(s, "PREDICTIONS")
title(s, "What the theory — and the replication — predict")

rounded_box(s, Inches(0.7), Inches(1.75), Inches(11.5), Inches(0.5), "FROM THE MODEL",
             fill=BLUE, text_color=WHITE, size=13, bold=True, align=PP_ALIGN.LEFT)

card_w, card_h = Inches(11.5), Inches(1.05)
x0 = Inches(0.7)
rounded_box(s, x0, Inches(2.3), card_w, card_h, "", fill=WHITE, border=ORANGE)
add_text(s, x0 + Inches(0.3), Inches(2.42), Inches(0.8), Inches(0.8), "1", size=28, bold=True, color=ORANGE, font=FONT_HEAD)
add_text(s, x0 + Inches(1.2), Inches(2.42), card_w - Inches(1.5), Inches(0.8),
          "Katz-Bonacich centrality predicts GPA — even after we control for friend-group composition. The theory's core, falsifiable claim.",
          size=16, color=DARK, line_spacing=1.3)

add_text(s, Inches(0.95), Inches(3.55), Inches(7), Inches(0.4), "FROM REPLICATING SMIRNOV & THURNER", size=13, bold=True, color=GRAY_TEXT)

preds = [
    ("2", "A friend's past GPA will not predict a student's future GPA, once we control for their own past GPA."),
    ("3", "New friendships will show a smaller GPA gap than dropped friendships — a sign of selection."),
    ("4", "The selection effect will be stronger in university than high school (more freedom to change circles)."),
    ("5", "The model-implied centrality effect may differ by setting — worth testing high school vs. university."),
]
card_w2, card_h2 = Inches(5.6), Inches(1.25)
gap_x, gap_y = Inches(0.3), Inches(0.18)
x0b, y0b = Inches(0.7), Inches(4.0)
for i, (num, desc) in enumerate(preds):
    col, row = i % 2, i // 2
    x = x0b + col * (card_w2 + gap_x)
    y = y0b + row * (card_h2 + gap_y)
    rounded_box(s, x, y, card_w2, card_h2, "", fill=CARD_BG)
    add_text(s, x + Inches(0.2), y + Inches(0.12), Inches(0.6), Inches(0.6), num, size=20, bold=True, color=GRAY_TEXT, font=FONT_HEAD)
    add_text(s, x + Inches(0.8), y + Inches(0.12), card_w2 - Inches(1.0), Inches(1.0),
              desc, size=13.5, color=DARK, line_spacing=1.25)

# ============================================================= SLIDE 7 -- data
s = add_slide()
eyebrow(s, "THE DATA")
title(s, "A real, directed friendship network")
s.shapes.add_picture(str(ASSETS / "real_network_school.png"), Inches(5.9), Inches(1.55), height=Inches(5.6))

add_text(s, Inches(0.7), Inches(1.85), Inches(4.9), Inches(0.4), "NODES", size=14, bold=True, color=BLUE)
add_text(s, Inches(0.7), Inches(2.25), Inches(4.9), Inches(1.0),
          "Individual students — 655 high-school; 1,200–1,549 per university class-year",
          size=14, color=DARK, line_spacing=1.3)

add_text(s, Inches(0.7), Inches(3.15), Inches(4.9), Inches(0.4), "EDGES", size=14, bold=True, color=ORANGE)
add_text(s, Inches(0.7), Inches(3.55), Inches(4.9), Inches(1.3),
          "Directed “like” ties, 2–14 snapshots per group (38 total). Only 24–27% go both ways.",
          size=14, color=DARK, line_spacing=1.3)

add_text(s, Inches(0.7), Inches(4.75), Inches(4.9), Inches(0.4), "ATTRIBUTES", size=14, bold=True, color=DARK)
add_text(s, Inches(0.7), Inches(5.15), Inches(4.9), Inches(1.3),
          "GPA (outcome); in/out-degree, Katz-Bonacich, betweenness, eigenvector; high school vs. university.",
          size=14, color=DARK, line_spacing=1.3)

add_text(s, Inches(0.7), Inches(6.55), Inches(4.9), Inches(0.6),
          "485 students · 3,186 ties, one real snapshot — colour = GPA, size = popularity",
          size=12.5, italic=True, color=GRAY_TEXT)

# ============================================================= SLIDE 8 -- our plan
s = add_slide()
eyebrow(s, "OUR PLAN")
title(s, "Three layers of analysis")

y = Inches(2.2)
bw, bh, gap = Inches(3.5), Inches(1.5), Inches(0.55)
labels = [
    ("LAYER 1", "Replicate", "Rebuild Smirnov & Thurner's\nselection-vs-influence checks\non the same data"),
    ("LAYER 2", "Test the model", "Compute Katz-Bonacich\ncentrality; test the theory's\nprediction against the data"),
    ("LAYER 3", "Compare", "Split high school vs.\nuniversity; test whether the\neffect holds across settings"),
]
x = Inches(0.7)
xs = []
for tag, head, desc in labels:
    xs.append(x)
    rounded_box(s, x, y, bw, bh, "", fill=WHITE)
    add_text(s, x + Inches(0.25), y + Inches(0.12), bw - Inches(0.5), Inches(0.3), tag, size=13, bold=True, color=ORANGE)
    add_text(s, x + Inches(0.25), y + Inches(0.42), bw - Inches(0.5), Inches(0.45), head, size=19, bold=True, color=DARK, font=FONT_HEAD)
    x += bw + gap
for i in range(2):
    arrow(s, xs[i] + bw, y + bh/2, xs[i+1], y + bh/2)

x = Inches(0.7)
for tag, head, desc in labels:
    add_text(s, x, y + bh + Inches(0.35), bw, Inches(1.6), desc, size=14, color=GRAY_TEXT, line_spacing=1.3)
    x += bw + gap

add_text(s, Inches(0.7), Inches(5.7), Inches(11.5), Inches(0.7),
          "Deliberately conservative: we pre-register our main test before exploring "
          "further, so later robustness checks can't be accused of cherry-picking.",
          size=15, italic=True, color=GRAY_TEXT)

rounded_box(s, Inches(0.7), Inches(6.55), Inches(11.5), Inches(0.55), "",
             fill=CARD_BG, border=BORDER)
add_text(s, Inches(0.95), Inches(6.62), Inches(11.0), Inches(0.4),
          "Also grounded in: AddHealth peer effects (IZA DP 3859) · Giulietti, Vlassopoulos & Zenou (2020) on peer depression",
          size=12.5, italic=True, color=GRAY_TEXT)

# ============================================================= SLIDE 9 -- questions
s = add_slide()
add_text(s, Inches(0.9), Inches(2.9), Inches(11), Inches(1.2), "Questions?", size=44, bold=True, color=DARK, font=FONT_HEAD)
add_text(s, Inches(0.9), Inches(4.1), Inches(10), Inches(0.6),
          "Data: Smirnov & Thurner (2017), Harvard Dataverse doi:10.7910/DVN/SZA9YW",
          size=15, color=GRAY_TEXT)
add_text(s, Inches(0.9), Inches(4.6), Inches(10), Inches(0.6),
          "Model: Calvó-Armengol, Patacchini & Zenou (2009), Review of Economic Studies",
          size=15, color=GRAY_TEXT)

for i, slide_i in enumerate(prs.slides, start=1):
    add_pagenum(slide_i, i)

out_path = ROOT / "Presentation1.pptx"
prs.save(out_path)
print(f"Saved -> {out_path}  ({len(prs.slides._sldIdLst)} slides)")
