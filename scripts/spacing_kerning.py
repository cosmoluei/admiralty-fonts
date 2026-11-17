"""
Milestone 3 Spacing, UFO Anchor Placement (mark/mkmk), and Class-Based Kerning
System (public.kern1.* / public.kern2.*) for Admiralty Sans Regular.
"""

from __future__ import annotations
from typing import Dict, List, Tuple
import ufoLib2

from glyphs_sans_latin_ext import COMPOSITE_RECIPES


# Optical X-centers & ogonek attachment points for base glyphs
BASE_ANCHORS: Dict[str, Dict[str, Tuple[float, float]]] = {
    "A": {"top": (318, 700), "bottom": (318, 0), "ogonek": (548, 0)},
    "AE": {"top": (560, 700), "bottom": (560, 0)},
    "B": {"top": (306, 700), "bottom": (318, 0)},
    "C": {"top": (356, 700), "bottom": (356, 0)},
    "D": {"top": (328, 700), "bottom": (328, 0)},
    "E": {"top": (302, 700), "bottom": (308, 0), "ogonek": (452, 0)},
    "F": {"top": (298, 700), "bottom": (128, 0)},
    "G": {"top": (358, 700), "bottom": (358, 0)},
    "Germandbls": {"top": (322, 700), "bottom": (322, 0)},
    "H": {"top": (340, 700), "bottom": (340, 0)},
    "I": {"top": (154, 700), "bottom": (154, 0), "ogonek": (166, 0)},
    "IJ": {"top": (380, 700), "bottom": (380, 0)},
    "J": {"top": (372, 700), "bottom": (224, 0)},
    "K": {"top": (318, 700), "bottom": (324, 0)},
    "L": {"top": (128, 700), "bottom": (290, 0)},
    "Ldot": {"top": (128, 700), "bottom": (290, 0)},
    "M": {"top": (408, 700), "bottom": (408, 0)},
    "N": {"top": (346, 700), "bottom": (346, 0)},
    "O": {"top": (342, 700), "bottom": (342, 0)},
    "OE": {"top": (580, 700), "bottom": (580, 0)},
    "Oslash": {"top": (342, 700), "bottom": (342, 0)},
    "P": {"top": (306, 700), "bottom": (128, 0)},
    "Q": {"top": (342, 700), "bottom": (342, 0)},
    "R": {"top": (306, 700), "bottom": (318, 0)},
    "S": {"top": (292, 700), "bottom": (282, 0)},
    "T": {"top": (292, 700), "bottom": (292, 0)},
    "Tbar": {"top": (292, 700), "bottom": (292, 0)},
    "U": {"top": (336, 700), "bottom": (336, 0), "ogonek": (416, 4)},
    "V": {"top": (306, 700), "bottom": (306, 0)},
    "W": {"top": (442, 700), "bottom": (442, 0)},
    "X": {"top": (302, 700), "bottom": (302, 0)},
    "Y": {"top": (292, 700), "bottom": (292, 0)},
    "Z": {"top": (292, 700), "bottom": (288, 0)},
    # Lowercase
    "a": {"top": (272, 520), "bottom": (264, 0), "ogonek": (436, 0)},
    "ae": {"top": (430, 520), "bottom": (430, 0)},
    "b": {"top": (118, 740), "bottom": (308, 0)},
    "c": {"top": (284, 520), "bottom": (284, 0)},
    "d": {"top": (458, 700), "bottom": (280, 0)},
    "e": {"top": (282, 520), "bottom": (288, 0), "ogonek": (396, 12)},
    "f": {"top": (236, 740), "bottom": (149, 0)},
    "g": {"top": (272, 520), "bottom": (260, -224)},
    "h": {"top": (119, 700), "bottom": (292, 0)},
    "i": {"top": (123, 710), "bottom": (123, 0), "ogonek": (132, 0)},
    "dotlessi": {"top": (123, 520), "bottom": (123, 0), "ogonek": (132, 0)},
    "j": {"top": (139, 710), "bottom": (52, -224)},
    "dotlessj": {"top": (139, 520), "bottom": (52, -224)},
    "k": {"top": (119, 700), "bottom": (288, 0)},
    "kgreenlandic": {"top": (258, 520), "bottom": (288, 0)},
    "l": {"top": (117, 700), "bottom": (146, 0)},
    "ldot": {"top": (117, 700), "bottom": (146, 0)},
    "longs": {"top": (228, 752), "bottom": (149, 0)},
    "m": {"top": (440, 520), "bottom": (440, 0)},
    "n": {"top": (298, 520), "bottom": (292, 0)},
    "o": {"top": (290, 520), "bottom": (290, 0)},
    "oe": {"top": (450, 520), "bottom": (450, 0)},
    "oslash": {"top": (290, 520), "bottom": (290, 0)},
    "p": {"top": (308, 520), "bottom": (117, -220)},
    "q": {"top": (268, 520), "bottom": (459, -220)},
    "r": {"top": (218, 520), "bottom": (119, 0)},
    "s": {"top": (242, 520), "bottom": (228, 0)},
    "t": {"top": (152, 700), "bottom": (228, 0)},
    "tbar": {"top": (152, 700), "bottom": (228, 0)},
    "u": {"top": (286, 520), "bottom": (286, 0), "ogonek": (460, 0)},
    "v": {"top": (252, 520), "bottom": (252, 0)},
    "w": {"top": (378, 520), "bottom": (378, 0)},
    "x": {"top": (250, 520), "bottom": (250, 0)},
    "y": {"top": (248, 520), "bottom": (116, -224)},
    "z": {"top": (238, 520), "bottom": (238, 0)},
}

MARK_ANCHORS: Dict[str, Dict[str, Tuple[float, float]]] = {
    "gravecomb": {"_top": (0, 520), "top": (0, 718)},
    "acutecomb": {"_top": (0, 520), "top": (0, 718)},
    "circumflexcomb": {"_top": (0, 520), "top": (0, 722)},
    "tildecomb": {"_top": (0, 520), "top": (0, 710)},
    "macroncomb": {"_top": (0, 520), "top": (0, 672)},
    "brevecomb": {"_top": (0, 520), "top": (0, 716)},
    "dotaccentcomb": {"_top": (0, 520), "top": (0, 690)},
    "dieresiscomb": {"_top": (0, 520), "top": (0, 690)},
    "ringabovecomb": {"_top": (0, 520), "top": (0, 744)},
    "hungarumlautcomb": {"_top": (0, 520), "top": (0, 718)},
    "caroncomb": {"_top": (0, 520), "top": (0, 722)},
    # Capital marks (compacted so 2-level Pinyin stacking <= 972u)
    "gravecomb.cap": {"_top": (0, 700), "top": (0, 860)},
    "acutecomb.cap": {"_top": (0, 700), "top": (0, 860)},
    "circumflexcomb.cap": {"_top": (0, 700), "top": (0, 862)},
    "tildecomb.cap": {"_top": (0, 700), "top": (0, 868)},
    "macroncomb.cap": {"_top": (0, 700), "top": (0, 808)},
    "brevecomb.cap": {"_top": (0, 700), "top": (0, 860)},
    "dotaccentcomb.cap": {"_top": (0, 700), "top": (0, 822)},
    "dieresiscomb.cap": {"_top": (0, 700), "top": (0, 816)},
    "ringabovecomb.cap": {"_top": (0, 700), "top": (0, 892)},
    "hungarumlautcomb.cap": {"_top": (0, 700), "top": (0, 860)},
    "caroncomb.cap": {"_top": (0, 700), "top": (0, 862)},
    # Bottom & ogonek marks
    "cedillacomb": {"_bottom": (0, 0), "bottom": (0, -206)},
    "commaaccentcomb": {"_bottom": (0, 0), "bottom": (0, -206)},
    "ogonekcomb": {"_ogonek": (0, 0)},
}


def attach_ufo_anchors_and_composites(ufo: ufoLib2.Font) -> None:
    """Attach base & mark anchors, then construct all precomposed European glyphs via UFO components."""
    for gname, adict in {**BASE_ANCHORS, **MARK_ANCHORS}.items():
        if gname not in ufo:
            continue
        g = ufo[gname]
        g.anchors = [
            ufoLib2.objects.Anchor(x=xy[0], y=xy[1], name=aname)
            for aname, xy in adict.items()
        ]

    glyph_order = list(ufo.lib.get("public.glyphOrder", []))
    for comp_name, uni, base_name, mark_name, anchor_name in COMPOSITE_RECIPES:
        base_g = ufo[base_name]
        mark_g = ufo[mark_name]

        # Special Czech/Slovak tall caron adjustments (dcaron, lcaron, tcaron use right-side apostrophe-caron
        # in traditional typography, or raised caron; here shifted cleanly right of ascender stem!)
        if comp_name in ("dcaron", "lcaron", "tcaron", "Lcaron"):
            dx_map = {"dcaron": 566, "lcaron": 224, "tcaron": 268, "Lcaron": 264}
            dy_map = {"dcaron": 16, "lcaron": 16, "tcaron": -16, "Lcaron": 0}
            w_override = {"dcaron": 656, "lcaron": 318, "tcaron": 354, "Lcaron": 544}
            dx, dy = dx_map[comp_name], dy_map[comp_name]
        else:
            w_override = {}
            b_anc = next(a for a in base_g.anchors if a.name == anchor_name)
            m_anc = next(a for a in mark_g.anchors if a.name == f"_{anchor_name}")
            dx = round(b_anc.x - m_anc.x)
            dy = round(b_anc.y - m_anc.y)

        g = ufo.newGlyph(comp_name)
        g.width = w_override.get(comp_name, base_g.width)
        if uni is not None:
            g.unicodes = [uni]

        # Flatten nested components so TTF/OTF emit depth-1 contour components only
        if base_g.components:
            for sub_c in base_g.components:
                g.components.append(
                    ufoLib2.objects.Component(baseGlyph=sub_c.baseGlyph, transformation=sub_c.transformation)
                )
        else:
            g.components.append(ufoLib2.objects.Component(baseGlyph=base_name, transformation=(1, 0, 0, 1, 0, 0)))
        g.components.append(ufoLib2.objects.Component(baseGlyph=mark_name, transformation=(1, 0, 0, 1, dx, dy)))

        # Propagate anchors onto composite glyph so runtime NFD stacking marks attach cleanly
        mark_out = {a.name: a for a in mark_g.anchors if not a.name.startswith("_")}
        prop_anchors = []
        for a in base_g.anchors:
            if comp_name not in ("dcaron", "lcaron", "tcaron", "Lcaron") and a.name == anchor_name and anchor_name in mark_out:
                m_out = mark_out[anchor_name]
                prop_anchors.append(
                    ufoLib2.objects.Anchor(x=round(dx + m_out.x), y=round(dy + m_out.y), name=a.name)
                )
            else:
                prop_anchors.append(ufoLib2.objects.Anchor(x=a.x, y=a.y, name=a.name))
        g.anchors = prop_anchors
        glyph_order.append(comp_name)

    ufo.lib["public.glyphOrder"] = glyph_order


def apply_class_kerning(ufo: ufoLib2.Font) -> None:
    """
    Build clean UFO v3 kerning groups (public.kern1.* = first/right-contour class,
    public.kern2.* = second/left-contour class) and populate class-based kerning.
    """
    # Map base letters to their right-side (kern1) and left-side (kern2) contour classes
    kern1_seed: Dict[str, List[str]] = {
        "A": ["A"],
        "B": ["B", "Germandbls"],
        "C": ["C"],
        "O": ["D", "O", "Q", "Oslash", "Eth", "Dcroat"],
        "E": ["E", "AE", "OE"],
        "F": ["F"],
        "G": ["G"],
        "H": ["H", "M", "N", "Hbar", "Eng"],
        "I": ["I"],
        "J": ["J", "U", "IJ"],
        "K": ["K", "X"],
        "L": ["L", "Lslash"],
        "P": ["P", "Thorn"],
        "R": ["R"],
        "S": ["S"],
        "T": ["T", "Tbar"],
        "V": ["V"],
        "W": ["W"],
        "Y": ["Y"],
        "Z": ["Z"],
        # Lowercase right-side classes
        "a": ["a", "d", "h", "m", "n", "u", "dotlessi", "hbar", "eng"],
        "o": ["b", "o", "p", "oslash", "thorn"],
        "c": ["c"],
        "e": ["e", "ae", "oe"],
        "f": ["f", "longs"],
        "g": ["g"],
        "q": ["q"],
        "j": ["j", "dotlessj"],
        "k": ["k", "x", "kgreenlandic"],
        "l": ["l", "lslash", "ldot"],
        "r": ["r"],
        "s": ["s"],
        "t": ["t", "tbar"],
        "v": ["v"],
        "w": ["w"],
        "y": ["y"],
        "z": ["z"],
        # Punctuation left-side triggers
        "quote_l": ["quoteleft", "quotedblleft"],
        "quote_r": ["quoteright", "quotedblright", "quotesingle", "quotedbl"],
        "hyphen": ["hyphen", "hyphentwo", "nonbreakinghyphen", "endash", "emdash"],
        "paren_l": ["parenleft", "bracketleft", "braceleft"],
        "paren_r": ["parenright", "bracketright", "braceright"],
    }

    kern2_seed: Dict[str, List[str]] = {
        "A": ["A", "AE"],
        "H": ["B", "D", "E", "F", "H", "K", "L", "M", "N", "P", "R", "Dcroat", "Thorn", "Germandbls", "Ldot", "Lslash", "Hbar", "Eng"],
        "O": ["C", "G", "O", "Q", "OE", "Oslash"],
        "I": ["I", "IJ"],
        "J": ["J"],
        "S": ["S"],
        "T": ["T", "Tbar"],
        "U": ["U"],
        "V": ["V"],
        "W": ["W"],
        "X": ["X"],
        "Y": ["Y"],
        "Z": ["Z"],
        # Lowercase left-side classes (j separated from n so qj/gj stay clear without crashing Tj!)
        "a": ["a", "ae"],
        "o": ["c", "d", "e", "g", "o", "q", "oe", "oslash", "eth", "dcroat"],
        "h": ["b", "h", "k", "l", "lslash", "ldot", "hbar", "thorn", "germandbls"],
        "n": ["i", "m", "n", "p", "r", "dotlessi", "eng", "kgreenlandic", "ij"],
        "j": ["j", "dotlessj"],
        "f": ["f", "longs"],
        "s": ["s"],
        "t": ["t", "tbar"],
        "u": ["u"],
        "v": ["v"],
        "w": ["w"],
        "x": ["x"],
        "y": ["y"],
        "z": ["z"],
        # Punctuation right-side receivers
        "period": ["period", "comma", "ellipsis", "quotesinglbase", "quotedblbase"],
        "colon": ["colon", "semicolon"],
        "quote_r": ["quoteright", "quotedblright", "quotesingle", "quotedbl"],
        "hyphen": ["hyphen", "hyphentwo", "nonbreakinghyphen", "endash", "emdash"],
        "paren_r": ["parenright", "bracketright", "braceright"],
    }

    # Propagate precomposed accented glyphs into their base letter's kerning classes
    # (excluding wide marks on narrow dotlessi/dotlessj from kern2['n'] to avoid cap-bar collisions!)
    wide_i_marks = {"circumflexcomb", "tildecomb", "macroncomb", "brevecomb", "dieresiscomb", "caroncomb"}
    base_to_k1 = {g: cls for cls, gs in kern1_seed.items() for g in gs}
    base_to_k2 = {g: cls for cls, gs in kern2_seed.items() for g in gs}

    for comp_name, _, base_name, mark_name, _ in COMPOSITE_RECIPES:
        if comp_name not in ufo:
            continue
        if base_name in base_to_k1:
            if not (base_name in ("dotlessi", "dotlessj", "i") and mark_name in wide_i_marks):
                c1 = base_to_k1[base_name]
                kern1_seed[c1].append(comp_name)
                base_to_k1[comp_name] = c1
        if base_name in base_to_k2:
            if not (base_name in ("dotlessi", "dotlessj", "i") and mark_name in wide_i_marks):
                c2 = base_to_k2[base_name]
                kern2_seed[c2].append(comp_name)
                base_to_k2[comp_name] = c2

    ufo.groups.clear()
    for cls_name, members in kern1_seed.items():
        valid = [m for m in members if m in ufo]
        if valid:
            ufo.groups[f"public.kern1.{cls_name}"] = valid
    for cls_name, members in kern2_seed.items():
        valid = [m for m in members if m in ufo]
        if valid:
            ufo.groups[f"public.kern2.{cls_name}"] = valid

    def k1(c: str) -> str:
        return f"public.kern1.{c}"

    def k2(c: str) -> str:
        return f"public.kern2.{c}"

    # Comprehensive optical class-kerning matrix (in 1000-UPM units)
    class_pairs: Dict[Tuple[str, str], int] = {
        # A- right edge
        (k1("A"), k2("O")): -22, (k1("A"), k2("T")): -56, (k1("A"), k2("U")): -18,
        (k1("A"), k2("V")): -52, (k1("A"), k2("W")): -42, (k1("A"), k2("Y")): -60,
        (k1("A"), k2("a")): -10, (k1("A"), k2("o")): -18, (k1("A"), k2("t")): -22,
        (k1("A"), k2("u")): -14, (k1("A"), k2("v")): -36, (k1("A"), k2("w")): -30,
        (k1("A"), k2("y")): -38, (k1("A"), k2("quote_r")): -54, (k1("A"), k2("hyphen")): -22,

        # B / C / O / D right edges
        (k1("B"), k2("A")): -14, (k1("B"), k2("T")): -18, (k1("B"), k2("V")): -20, (k1("B"), k2("Y")): -24,
        (k1("C"), k2("O")): -12, (k1("C"), k2("o")): -10, (k1("C"), k2("hyphen")): -18,
        (k1("O"), k2("A")): -22, (k1("O"), k2("T")): -20, (k1("O"), k2("V")): -20,
        (k1("O"), k2("W")): -16, (k1("O"), k2("X")): -22, (k1("O"), k2("Y")): -24,
        (k1("O"), k2("period")): -22,

        # F / P right edges
        (k1("F"), k2("A")): -48, (k1("F"), k2("O")): -12, (k1("F"), k2("J")): -32,
        (k1("F"), k2("a")): -28, (k1("F"), k2("o")): -30, (k1("F"), k2("n")): -14,
        (k1("F"), k2("s")): -24, (k1("F"), k2("u")): -16, (k1("F"), k2("period")): -66,
        (k1("F"), k2("colon")): -24,
        (k1("P"), k2("A")): -54, (k1("P"), k2("J")): -36, (k1("P"), k2("a")): -20,
        (k1("P"), k2("o")): -24, (k1("P"), k2("s")): -18, (k1("P"), k2("period")): -78,

        # K / L / R right edges
        (k1("K"), k2("O")): -26, (k1("K"), k2("a")): -14, (k1("K"), k2("o")): -22,
        (k1("K"), k2("u")): -16, (k1("K"), k2("v")): -20, (k1("K"), k2("w")): -18,
        (k1("K"), k2("y")): -20, (k1("K"), k2("hyphen")): -32,
        (k1("L"), k2("O")): -18, (k1("L"), k2("T")): -56, (k1("L"), k2("U")): -16,
        (k1("L"), k2("V")): -52, (k1("L"), k2("W")): -42, (k1("L"), k2("Y")): -60,
        (k1("L"), k2("v")): -32, (k1("L"), k2("w")): -26, (k1("L"), k2("y")): -34,
        (k1("L"), k2("quote_r")): -58, (k1("L"), k2("hyphen")): -34,
        (k1("R"), k2("O")): -16, (k1("R"), k2("T")): -22, (k1("R"), k2("V")): -22,
        (k1("R"), k2("W")): -18, (k1("R"), k2("Y")): -26, (k1("R"), k2("a")): -12,
        (k1("R"), k2("o")): -16, (k1("R"), k2("u")): -12, (k1("R"), k2("y")): -20,

        # T / V / W / Y overhanging capitals
        (k1("T"), k2("A")): -56, (k1("T"), k2("J")): -38, (k1("T"), k2("O")): -18,
        (k1("T"), k2("a")): -46, (k1("T"), k2("o")): -48, (k1("T"), k2("n")): -34,
        (k1("T"), k2("s")): -42, (k1("T"), k2("u")): -36, (k1("T"), k2("v")): -38,
        (k1("T"), k2("w")): -36, (k1("T"), k2("y")): -38, (k1("T"), k2("z")): -38,
        (k1("T"), k2("period")): -58, (k1("T"), k2("colon")): -38, (k1("T"), k2("hyphen")): -44,

        (k1("V"), k2("A")): -52, (k1("V"), k2("J")): -36, (k1("V"), k2("O")): -18,
        (k1("V"), k2("a")): -42, (k1("V"), k2("o")): -44, (k1("V"), k2("n")): -26,
        (k1("V"), k2("s")): -36, (k1("V"), k2("u")): -30, (k1("V"), k2("y")): -28,
        (k1("V"), k2("period")): -64, (k1("V"), k2("colon")): -32, (k1("V"), k2("hyphen")): -34,

        (k1("W"), k2("A")): -42, (k1("W"), k2("J")): -28, (k1("W"), k2("O")): -14,
        (k1("W"), k2("a")): -32, (k1("W"), k2("o")): -34, (k1("W"), k2("n")): -20,
        (k1("W"), k2("s")): -28, (k1("W"), k2("u")): -24, (k1("W"), k2("y")): -22,
        (k1("W"), k2("period")): -52, (k1("W"), k2("colon")): -26, (k1("W"), k2("hyphen")): -28,

        (k1("Y"), k2("A")): -60, (k1("Y"), k2("J")): -42, (k1("Y"), k2("O")): -22,
        (k1("Y"), k2("a")): -50, (k1("Y"), k2("o")): -52, (k1("Y"), k2("n")): -38,
        (k1("Y"), k2("s")): -44, (k1("Y"), k2("u")): -40, (k1("Y"), k2("period")): -68,
        (k1("Y"), k2("colon")): -40, (k1("Y"), k2("hyphen")): -46,

        # Lowercase optical pairs
        (k1("o"), k2("v")): -14, (k1("o"), k2("w")): -12, (k1("o"), k2("x")): -18,
        (k1("o"), k2("y")): -14, (k1("o"), k2("period")): -16,
        (k1("e"), k2("v")): -12, (k1("e"), k2("w")): -10, (k1("e"), k2("x")): -14,
        (k1("e"), k2("y")): -12,
        (k1("f"), k2("a")): -12, (k1("f"), k2("o")): -14, (k1("f"), k2("period")): -26,
        (k1("f"), k2("V")): 24, (k1("f"), k2("W")): 24, (k1("f"), k2("Y")): 24,
        (k1("f"), k2("quote_r")): 24, (k1("f"), k2("paren_r")): 20,
        (k1("g"), k2("j")): 24,
        # Review 2: pairs that touched or overlapped in the Bold styles (f + tall letter,
        # j after an opening bracket, doubled diagonals). Same values in Sans and Serif.
        (k1("f"), k2("h")): 22, (k1("f"), k2("H")): 24, (k1("f"), k2("I")): 24, (k1("f"), k2("T")): 28,
        (k1("paren_l"), k2("j")): 40, (k1("paren_r"), k2("j")): 16,
        (k1("q"), k2("j")): 52, (k1("q"), k2("f")): 30, (k1("j"), k2("j")): 12,
        (k1("f"), k2("X")): 32,
        (k1("V"), k2("V")): 14, (k1("W"), k2("W")): 12, (k1("Y"), k2("Y")): 14,
        (k1("V"), k2("W")): 12, (k1("W"), k2("V")): 12, (k1("Y"), k2("W")): 14, (k1("W"), k2("Y")): 12,
        (k1("a"), k2("z")): 8, (k1("l"), k2("z")): 8, (k1("V"), k2("Y")): 14, (k1("Y"), k2("V")): 14,
        (k1("v"), k2("v")): 10, (k1("w"), k2("w")): 10, (k1("v"), k2("w")): 10, (k1("w"), k2("v")): 10,
        (k1("y"), k2("y")): 8, (k1("v"), k2("y")): 8, (k1("y"), k2("v")): 8,
        (k1("k"), k2("o")): -16, (k1("k"), k2("e")): -16,
        (k1("r"), k2("a")): -12, (k1("r"), k2("o")): -16, (k1("r"), k2("s")): -10,
        (k1("r"), k2("period")): -46, (k1("r"), k2("hyphen")): -20,
        (k1("t"), k2("o")): -8, (k1("t"), k2("y")): -12,
        (k1("v"), k2("a")): -16, (k1("v"), k2("o")): -18, (k1("v"), k2("period")): -46,
        (k1("w"), k2("a")): -14, (k1("w"), k2("o")): -16, (k1("w"), k2("period")): -40,
        (k1("y"), k2("a")): -14, (k1("y"), k2("o")): -18, (k1("y"), k2("period")): -48,

        # Quotes & Dashes
        (k1("quote_l"), k2("A")): -50, (k1("quote_l"), k2("J")): -36,
        (k1("quote_r"), k2("A")): -50, (k1("quote_r"), k2("s")): -18,
        (k1("hyphen"), k2("A")): -22, (k1("hyphen"), k2("T")): -44,
        (k1("hyphen"), k2("V")): -34, (k1("hyphen"), k2("W")): -28,
        (k1("hyphen"), k2("Y")): -46,
    }

    ufo.kerning.clear()
    for pair, val in class_pairs.items():
        if pair[0] in ufo.groups and pair[1] in ufo.groups:
            ufo.kerning[pair] = val
    # Review 3: Q is in the round-capital class, but its tail needs room before j
    if "Q" in ufo and k2("j") in ufo.groups:
        ufo.kerning[("Q", k2("j"))] = 30
