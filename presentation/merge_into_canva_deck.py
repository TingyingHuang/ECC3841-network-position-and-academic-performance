"""Puts the final Presentation 3 content into Amy's Canva export, keeping her page design.

The final deck has 15 slides and ends on team contributions, as the project brief requires.
Her slides that carry over (title, recap, models, Model 2 takeaway, result chart, core
question, thank-you) are edited in place: same boxes, fonts and positions, new text.
Content she does not have (Model 1, the Model 2 and Model 3 games, Model 2 on our data,
use 3 and the manager decision) is copied in from build_deck.py built at her slide size
(P3_SCALE=1.5). Her result chart and title-page network are also replaced: Canva exports
their lines as rotated or flipped shapes, which lose their direction when re-imported. Her other slides (old Model 1/2 setup and evidence, literature,
limitations, conclusion, references) are dropped: they repeat other slides or are not
required for Presentation 3.

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


A_NS = "{http://schemas.openxmlformats.org/drawingml/2006/main}"


def unscale_groups(slide):
    """Canva stores frames, underlines and callouts as groups drawn at 0.75 scale
    (ext != chExt). Some viewers (Quick Look, Keynote) then drop the shapes. Apply each
    group's scale to its children so every group draws at 1:1; the look is unchanged."""
    def fix(grp):
        x = grp.find(f"{A_NS}xfrm") if grp.tag.endswith("grpSpPr") else None
        if x is None:
            return
        off, ext, choff, chext = (x.find(f"{A_NS}{t}") for t in ("off", "ext", "chOff", "chExt"))
        if None in (off, ext, choff, chext):
            return
        sx = int(ext.get("cx")) / max(1, int(chext.get("cx")))
        sy = int(ext.get("cy")) / max(1, int(chext.get("cy")))
        ox, oy, cx0, cy0 = int(off.get("x")), int(off.get("y")), int(choff.get("x")), int(choff.get("y"))
        for child in grp.getparent():
            pr = child.find(f"{{http://schemas.openxmlformats.org/presentationml/2006/main}}spPr")
            if pr is None:
                pr = child.find(f"{{http://schemas.openxmlformats.org/presentationml/2006/main}}grpSpPr")
            cx = pr.find(f"{A_NS}xfrm") if pr is not None else None
            if cx is None or cx.find(f"{A_NS}off") is None:
                continue
            co, ce = cx.find(f"{A_NS}off"), cx.find(f"{A_NS}ext")
            co.set("x", str(round(ox + (int(co.get("x")) - cx0) * sx)))
            co.set("y", str(round(oy + (int(co.get("y")) - cy0) * sy)))
            ce.set("cx", str(round(int(ce.get("cx")) * sx)))
            ce.set("cy", str(round(int(ce.get("cy")) * sy)))
        choff.set("x", off.get("x")); choff.set("y", off.get("y"))
        chext.set("cx", ext.get("cx")); chext.set("cy", ext.get("cy"))
    # outermost groups first, so nested groups see their final position before being fixed
    groups = [g for g in slide.shapes._spTree.iter(f"{{http://schemas.openxmlformats.org/presentationml/2006/main}}grpSpPr")
              if g.getparent() is not slide.shapes._spTree]
    for g in sorted(groups, key=lambda e: len(list(e.iterancestors()))):
        fix(g)


def ungroup(slide):
    """After unscale_groups every group draws 1:1, so its children already carry slide
    coordinates. Lift them out of the group; some viewers (Quick Look) skip grouped shapes."""
    P = "{http://schemas.openxmlformats.org/presentationml/2006/main}"
    tree = slide.shapes._spTree
    while True:
        groups = [g for g in tree.iter(f"{P}grpSp")]
        if not groups:
            return
        g = groups[0]
        parent, idx = g.getparent(), g.getparent().index(g)
        kids = [c for c in g if not c.tag.endswith("}nvGrpSpPr") and not c.tag.endswith("}grpSpPr")]
        parent.remove(g)
        for j, c in enumerate(kids):
            parent.insert(idx + j, c)


def normalise_paths(slide):
    """Canva writes freeform paths in a coordinate box (w, h) larger than the shape itself.
    That is valid, but some viewers then skip the shape. Rescale each path to the shape's
    own size; the drawing is identical."""
    for path in slide.shapes._spTree.iter(f"{A_NS}path"):
        xfrm = path.getparent().getparent().getparent().find(f"{A_NS}xfrm")
        if xfrm is None or xfrm.find(f"{A_NS}ext") is None or not path.get("w") or not path.get("h"):
            continue
        ext = xfrm.find(f"{A_NS}ext")
        W, H, pw, ph = int(ext.get("cx")), int(ext.get("cy")), int(path.get("w")), int(path.get("h"))
        if (pw, ph) == (W, H) or not pw or not ph:
            continue
        fx, fy = W / pw, H / ph
        for pt in path.iter(f"{A_NS}pt"):
            pt.set("x", str(round(int(pt.get("x")) * fx))); pt.set("y", str(round(int(pt.get("y")) * fy)))
        for arc in path.iter(f"{A_NS}arcTo"):
            if arc.get("wR"): arc.set("wR", str(round(int(arc.get("wR")) * fx)))
            if arc.get("hR"): arc.set("hR", str(round(int(arc.get("hR")) * fy)))
        path.set("w", str(W)); path.set("h", str(H))
    # Canva leaves a stock image behind some callouts at 0% opacity; some viewers ignore the
    # opacity and show it, so replace those fills with no fill (the look in Canva is the same)
    for blip_fill in list(slide.shapes._spTree.iter(f"{A_NS}blipFill")):
        amt = blip_fill.xpath("./a:blip/a:alphaModFix/@amt")
        if amt and int(amt[0]) == 0:
            blip_fill.addprevious(blip_fill.makeelement(f"{A_NS}noFill", {}))
            blip_fill.getparent().remove(blip_fill)
    for xfrm in slide.shapes._spTree.iter(f"{A_NS}xfrm"):  # Canva writes flipH="false"; drop the no-ops
        for k in ("flipH", "flipV"):
            if xfrm.get(k) in ("false", "0"):
                del xfrm.attrib[k]


def main(canva, generated, out):
    A, G = Presentation(canva), Presentation(generated)
    a = list(A.slides)
    g = list(G.slides)

    # ---- title: keep her text, replace the network drawing (right of 12.5 in) ----
    s = a[0]
    for sh in list(s.shapes):
        if Emu(sh.left).inches >= 12.5:
            sh._element.getparent().remove(sh._element)
    used = max(int(x) for x in s.shapes._spTree.xpath(".//p:cNvPr/@id"))
    for sh in g[0].shapes:
        if Emu(sh.left).inches >= 12.5:
            el = copy.deepcopy(sh._element)
            for c in el.xpath(".//p:cNvPr"):
                used += 1; c.set("id", str(used))
            s.shapes._spTree.append(el)

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
    set_text(s, "TextBox 8", "Explains P2's baseline")
    set_text(s, "TextBox 9", "Contacts' GPA added nothing in P2 because friends are chosen for similar grades: selection, not influence.")
    set_text(s, "TextBox 12", "Explains why position adds little")
    set_text(s, "TextBox 13", "A well-connected student mostly reaches similar-GPA peers, so position mostly mirrors grades the student already has.")
    set_text(s, "TextBox 16", "Use 2: design study groups, early")
    set_text(s, "TextBox 17", "Mixing won't happen by itself. Form mixed-ability groups in first year. Lecture 7 (Bangladesh RCT): ability-balanced groups raised scores, friendship groups most. Advice: let friends group, but cap each group's average score.")

    # ---- answering the core question --------------------------------------------
    s = a[9]
    set_text(s, "TextBox 8", "What structure explains")
    set_text(s, "TextBox 9", "Why friends' grades look alike: students choose similar friends (Model 2), rather than peers raising effort (Model 1).")
    set_text(s, "TextBox 12", "What structure decides")
    set_text(s, "TextBox 13", "Who adopts a new habit: each student waits for enough adopting friends, so who starts and who is isolated matter (Model 3).")
    set_text(s, "TextBox 16", "What we cannot claim")
    set_text(s, "TextBox 17", "Causes: these are predictions. And in this sparse network, Katz reach and friend count cannot be separated.")
    set_text(s, "TextBox 22", "Our answer to P1: position follows grades more than grades follow position.")

    # ---- thank you + contributions -----------------------------------------------
    s = a[15]
    set_text(s, "TextBox 3", "Team contributions:")
    set_text(s, "TextBox 4", "Amy Bing: [contribution]\nTingying Huang: [contribution]")

    # ---- insert generated slides, drop the replaced ones, set the order ------------
    new = {k: copy_in(A, g[k - 1]) for k in (4, 5, 6, 7, 8, 10, 11, 12, 13)}
    order = [a[0], a[1], a[2], new[4], new[5], new[6], new[7], new[8], a[5], new[10],
             new[11], new[12], new[13], a[9], a[15]]
    lst = A.slides._sldIdLst
    ids = {sl.slide_id: el for sl, el in zip(A.slides, list(lst))}
    order_ids = [sl.slide_id for sl in order]
    for sid, el in list(ids.items()):
        lst.remove(el)
        if sid not in order_ids:
            A.part.drop_rel(el.rId)
    for sid in order_ids:
        lst.append(ids[sid])

    for sl in order:
        unscale_groups(sl)
        ungroup(sl)
        normalise_paths(sl)

    # ---- page numbers follow the final order; none on the title or contributions slide ----
    for k, sl in enumerate(A.slides):
        for sh in sl.shapes:
            if sh.has_text_frame and Emu(sh.left).inches > 18 and Emu(sh.top).inches > 10.2 and sh.text_frame.text.strip().isdigit():
                runs = sh.text_frame.paragraphs[0].runs
                runs[0].text = str(k) if 0 < k < len(order) - 1 else ""
    A.save(out)
    print(out, len(A.slides), "slides")


if __name__ == "__main__":
    main(*sys.argv[1:4])
