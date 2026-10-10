"""Puts the final Presentation 3 content into Amy's Canva export, keeping her page design.

Her slides that carry over (title, recap, models, Model 2 takeaway, result chart, core
question, literature, limitations, conclusion, thank-you, references) are edited in place:
same boxes, fonts and positions, new text. Content she does not have (the replication
slide, Model 1, the Model 2 and Model 3 games, Model 3 on our data, use 3 and the manager
decision) is copied in from build_deck.py built at her slide size (P3_SCALE=1.5).
Her slides 4, 5, 7, 9 and 13 are replaced by those richer versions.

Usage:
  P3_SCALE=1.5 P3_DECK_OUT=/tmp/deck_x15.pptx python3 presentation/build_deck.py
  python3 presentation/merge_into_canva_deck.py <canva.pptx> /tmp/deck_x15.pptx <out.pptx>
"""
import copy
import sys
from pathlib import Path

from pptx import Presentation
from pptx.util import Emu, Inches

sys.path.insert(0, str(Path(__file__).resolve().parent))
from p3_results import load_results, pct, pval  # noqa: E402

R = load_results()


def shape(slide, name):
    for sh in slide.shapes:
        if sh.name == name:
            return sh
        if sh.shape_type == 6:
            for c in sh.shapes:
                if c.name == name:
                    return c
    raise KeyError(name)


def set_text(slide, name, value):
    """Replace a text box's text, keeping the first run's formatting; '\\n' starts a new paragraph."""
    tf = shape(slide, name).text_frame
    paras = tf.paragraphs
    first = paras[0]
    runs = first.runs
    for r in runs[1:]:
        r._r.getparent().remove(r._r)
    for p in paras[1:]:
        p._p.getparent().remove(p._p)
    lines = value.split("\n")
    runs[0].text = lines[0]
    for line in lines[1:]:
        new = copy.deepcopy(first._p)
        tf._txBody.append(new)
        rs = new.findall(".//{http://schemas.openxmlformats.org/drawingml/2006/main}r")
        for extra in rs[1:]:
            extra.getparent().remove(extra)
        if rs:
            rs[0].find("{http://schemas.openxmlformats.org/drawingml/2006/main}t").text = line
        else:  # empty paragraph template: copy the first run in
            new.append(copy.deepcopy(runs[0]._r))
            new.findall(".//{http://schemas.openxmlformats.org/drawingml/2006/main}t")[0].text = line


def copy_in(dst, src_slide):
    """Append a copy of a generated slide (no pictures or links) to dst."""
    s = dst.slides.add_slide(dst.slide_layouts[6])
    for ph in list(s.placeholders):
        ph._element.getparent().remove(ph._element)
    s.background.fill.solid()
    s.background.fill.fore_color.rgb = src_slide.background.fill.fore_color.rgb
    tree = s.shapes._spTree
    for el in src_slide.shapes._spTree:
        if el.tag.endswith("}nvGrpSpPr") or el.tag.endswith("}grpSpPr"):
            continue
        tree.append(copy.deepcopy(el))
    return s


def clone(slide, name):
    """Copy a shape on the same slide, with fresh shape ids so PowerPoint does not ask to repair."""
    el = copy.deepcopy(shape(slide, name)._element)
    used = [int(x) for x in slide.shapes._spTree.xpath(".//p:cNvPr/@id")]
    for i, c in enumerate(el.xpath(".//p:cNvPr")):
        c.set("id", str(max(used) + 1 + i))
    slide.shapes._spTree.append(el)
    return slide.shapes[-1]


def main(canva, generated, out):
    A, G = Presentation(canva), Presentation(generated)
    a = list(A.slides)
    g = list(G.slides)

    # ---- recap: the numbers Presentation 2 actually showed ----------------------
    s = a[1]
    for lab, val, sub, (nl, nv, ns) in [
            ("BASELINE", f"{R['own_gpa']:.3f}", "own past GPA, p < 0.001", ("TextBox 8", "TextBox 9", "TextBox 10")),
            ("CONTACTS' PAST GPA", pval(R["contact_p"]), "no effect on later GPA", ("TextBox 13", "TextBox 14", "TextBox 15")),
            ("POOLED KATZ", f"{R['pooled_katz']:+.3f}", f"→ {R['pooled_katz_ctrl']:+.3f} once\ndirect links counted", ("TextBox 18", "TextBox 19", "TextBox 20")),
            ("SCHOOL PANEL, KATZ", f"{R['katz_full'].coef:+.3f}", f"beyond direct links\n{pval(R['katz_full'].pval)}", ("TextBox 23", "TextBox 24", "TextBox 25"))]:
        set_text(s, nl, lab); set_text(s, nv, val); set_text(s, ns, sub)
    set_text(s, "TextBox 30", "P1's prediction, that Katz reach matters beyond direct friends, did not hold. "
                              "So: what can a school still use its students' friendship network for?")

    # ---- models: two cards become three ----------------------------------------
    s = a[2]
    set_text(s, "TextBox 2", "Three course models, three possible uses")
    # card frames: her 5.7-inch-wide frame from the 'selection' slide, so corners keep their shape
    frame = shape(a[5], "Group 6")._element
    tree = s.shapes._spTree
    for old in ("Group 5", "Group 10"):
        el = shape(s, old)._element
        el.getparent().remove(el)
    next_id = max(int(x) for x in tree.xpath(".//p:cNvPr/@id")) + 1
    for i in range(3):
        el = copy.deepcopy(frame)
        for c in el.xpath(".//p:cNvPr"):
            c.set("id", str(next_id)); next_id += 1
        tree.insert(2 + i, el)
        sh = [x for x in s.shapes if x._element is el][0]
        sh.left, sh.top = Inches(1.2 + i * 6.2), Inches(2.84)
    card3 = [clone(s, n) for n in ("TextBox 12", "TextBox 13", "TextBox 14")]
    for i, names in enumerate([("TextBox 7", "TextBox 8", "TextBox 9"), ("TextBox 12", "TextBox 13", "TextBox 14"), None]):
        x = 1.2 + i * 6.2 + 0.45
        for sh in (card3 if names is None else [shape(s, n) for n in names]):
            sh.left, sh.width = Inches(x), Inches(4.9)
    texts = [("MODEL 1 · EFFORT GAME & KATZ", "Flag students who\nneed support?",
              "Lectures 1, 3, 7. Effort follows Katz-Bonacich centrality. Tested against friend counts in our school panel."),
             ("MODEL 2 · NETWORK FORMATION", "Organise\nstudy groups?",
              "Pairwise stability (Topic 2), homophily and Schelling (Topic 8). Tested on which ties form and which break."),
             ("MODEL 3 · THRESHOLD CONTAGION", "Spread a\nstudy habit?",
              "Majority game (Lecture 3), complex contagion (Topic 8). Simulated on our real networks.")]
    for (kick, head, body), names in zip(texts, [("TextBox 7", "TextBox 8", "TextBox 9"),
                                                  ("TextBox 12", "TextBox 13", "TextBox 14")]):
        set_text(s, names[0], kick); set_text(s, names[1], head); set_text(s, names[2], body)
    kick_sh, head_sh, body_sh = card3
    for sh, val in zip((kick_sh, head_sh, body_sh), texts[2]):
        tf = sh.text_frame
        tmp_name = sh.name
        sh.name = "__card3__"
        set_text(s, "__card3__", val)
        sh.name = tmp_name
    set_text(s, "TextBox 19", "Each model: the incentive, a small example, how it maps onto our data, the result, and what a school should do.")

    # ---- Model 2 takeaway + use 2 ----------------------------------------------
    s = a[5]
    set_text(s, "TextBox 2", "MODEL 2 · TAKEAWAY, AND USE 2")
    set_text(s, "TextBox 9", "Similar students keep re-matching, term after term, in every cohort and most of all among freshmen: selection, not influence.")
    set_text(s, "TextBox 12", "Explains why position adds little")
    set_text(s, "TextBox 13", "A well-connected student mostly reaches similar-GPA peers, so position mostly mirrors grades the student already has.")
    set_text(s, "TextBox 16", "Use 2: design study groups, early")
    set_text(s, "TextBox 17", "Mixing won't happen by itself. Form mixed-ability groups in first year. Lecture 7 (Bangladesh RCT): friendship groups with a cap on the group's average score raised scores.")

    # ---- Model 3 result chart ---------------------------------------------------
    s = a[7]
    set_text(s, "TextBox 2", "MODEL 3 · RESULT")
    set_text(s, "TextBox 8", "Highest Katz")
    set_text(s, "TextBox 11", "Most active")
    set_text(s, "TextBox 143", "Share of students who end up adopting (%), starting with 3% of students, 300 simulations per point. Easy habit (r = 1): spreads anyway. Hard habit (r ≥ 4): barely spreads.")

    # ---- answering the core question --------------------------------------------
    s = a[9]
    set_text(s, "TextBox 8", "Does position predict grades?")
    set_text(s, "TextBox 9", f"Barely: about {100 * R['sd_katz']:.1f}% of a GPA s.d., and in this sparse network Katz reach can't be told apart from friend count.")
    set_text(s, "TextBox 12", "Why the network looks like this")
    set_text(s, "TextBox 13", "Students choose friends with similar grades, most of all in first year. The network reflects grades; it doesn't drive them.")
    set_text(s, "TextBox 16", "What the network is for")
    set_text(s, "TextBox 17", "Organising study groups a school designs, and spreading habits of middle difficulty through active students.")
    set_text(s, "TextBox 22", "Course question: network structure explains why friends' grades look alike (selection) and decides who adopts a new habit (thresholds).")

    # ---- limitations ------------------------------------------------------------
    s = a[10]
    set_text(s, "TextBox 8", "Prediction, not cause")
    set_text(s, "TextBox 11", "Students who name more friends may also be more motivated. A stronger test would use random assignment or a natural experiment.")
    set_text(s, "TextBox 14", "Katz vs friend count")
    set_text(s, "TextBox 17", f"They correlate at {R['corr_katz_out']:.2f} here, so our network cannot separate them.")
    set_text(s, "TextBox 20", "Cohorts and simulation")
    set_text(s, "TextBox 23", "The first-year pattern compares different cohorts; the simulation uses equal thresholds and one snapshot, and its best rule depends on the number of starters.")

    # ---- literature ---------------------------------------------------------------
    s = a[11]
    set_text(s, "TextBox 12", "Randomly assigned Dartmouth roommates and peer effects in GPA.\n\nRelevance: random exposure would support a causal reading; our friendships are chosen.")
    set_text(s, "TextBox 16", "Lecture 7: Katz-Bonacich centrality predicts US students' grades better than degree.\n\nRelevance: our students name far fewer friends, so Katz ≈ friend count here.")

    # ---- conclusion ---------------------------------------------------------------
    s = a[13]
    set_text(s, "TextBox 6", "A disciplined empirical result, a model-based explanation for it, and three practical uses.")
    set_text(s, "TextBox 10", "Does network position shape academic performance? The effort game predicts Katz should matter.")
    set_text(s, "TextBox 14", "A small, mostly direct-link-driven association; Katz adds nothing beyond direct links.")
    set_text(s, "TextBox 17", "P3 – USE")
    set_text(s, "TextBox 18", "Target support by grades; design study groups early; seed habits through active students.")

    # ---- references (appendix) ----------------------------------------------------
    s = a[14]
    set_text(s, "TextBox 3", "These sources frame the models and the identification challenge; all results are from our own data and simulations.")
    set_text(s, "TextBox 6", "Data & peer effects")
    set_text(s, "TextBox 7", "Smirnov, I., & Thurner, S. (2017). Formation of homophily in academic performance. PLOS ONE, 12(8), e0183473.\n\n"
                             "Manski, C. F. (1993). Identification of endogenous social effects: the reflection problem. Review of Economic Studies, 60(3), 531–542.\n\n"
                             "Sacerdote, B. (2001). Peer effects with random assignment. Quarterly Journal of Economics, 116(2), 681–704.")
    set_text(s, "TextBox 10", "Games on networks")
    set_text(s, "TextBox 11", "Ballester, C., Calvó-Armengol, A., & Zenou, Y. (2006). Who's who in networks. Econometrica, 74(5), 1403–1417.\n\n"
                              "Calvó-Armengol, A., Patacchini, E., & Zenou, Y. (2009). Peer effects and social networks in education. Review of Economic Studies, 76(4), 1239–1267.")
    set_text(s, "TextBox 14", "Contagion")
    set_text(s, "TextBox 15", "Granovetter, M. (1978). Threshold models of collective behavior. American Journal of Sociology, 83(6), 1420–1443.\n\n"
                              "Watts, D. J. (2002). A simple model of global cascades on random networks. PNAS, 99(9), 5766–5771.")
    set_text(s, "TextBox 16", "Appendix: references motivate the theoretical discussion; the results are based on our own network data and simulations.")

    # ---- thank you + contributions -----------------------------------------------
    s = a[15]
    set_text(s, "TextBox 3", "Team contributions:")
    set_text(s, "TextBox 4", "Amy Bing: [contribution]\nTingying Huang: [contribution]")

    # ---- insert generated slides, drop the replaced ones, set the order ------------
    new = {k: copy_in(A, g[k - 1]) for k in (4, 5, 6, 7, 8, 10, 11, 13, 14)}
    order = [a[0], a[1], a[2], new[4], new[5], new[6], new[7], new[8], a[5], new[10], new[11],
             a[7], new[13], new[14], a[9], a[11], a[10], a[13], a[15], a[14]]
    lst = A.slides._sldIdLst
    ids = {sl.slide_id: el for sl, el in zip(A.slides, list(lst))}
    order_ids = [sl.slide_id for sl in order]
    for sid, el in list(ids.items()):
        lst.remove(el)
        if sid not in order_ids:
            A.part.drop_rel(el.rId)
    for sid in order_ids:
        lst.append(ids[sid])

    # ---- page numbers follow the final order; none on title, thank-you, appendix ----
    for k, sl in enumerate(A.slides):
        for sh in sl.shapes:
            if sh.has_text_frame and Emu(sh.left).inches > 18 and Emu(sh.top).inches > 10.2 and sh.text_frame.text.strip().isdigit():
                runs = sh.text_frame.paragraphs[0].runs
                runs[0].text = str(k) if 0 < k < len(order) - 2 else ""
    A.save(out)
    print(out, len(A.slides), "slides")


if __name__ == "__main__":
    main(*sys.argv[1:4])
