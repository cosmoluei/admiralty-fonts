"""
Milestone 3 Latin Extended / GF Latin Core glyphs, combining diacritical marks,
spacing modifiers, Latin-1 symbols, and Chat UI arrows for Admiralty Sans Regular.
"""

from __future__ import annotations
from typing import Callable, Dict, List, Tuple

from design_system import (
    ContourBuilder,
    METRICS,
    SansWeightParams,
    TABULAR_FIG_WIDTH,
    bar_segment_contour,
    humanist_oval_contour,
    lerp_x,
    rect_contour,
    union_contours,
)
from glyphs_sans_caps import build_D, build_H, build_I, build_J, build_L, build_N, build_O, build_P, build_T, build_W
from glyphs_sans_figs_punct import (
    build_asciitilde,
    build_equal,
    build_exclam,
    build_greater,
    build_hyphen,
    build_less,
    build_plus,
    build_quotedblright,
    build_question,
    build_quoteright,
)
from glyphs_sans_lc import build_d, build_f, build_h, build_i, build_j, build_k, build_l, build_n, build_o, build_t, build_u


# ---------------------------------------------------------------------------
# Special European Base Letters (Contours)
# ---------------------------------------------------------------------------

def build_dotlessi(p: SansWeightParams) -> List[ContourBuilder]:
    return [rect_contour(80, 0, 80 + p.lc_stem_v, METRICS.x_height)]


def build_dotlessj(p: SansWeightParams) -> List[ContourBuilder]:
    xh = METRICS.x_height
    desc_bot = METRICS.descender - 4
    stem = (
        ContourBuilder((52, desc_bot))
        .hv_to(182, -62, 0.58, 0.58)
        .line_to(182, xh)
        .line_to(96, xh)
        .line_to(96, -64)
        .vh_to(44, -152, 0.58, 0.58)
        .curve_to((26, -152), (10, -149), (-4, -144), smooth=False)
        .line_to(-16, -212)
        .curve_to((6, -220), (28, desc_bot), (52, desc_bot), smooth=True)
    )
    return [stem]


def build_AE(p: SansWeightParams) -> List[ContourBuilder]:
    cap = METRICS.cap_height  # 700
    bh = p.cap_stem_h         # 78
    # Left diagonal of A meets shared upright stem (438..530), E arms extend to 842
    yb0, yb1 = 194, 266
    xl_b0 = lerp_x(124, 0, 438, 560, yb0)
    xl_b1 = lerp_x(124, 0, 438, 560, yb1)

    outer = (
        ContourBuilder((26, 0))
        .line_to(124, 0)
        .line_to(xl_b0, yb0)
        .line_to(438, yb0)
        .line_to(438, 0)
        .line_to(846, 0)
        .line_to(846, bh)
        .line_to(530, bh)
        .line_to(530, 322)
        .line_to(798, 322)
        .line_to(798, 398)
        .line_to(530, 398)
        .line_to(530, cap - bh)
        .line_to(832, cap - bh)
        .line_to(832, cap)
        .line_to(388, cap)
    )
    inner = (
        ContourBuilder((xl_b1, yb1))
        .line_to(430, 560)
        .line_to(438, 560)
        .line_to(438, yb1)
    )
    return [outer, inner]


def build_ae(p: SansWeightParams) -> List[ContourBuilder]:
    # Explicit non-overlapping humanist 'æ' sharing a crisp 84u central stem (384..468)
    # with clean V-crotches at top (422..428, 446) and bottom (422..428, 74).
    outer = (
        ContourBuilder((212, -10))
        .curve_to((290, -10), (376, 18), (422, 74), smooth=False)
        .line_to(428, 74)
        .curve_to((470, 18), (534, -10), (614, -10), smooth=True)
        .curve_to((698, -10), (760, 24), (796, 88), smooth=False)
        .line_to(748, 146)
        .curve_to((712, 92), (666, 62), (616, 62), smooth=True)
        .curve_to((534, 62), (472, 132), (468, 236), smooth=False)
        .line_to(806, 236)
        .line_to(806, 278)
        .vh_to(610, 530, 0.58, 0.58)
        .curve_to((536, 530), (468, 500), (428, 446), smooth=False)
        .line_to(422, 446)
        .curve_to((388, 500), (330, 530), (264, 530), smooth=True)
        .curve_to((190, 530), (130, 510), (86, 476), smooth=False)
        .line_to(108, 410)
        .curve_to((148, 440), (200, 458), (256, 458), smooth=True)
        .hv_to(384, 346, 0.56, 0.56)
        .line_to(384, 304)
        .curve_to((270, 302), (54, 256), (54, 136), smooth=True)
        .vh_to(212, -10, 0.58, 0.58)
    )
    inner_a = (
        ContourBuilder((224, 58))
        .hv_to(138, 138, 0.58, 0.58)
        .curve_to((138, 206), (260, 244), (384, 246), smooth=False)
        .line_to(384, 146)
        .vh_to(224, 58, 0.56, 0.58)
    )
    inner_e = (
        ContourBuilder((468, 302))
        .line_to(468, 342)
        .vh_to(604, 458, 0.56, 0.58)
        .curve_to((672, 458), (720, 396), (726, 302), smooth=False)
    )
    return [outer, inner_a, inner_e]


def build_OE(p: SansWeightParams) -> List[ContourBuilder]:
    cap = METRICS.cap_height
    bh = p.cap_stem_h  # 78
    # Explicit 2-contour 'Œ': left humanist D-bowl meeting shared 92u stem (456..548)
    # with clean symmetric crotches at (456, 58) and (456, 642).
    outer = (
        ContourBuilder((298, -12))
        .curve_to((368, -12), (422, 14), (456, 58), smooth=False)
        .line_to(458, 0)
        .line_to(884, 0)
        .line_to(884, bh)
        .line_to(548, bh)
        .line_to(548, 322)
        .line_to(834, 322)
        .line_to(834, 398)
        .line_to(548, 398)
        .line_to(548, cap - bh)
        .line_to(868, cap - bh)
        .line_to(868, cap)
        .line_to(458, cap)
        .line_to(456, 642)
        .curve_to((422, 686), (368, 712), (298, 712), smooth=True)
        .hv_to(56, 350, 0.585, 0.59)
        .vh_to(298, -12, 0.59, 0.585)
    )
    inner = (
        ContourBuilder((308, 66))
        .hv_to(152, 350, 0.59, 0.60)
        .vh_to(308, 634, 0.60, 0.59)
        .hv_to(456, 514, 0.56, 0.56)
        .line_to(456, 186)
        .vh_to(308, 66, 0.56, 0.56)
    )
    return [outer, inner]


def build_oe(p: SansWeightParams) -> List[ContourBuilder]:
    # Explicit 3-contour humanist 'œ': left D-bowl + right 'e' sharing a crisp 84u
    # central stem (392..476) with clean top/bottom crotches (zero center blob).
    outer = (
        ContourBuilder((250, -10))
        .curve_to((328, -10), (392, 18), (430, 74), smooth=False)
        .line_to(436, 74)
        .curve_to((476, 18), (540, -10), (622, -10), smooth=True)
        .curve_to((706, -10), (768, 24), (804, 88), smooth=False)
        .line_to(756, 146)
        .curve_to((720, 92), (674, 62), (624, 62), smooth=True)
        .curve_to((542, 62), (480, 132), (476, 236), smooth=False)
        .line_to(814, 236)
        .line_to(814, 278)
        .vh_to(618, 530, 0.58, 0.58)
        .curve_to((544, 530), (476, 500), (436, 446), smooth=False)
        .line_to(430, 446)
        .curve_to((392, 500), (328, 530), (250, 530), smooth=True)
        .hv_to(54, 260, 0.585, 0.585)
        .vh_to(250, -10, 0.585, 0.585)
    )
    inner_o = (
        ContourBuilder((266, 62))
        .hv_to(144, 260, 0.59, 0.60)
        .vh_to(266, 458, 0.60, 0.59)
        .hv_to(392, 334, 0.56, 0.56)
        .line_to(392, 186)
        .vh_to(266, 62, 0.56, 0.56)
    )
    inner_e = (
        ContourBuilder((476, 302))
        .line_to(476, 342)
        .vh_to(612, 458, 0.56, 0.58)
        .curve_to((680, 458), (728, 396), (734, 302), smooth=False)
    )
    return [outer, inner_o, inner_e]


def build_Oslash(p: SansWeightParams) -> List[ContourBuilder]:
    o_parts = build_O(p)
    slash = bar_segment_contour((92, -38), (592, 738), 68)
    return union_contours(o_parts + [slash])


def build_oslash(p: SansWeightParams) -> List[ContourBuilder]:
    o_parts = build_o(p)
    slash = bar_segment_contour((86, -32), (494, 552), 62)
    return union_contours(o_parts + [slash])


def build_Eth(p: SansWeightParams) -> List[ContourBuilder]:
    d_parts = build_D(p)
    bar = rect_contour(18, 322, 306, 392)
    return union_contours(d_parts + [bar])


def build_Dcroat(p: SansWeightParams) -> List[ContourBuilder]:
    return build_Eth(p)


def build_dcroat(p: SansWeightParams) -> List[ContourBuilder]:
    d_parts = build_d(p)
    bar = rect_contour(284, 556, 554, 620)
    return union_contours(d_parts + [bar])


def build_eth(p: SansWeightParams) -> List[ContourBuilder]:
    # Icelandic lowercase eth (ð): smooth top crown at y=482 and cleanly separated
    # crossbar at y=566..698 so pathops produces exact 2 contours (zero trapped slivers!)
    outer = (
        ContourBuilder((286, -10))
        .hv_to(518, 252, 0.585, 0.585)
        .curve_to((518, 444), (410, 634), (196, 760), smooth=False)
        .line_to(144, 704)
        .curve_to((262, 628), (350, 532), (394, 422), smooth=False)
        .curve_to((358, 464), (304, 484), (244, 484), smooth=False)
        .hv_to(54, 240, 0.585, 0.585)
        .vh_to(286, -10, 0.585, 0.585)
    )
    inner = (
        ContourBuilder((282, 62))
        .hv_to(144, 242, 0.59, 0.60)
        .vh_to(272, 420, 0.60, 0.59)
        .hv_to(426, 252, 0.58, 0.58)
        .vh_to(282, 62, 0.58, 0.58)
    )
    cross = bar_segment_contour((188, 566), (456, 698), 58)
    return union_contours([outer, inner, cross])


def build_Thorn(p: SansWeightParams) -> List[ContourBuilder]:
    cap = METRICS.cap_height
    xl0, xl1 = 82, 82 + p.cap_stem_v
    outer = (
        ContourBuilder((xl0, 0))
        .line_to(xl1, 0)
        .line_to(xl1, 166)
        .line_to(316, 166)
        .hv_to(542, 376, 0.58, 0.58)
        .vh_to(316, 586, 0.58, 0.58)
        .line_to(xl1, 586)
        .line_to(xl1, cap)
        .line_to(xl0, cap)
    )
    inner = (
        ContourBuilder((xl1, 242))
        .line_to(xl1, 510)
        .line_to(308, 510)
        .hv_to(446, 376, 0.59, 0.59)
        .vh_to(308, 242, 0.59, 0.59)
    )
    return [outer, inner]


def build_thorn(p: SansWeightParams) -> List[ContourBuilder]:
    asc = METRICS.ascender
    desc = METRICS.descender
    top = METRICS.x_height + METRICS.lc_overshoot
    bot = -METRICS.lc_overshoot
    outer = (
        ContourBuilder((74, desc))
        .line_to(160, desc)
        .line_to(160, 68)
        .curve_to((192, 18), (250, bot), (324, bot), smooth=True)
        .hv_to(522, 260, 0.585, 0.585)
        .vh_to(324, top, 0.585, 0.585)
        .curve_to((250, top), (192, 502), (160, 452), smooth=False)
        .line_to(160, asc)
        .line_to(74, asc)
    )
    inner = (
        ContourBuilder((308, 62))
        .hv_to(160, 188, 0.56, 0.56)
        .line_to(160, 332)
        .vh_to(308, 458, 0.56, 0.56)
        .hv_to(432, 260, 0.59, 0.60)
        .vh_to(308, 62, 0.60, 0.59)
    )
    return [outer, inner]


def build_germandbls(p: SansWeightParams) -> List[ContourBuilder]:
    # Classic calm humanist Eszett (ß): left stem 76..162 ascending into 748 arch,
    # flowing into an upper-right loop + open lower-right belly.
    c = (
        ContourBuilder((76, 0))
        .line_to(162, 0)
        .line_to(162, 536)
        .vh_to(298, 678, 0.58, 0.58)
        .hv_to(418, 562, 0.58, 0.58)
        .curve_to((418, 492), (372, 448), (274, 412), smooth=False)
        .line_to(254, 348)
        .curve_to((394, 326), (464, 266), (464, 174), smooth=False)
        .vh_to(332, 62, 0.58, 0.58)
        .curve_to((284, 62), (244, 76), (212, 102), smooth=False)
        .line_to(176, 36)
        .curve_to((220, 4), (274, -10), (338, -10), smooth=True)
        .hv_to(556, 176, 0.58, 0.58)
        .curve_to((556, 276), (496, 346), (394, 380), smooth=False)
        .curve_to((466, 420), (508, 484), (508, 566), smooth=False)
        .vh_to(298, 750, 0.58, 0.58)
        .hv_to(76, 536, 0.58, 0.58)
    )
    return [c]


def build_Lslash(p: SansWeightParams) -> List[ContourBuilder]:
    l_base = build_L(p)
    slash = bar_segment_contour((18, 258), (274, 444), 64)
    return union_contours(l_base + [slash])


def build_lslash(p: SansWeightParams) -> List[ContourBuilder]:
    l_base = [c.translated(14, 0) for c in build_l(p)]
    slash = bar_segment_contour((14, 310), (254, 468), 58)
    return union_contours(l_base + [slash])


def build_Hbar(p: SansWeightParams) -> List[ContourBuilder]:
    h_base = build_H(p)
    bar = rect_contour(24, 502, 656, 566)
    return union_contours(h_base + [bar])


def build_hbar(p: SansWeightParams) -> List[ContourBuilder]:
    h_base = build_h(p)
    bar = rect_contour(18, 562, 292, 622)
    return union_contours(h_base + [bar])


def build_Eng(p: SansWeightParams) -> List[ContourBuilder]:
    cap = METRICS.cap_height
    c = (
        ContourBuilder((82, 0))
        .line_to(168, 0)
        .line_to(168, 548)
        .line_to(176, 548)
        .line_to(496, 0)
        .line_to(524, 0)
        .line_to(524, -64)
        .vh_to(418, -152, 0.58, 0.58)
        .curve_to((392, -152), (368, -148), (348, -140), smooth=False)
        .line_to(332, -208)
        .curve_to((360, -220), (392, -224), (426, -224), smooth=True)
        .hv_to(610, -62, 0.58, 0.58)
        .line_to(610, cap)
        .line_to(524, cap)
        .line_to(524, 152)
        .line_to(516, 152)
        .line_to(196, cap)
        .line_to(82, cap)
    )
    return [c]


def build_eng(p: SansWeightParams) -> List[ContourBuilder]:
    xh = METRICS.x_height
    top = xh + METRICS.lc_overshoot
    c = (
        ContourBuilder((76, 0))
        .line_to(162, 0)
        .line_to(162, 338)
        .curve_to((162, 404), (222, 454), (304, 454), smooth=True)
        .hv_to(422, 326, 0.56, 0.58)
        .line_to(422, -64)
        .vh_to(328, -152, 0.58, 0.58)
        .curve_to((304, -152), (282, -148), (264, -140), smooth=False)
        .line_to(248, -208)
        .curve_to((274, -220), (304, -224), (336, -224), smooth=True)
        .hv_to(508, -62, 0.58, 0.58)
        .line_to(508, 338)
        .vh_to(324, top, 0.58, 0.58)
        .curve_to((244, top), (186, 498), (156, 444), smooth=False)
        .line_to(154, xh)
        .line_to(76, xh)
    )
    return [c]


def build_Germandbls(p: SansWeightParams) -> List[ContourBuilder]:
    # Capital Eszett (ẞ, U+1E9E, w=668): distinct geometric-humanist capital with flat cap roof
    cap = METRICS.cap_height
    c = (
        ContourBuilder((82, 0))
        .line_to(172, 0)
        .line_to(172, 624)
        .line_to(350, 624)
        .hv_to(434, 536, 0.58, 0.58)
        .curve_to((434, 468), (382, 424), (274, 392), smooth=False)
        .line_to(274, 326)
        .curve_to((424, 306), (506, 252), (506, 174), smooth=False)
        .vh_to(382, 74, 0.58, 0.58)
        .curve_to((328, 74), (274, 82), (222, 98), smooth=False)
        .line_to(204, 26)
        .curve_to((262, 6), (324, -10), (390, -10), smooth=True)
        .hv_to(598, 176, 0.58, 0.58)
        .curve_to((598, 274), (534, 338), (420, 366), smooth=False)
        .curve_to((486, 404), (524, 464), (524, 540), smooth=False)
        .curve_to((524, 624), (454, cap), (354, cap), smooth=False)
        .line_to(82, cap)
    )
    return [c]


def build_IJ(p: SansWeightParams) -> List[ContourBuilder]:
    return build_I(p) + [c.translated(286, 0) for c in build_J(p)]


def build_ij(p: SansWeightParams) -> List[ContourBuilder]:
    return build_i(p) + [c.translated(236, 0) for c in build_j(p)]


def build_kgreenlandic(p: SansWeightParams) -> List[ContourBuilder]:
    # x-height kra (ĸ, w=516): identical to k except stem stops at x_height=520
    xh = METRICS.x_height
    c = (
        ContourBuilder((74, 0))
        .line_to(160, 0)
        .line_to(160, 206)
        .line_to(224, 270)
        .line_to(402, 0)
        .line_to(502, 0)
        .line_to(282, 326)
        .line_to(480, xh)
        .line_to(378, xh)
        .line_to(160, 296)
        .line_to(160, xh)
        .line_to(74, xh)
    )
    return [c]


def build_Ldot(p: SansWeightParams) -> List[ContourBuilder]:
    return build_L(p) + [humanist_oval_contour(348, 368, 48, 48, 0.62, 0.62, clockwise=False)]


def build_ldot(p: SansWeightParams) -> List[ContourBuilder]:
    return build_l(p) + [humanist_oval_contour(298, 286, 46, 46, 0.62, 0.62, clockwise=False)]


def build_napostrophe(p: SansWeightParams) -> List[ContourBuilder]:
    q = [c.translated(-24, 0) for c in build_quoteright(p)]
    n = [c.translated(166, 0) for c in build_n(p)]
    return q + n


def build_Tbar(p: SansWeightParams) -> List[ContourBuilder]:
    return union_contours(build_T(p) + [rect_contour(122, 336, 462, 400)])


def build_tbar(p: SansWeightParams) -> List[ContourBuilder]:
    return union_contours(build_t(p) + [rect_contour(42, 240, 286, 300)])


def build_longs(p: SansWeightParams) -> List[ContourBuilder]:
    # Long s (ſ, U+017F, w=312): calm upright arch without right crossbar
    c = (
        ContourBuilder((106, 0))
        .line_to(192, 0)
        .line_to(192, 608)
        .vh_to(272, 682, 0.58, 0.58)
        .curve_to((296, 682), (316, 678), (334, 670), smooth=False)
        .line_to(348, 738)
        .curve_to((322, 748), (294, 752), (262, 752), smooth=True)
        .hv_to(106, 604, 0.58, 0.58)
        .line_to(106, 520)
        .line_to(36, 520)
        .line_to(36, 448)
        .line_to(106, 448)
    )
    return [c]


# ---------------------------------------------------------------------------
# Combining Diacritical Marks (Centered at x=0, width=0) & .cap Variants
# ---------------------------------------------------------------------------
# Lowercase top marks attach via _top=(0, 520); ink sits around y=580..732.
# Capital top marks attach via _top=(0, 700); ink sits around y=752..888 (<=980!).
# Bottom marks attach via _bottom=(0, 0); ink sits around y=-212..0 (>=-320!).

def build_acutecomb(p: SansWeightParams) -> List[ContourBuilder]:
    return [ContourBuilder((-48, 580)).line_to(12, 580).line_to(98, 730).line_to(16, 730)]


def build_gravecomb(p: SansWeightParams) -> List[ContourBuilder]:
    return [ContourBuilder((-12, 580)).line_to(48, 580).line_to(-16, 730).line_to(-98, 730)]


def build_circumflexcomb(p: SansWeightParams) -> List[ContourBuilder]:
    return [
        ContourBuilder((-138, 580))
        .line_to(-66, 580)
        .line_to(0, 672)
        .line_to(66, 580)
        .line_to(138, 580)
        .line_to(34, 734)
        .line_to(-34, 734)
    ]


def build_caroncomb(p: SansWeightParams) -> List[ContourBuilder]:
    return [
        ContourBuilder((-34, 580))
        .line_to(34, 580)
        .line_to(138, 734)
        .line_to(66, 734)
        .line_to(0, 642)
        .line_to(-66, 734)
        .line_to(-138, 734)
    ]


def build_tildecomb(p: SansWeightParams) -> List[ContourBuilder]:
    return [
        ContourBuilder((74, 586))
        .curve_to((122, 586), (156, 616), (178, 674), smooth=False)
        .line_to(126, 698)
        .curve_to((110, 658), (90, 644), (66, 644), smooth=True)
        .curve_to((38, 644), (10, 660), (-22, 682), smooth=True)
        .curve_to((-54, 704), (-82, 718), (-112, 718), smooth=True)
        .curve_to((-154, 718), (-184, 690), (-198, 636), smooth=False)
        .line_to(-146, 612)
        .curve_to((-134, 648), (-118, 662), (-94, 662), smooth=True)
        .curve_to((-68, 662), (-40, 646), (-8, 624), smooth=True)
        .curve_to((24, 602), (50, 586), (74, 586), smooth=True)
    ]


def build_macroncomb(p: SansWeightParams) -> List[ContourBuilder]:
    return [rect_contour(-142, 608, 142, 672)]


def build_brevecomb(p: SansWeightParams) -> List[ContourBuilder]:
    return [
        ContourBuilder((0, 580))
        .hv_to(140, 724, 0.58, 0.58)
        .line_to(76, 724)
        .vh_to(0, 644, 0.58, 0.58)
        .hv_to(-76, 724, 0.58, 0.58)
        .line_to(-140, 724)
        .vh_to(0, 580, 0.58, 0.58)
    ]


def build_dotaccentcomb(p: SansWeightParams) -> List[ContourBuilder]:
    return [humanist_oval_contour(0, 638, 48, 48, 0.62, 0.62, clockwise=False)]


def build_dieresiscomb(p: SansWeightParams) -> List[ContourBuilder]:
    return [
        humanist_oval_contour(-92, 638, 46, 46, 0.62, 0.62, clockwise=False),
        humanist_oval_contour(92, 638, 46, 46, 0.62, 0.62, clockwise=False),
    ]


def build_ringabovecomb(p: SansWeightParams) -> List[ContourBuilder]:
    return [
        humanist_oval_contour(0, 662, 92, 92, 0.59, 0.59, clockwise=False),
        humanist_oval_contour(0, 662, 44, 44, 0.60, 0.60, clockwise=True),
    ]


def build_hungarumlautcomb(p: SansWeightParams) -> List[ContourBuilder]:
    a = build_acutecomb(p)[0]
    return [a.translated(-76, 0), a.translated(68, 0)]


# Capital-proportioned compact marks (ink y=740..854, allowing 2-level Pinyin stacking <= 980!)
def build_acutecomb_cap(p: SansWeightParams) -> List[ContourBuilder]:
    return [ContourBuilder((-48, 740)).line_to(8, 740).line_to(98, 852).line_to(18, 852)]


def build_gravecomb_cap(p: SansWeightParams) -> List[ContourBuilder]:
    return [ContourBuilder((-8, 740)).line_to(48, 740).line_to(-18, 852).line_to(-98, 852)]


def build_circumflexcomb_cap(p: SansWeightParams) -> List[ContourBuilder]:
    return [
        ContourBuilder((-142, 740))
        .line_to(-70, 740)
        .line_to(0, 808)
        .line_to(70, 740)
        .line_to(142, 740)
        .line_to(34, 856)
        .line_to(-34, 856)
    ]


def build_caroncomb_cap(p: SansWeightParams) -> List[ContourBuilder]:
    return [
        ContourBuilder((-34, 740))
        .line_to(34, 740)
        .line_to(142, 856)
        .line_to(70, 856)
        .line_to(0, 788)
        .line_to(-70, 856)
        .line_to(-142, 856)
    ]


def build_caroncomb_alt(p: SansWeightParams) -> List[ContourBuilder]:
    """Czech/Slovak apostrophe-form caron for dcaron, Lcaron, lcaron, tcaron."""
    cx, top_y = 0, 748
    y_mid = top_y - 48
    return [
        ContourBuilder((cx - 22, top_y - 214))
        .curve_to((cx + 24, top_y - 188), (cx + 48, top_y - 130), (cx + 48, y_mid), smooth=True)
        .vh_to(cx, top_y, 0.60, 0.60)
        .hv_to(cx - 46, y_mid, 0.60, 0.60)
        .vh_to(cx - 6, top_y - 94, 0.58, 0.58)
        .curve_to((cx - 8, top_y - 130), (cx - 22, top_y - 162), (cx - 48, top_y - 184), smooth=False)
    ]


def build_tildecomb_cap(p: SansWeightParams) -> List[ContourBuilder]:
    return [c.translated(0, 146) for c in build_tildecomb(p)]


def build_macroncomb_cap(p: SansWeightParams) -> List[ContourBuilder]:
    return [rect_contour(-148, 744, 148, 800)]


def build_brevecomb_cap(p: SansWeightParams) -> List[ContourBuilder]:
    return [
        ContourBuilder((0, 740))
        .hv_to(140, 852, 0.58, 0.58)
        .line_to(78, 852)
        .vh_to(0, 794, 0.58, 0.58)
        .hv_to(-78, 852, 0.58, 0.58)
        .line_to(-140, 852)
        .vh_to(0, 740, 0.58, 0.58)
    ]


def build_dotaccentcomb_cap(p: SansWeightParams) -> List[ContourBuilder]:
    return [humanist_oval_contour(0, 774, 42, 42, 0.62, 0.62, clockwise=False)]


def build_dieresiscomb_cap(p: SansWeightParams) -> List[ContourBuilder]:
    return [
        humanist_oval_contour(-94, 774, 42, 40, 0.62, 0.62, clockwise=False),
        humanist_oval_contour(94, 774, 42, 40, 0.62, 0.62, clockwise=False),
    ]


def build_ringabovecomb_cap(p: SansWeightParams) -> List[ContourBuilder]:
    return [
        humanist_oval_contour(0, 804, 82, 82, 0.59, 0.59, clockwise=False),
        humanist_oval_contour(0, 804, 38, 38, 0.60, 0.60, clockwise=True),
    ]


def build_hungarumlautcomb_cap(p: SansWeightParams) -> List[ContourBuilder]:
    a = build_acutecomb_cap(p)[0]
    return [a.translated(-76, 0), a.translated(68, 0)]


def build_cedillacomb(p: SansWeightParams) -> List[ContourBuilder]:
    # Attaches at _bottom=(0, 0)
    return [
        ContourBuilder((-34, -214))
        .curve_to((44, -214), (96, -174), (96, -118), smooth=True)
        .vh_to(12, -40, 0.58, 0.58)
        .line_to(30, 8)
        .line_to(-26, 8)
        .line_to(-52, -82)
        .line_to(-12, -88)
        .curve_to((18, -88), (36, -100), (36, -120), smooth=False)
        .vh_to(-32, -162, 0.58, 0.58)
        .curve_to((-54, -162), (-74, -156), (-90, -148), smooth=False)
        .line_to(-106, -198)
        .curve_to((-84, -208), (-60, -214), (-34, -214), smooth=True)
    ]


def build_commaaccentcomb(p: SansWeightParams) -> List[ContourBuilder]:
    return [
        ContourBuilder((-24, -212))
        .curve_to((20, -190), (42, -140), (42, -74), smooth=True)
        .vh_to(0, -32, 0.60, 0.60)
        .hv_to(-42, -74, 0.60, 0.60)
        .vh_to(-6, -114, 0.58, 0.58)
        .curve_to((-8, -146), (-22, -172), (-46, -190), smooth=False)
    ]


def build_ogonekcomb(p: SansWeightParams) -> List[ContourBuilder]:
    # Attaches at _ogonek=(0, 0)
    return [
        ContourBuilder((24, -206))
        .curve_to((56, -206), (84, -198), (108, -184), smooth=False)
        .line_to(92, -132)
        .curve_to((74, -142), (56, -146), (36, -146), smooth=True)
        .hv_to(-18, -94, 0.58, 0.58)
        .curve_to((-18, -64), (-2, -32), (24, 8), smooth=False)
        .line_to(-36, 8)
        .curve_to((-66, -32), (-82, -68), (-82, -104), smooth=False)
        .vh_to(24, -206, 0.58, 0.58)
    ]


# Spacing modifier clones (width=320, centered at x=160)
def _spacing_mark(comb_fn: Callable[[SansWeightParams], List[ContourBuilder]], dx: float = 160.0):
    def _b(p: SansWeightParams) -> List[ContourBuilder]:
        return [c.translated(dx, 0) for c in comb_fn(p)]
    return _b


# ---------------------------------------------------------------------------
# Latin-1 Symbols, Math Operators & Chat UI Arrows
# ---------------------------------------------------------------------------

def _rotate_180(contours: List[ContourBuilder], cx: float, cy: float) -> List[ContourBuilder]:
    out: List[ContourBuilder] = []
    for cb in contours:
        nc = ContourBuilder((2 * cx - cb.start[0], 2 * cy - cb.start[1]))
        for op in cb.ops:
            if op[0] == "line":
                nc.line_to(2 * cx - op[1][0], 2 * cy - op[1][1])
            elif op[0] == "curve":
                c1, c2, end, sm = op[1], op[2], op[3], op[4]
                nc.curve_to(
                    (2 * cx - c1[0], 2 * cy - c1[1]),
                    (2 * cx - c2[0], 2 * cy - c2[1]),
                    (2 * cx - end[0], 2 * cy - end[1]),
                    smooth=sm,
                )
        out.append(nc)
    return out


def build_exclamdown(p: SansWeightParams) -> List[ContourBuilder]:
    return _rotate_180(build_exclam(p), 138, 260)


def build_questiondown(p: SansWeightParams) -> List[ContourBuilder]:
    return _rotate_180(build_question(p), 238, 260)


def build_guilsinglleft(p: SansWeightParams) -> List[ContourBuilder]:
    return [
        ContourBuilder((64, 240))
        .line_to(232, 82)
        .line_to(272, 132)
        .line_to(142, 262)
        .line_to(272, 392)
        .line_to(232, 442)
        .line_to(64, 284)
    ]


def build_guilsinglright(p: SansWeightParams) -> List[ContourBuilder]:
    return [
        ContourBuilder((52, 82))
        .line_to(260, 240) if False else
        ContourBuilder((52, 132))
        .line_to(92, 82)
        .line_to(260, 240)
        .line_to(260, 284)
        .line_to(92, 442)
        .line_to(52, 392)
        .line_to(182, 262)
    ]


def build_guillemotleft(p: SansWeightParams) -> List[ContourBuilder]:
    g = build_guilsinglleft(p)[0]
    return [g.translated(-12, 0), g.translated(166, 0)]


def build_guillemotright(p: SansWeightParams) -> List[ContourBuilder]:
    g = build_guilsinglright(p)[0]
    return [g.translated(-4, 0), g.translated(174, 0)]


def build_quotesinglbase(p: SansWeightParams) -> List[ContourBuilder]:
    return [c.translated(0, -600) for c in build_quoteright(p)]


def build_quotedblbase(p: SansWeightParams) -> List[ContourBuilder]:
    return [c.translated(0, -600) for c in build_quotedblright(p)]


def build_plusminus(p: SansWeightParams) -> List[ContourBuilder]:
    h_plus = rect_contour(68, 314, 512, 382)
    v_plus = rect_contour(256, 152, 324, 544)
    minus = rect_contour(68, 36, 512, 104)
    return union_contours([h_plus, v_plus, minus])


def build_minus(p: SansWeightParams) -> List[ContourBuilder]:
    return [rect_contour(68, 240, 512, 312)]


def build_multiply(p: SansWeightParams) -> List[ContourBuilder]:
    d1 = bar_segment_contour((112, 98), (468, 454), 70)
    d2 = bar_segment_contour((112, 454), (468, 98), 70)
    return union_contours([d1, d2])


def build_divide(p: SansWeightParams) -> List[ContourBuilder]:
    bar = rect_contour(68, 240, 512, 312)
    d_top = humanist_oval_contour(290, 444, 52, 52, 0.62, 0.62, clockwise=False)
    d_bot = humanist_oval_contour(290, 108, 52, 52, 0.62, 0.62, clockwise=False)
    return [bar, d_top, d_bot]


def build_notequal(p: SansWeightParams) -> List[ContourBuilder]:
    eq = build_equal(p)
    sl = bar_segment_contour((164, 48), (416, 504), 64)
    return union_contours(eq + [sl])


def build_lessequal(p: SansWeightParams) -> List[ContourBuilder]:
    lt = [c.translated(0, 68) for c in build_less(p)]
    bar = rect_contour(68, 24, 504, 92)
    return lt + [bar]


def build_greaterequal(p: SansWeightParams) -> List[ContourBuilder]:
    gt = [c.translated(0, 68) for c in build_greater(p)]
    bar = rect_contour(76, 24, 512, 92)
    return gt + [bar]


def build_brokenbar(p: SansWeightParams) -> List[ContourBuilder]:
    return [rect_contour(104, -140, 176, 244), rect_contour(104, 366, 176, 750)]


def build_logicalnot(p: SansWeightParams) -> List[ContourBuilder]:
    return [
        ContourBuilder((64, 260))
        .line_to(444, 260)
        .line_to(444, 88)
        .line_to(516, 88)
        .line_to(516, 332)
        .line_to(64, 332)
    ]


def build_dagger(p: SansWeightParams) -> List[ContourBuilder]:
    v = rect_contour(192, -30, 262, 700)
    h = rect_contour(56, 466, 398, 534)
    return union_contours([v, h])


def build_daggerdbl(p: SansWeightParams) -> List[ContourBuilder]:
    v = rect_contour(192, -30, 262, 700)
    h1 = rect_contour(56, 476, 398, 542)
    h2 = rect_contour(56, 128, 398, 194)
    return union_contours([v, h1, h2])


def build_section(p: SansWeightParams) -> List[ContourBuilder]:
    """
    Upright, poised humanist section sign (§) built via exact normal-offset cubic
    fitting along a smooth 180°-symmetric centerline spine centered at (260, 308).
    """
    import numpy as np

    def _eval_c(p0, p1, p2, p3, t):
        mt = 1.0 - t
        return (mt**3) * p0 + 3 * (mt**2) * t * p1 + 3 * mt * (t**2) * p2 + (t**3) * p3

    def _eval_dc(p0, p1, p2, p3, t):
        mt = 1.0 - t
        return 3 * (mt**2) * (p1 - p0) + 6 * mt * t * (p2 - p1) + 3 * (t**2) * (p3 - p2)

    def _fit_c(pts):
        p0, p3 = pts[0], pts[-1]
        chord = np.linalg.norm(np.diff(pts, axis=0), axis=1)
        t = np.concatenate([[0.0], np.cumsum(chord)])
        t /= t[-1]
        mt = 1.0 - t
        mat = np.column_stack([3 * (mt**2) * t, 3 * mt * (t**2)])
        rhs = pts - ((mt**3)[:, None] * p0 + (t**3)[:, None] * p3)
        c12, _, _, _ = np.linalg.lstsq(mat, rhs, rcond=None)
        return (float(c12[0][0]), float(c12[0][1])), (float(c12[1][0]), float(c12[1][1])), (float(p3[0]), float(p3[1]))

    segs = [
        (np.array([392.0, 614.0]), np.array([364.0, 658.0]), np.array([316.0, 678.0]), np.array([262.0, 678.0])),
        (np.array([262.0, 678.0]), np.array([190.0, 678.0]), np.array([140.0, 632.0]), np.array([140.0, 570.0])),
        (np.array([140.0, 570.0]), np.array([140.0, 498.0]), np.array([204.0, 466.0]), np.array([274.0, 426.0])),
        (np.array([274.0, 426.0]), np.array([346.0, 385.0]), np.array([392.0, 344.0]), np.array([392.0, 278.0])),
        (np.array([392.0, 278.0]), np.array([392.0, 214.0]), np.array([322.0, 190.0]), np.array([246.0, 190.0])),
    ]

    left_list, right_list = [], []
    for p0, p1, p2, p3 in segs:
        ts = np.linspace(0.0, 1.0, 48)
        pts = np.array([_eval_c(p0, p1, p2, p3, tv) for tv in ts])
        dpts = np.array([_eval_dc(p0, p1, p2, p3, tv) for tv in ts])
        tang = dpts / np.linalg.norm(dpts, axis=1, keepdims=True)
        nrm = np.column_stack([-tang[:, 1], tang[:, 0]])
        hw = 34.5 - 2.5 * (np.abs(tang[:, 0]) ** 2)
        left_list.append(pts + nrm * hw[:, None])
        right_list.append(pts - nrm * hw[:, None])

    # Outer/right-normal first -> CCW positive area so union_contours unions s1 & s2!
    s1 = ContourBuilder((float(right_list[0][0][0]), float(right_list[0][0][1])))
    for rpts in right_list:
        c1, c2, p3 = _fit_c(rpts)
        s1.curve_to(c1, c2, p3)
    s1.line_to(float(left_list[-1][-1][0]), float(left_list[-1][-1][1]))
    for lpts in reversed(left_list):
        c1, c2, p3 = _fit_c(lpts[::-1])
        s1.curve_to(c1, c2, p3)

    s2 = _rotate_180([s1], 260, 308)
    return union_contours([s1] + s2)


def build_paragraph(p: SansWeightParams) -> List[ContourBuilder]:
    # Pilcrow (¶)
    bowl = (
        ContourBuilder((246, 318))
        .line_to(520, 318)
        .line_to(520, 700)
        .line_to(246, 700)
        .hv_to(56, 509, 0.58, 0.58)
        .vh_to(246, 318, 0.58, 0.58)
    )
    s1 = rect_contour(292, -80, 362, 700)
    s2 = rect_contour(450, -80, 520, 700)
    return union_contours([bowl, s1, s2])


def _circled_badge(inner_contours: List[ContourBuilder], w: int = 740) -> List[ContourBuilder]:
    # Pure non-overlapping ring (y: 10..690, cx=370, cy=350) + inner contours directly!
    cx, cy = w / 2.0, 350.0
    outer = humanist_oval_contour(cx, cy, 338, 340, 0.585, 0.585, clockwise=False)
    hole = humanist_oval_contour(cx, cy, 278, 280, 0.60, 0.60, clockwise=True)
    return [outer, hole] + inner_contours


def build_copyright(p: SansWeightParams) -> List[ContourBuilder]:
    # Clean humanist 'C' optically centered inside cx=370 circle (zero boolean distortion)
    c = (
        ContourBuilder((382, 168))
        .curve_to((444, 168), (494, 192), (526, 238), smooth=False)
        .line_to(476, 280)
        .curve_to((452, 246), (420, 230), (382, 230), smooth=True)
        .hv_to(274, 350, 0.59, 0.60)
        .vh_to(382, 470, 0.60, 0.59)
        .curve_to((420, 470), (452, 454), (476, 420), smooth=False)
        .line_to(526, 462)
        .curve_to((494, 508), (444, 532), (382, 532), smooth=True)
        .hv_to(208, 350, 0.585, 0.59)
        .vh_to(382, 168, 0.59, 0.585)
    )
    return _circled_badge([c], 740)


def build_registered(p: SansWeightParams) -> List[ContourBuilder]:
    r_out = (
        ContourBuilder((262, 184))
        .line_to(326, 184)
        .line_to(326, 324)
        .line_to(374, 324)
        .line_to(446, 184)
        .line_to(518, 184)
        .line_to(436, 336)
        .curve_to((480, 350), (506, 382), (506, 426), smooth=False)
        .vh_to(386, 516, 0.58, 0.58)
        .line_to(262, 516)
    )
    r_in = (
        ContourBuilder((326, 378))
        .line_to(326, 460)
        .line_to(382, 460)
        .hv_to(440, 419, 0.58, 0.58)
        .vh_to(382, 378, 0.58, 0.58)
    )
    return _circled_badge([r_out, r_in], 740)


def build_trademark(p: SansWeightParams) -> List[ContourBuilder]:
    t = (
        ContourBuilder((116, 380))
        .line_to(174, 380)
        .line_to(174, 646)
        .line_to(268, 646)
        .line_to(268, 700)
        .line_to(22, 700)
        .line_to(22, 646)
        .line_to(116, 646)
    )
    m = (
        ContourBuilder((306, 380))
        .line_to(360, 380)
        .line_to(360, 608)
        .line_to(366, 608)
        .line_to(452, 380)
        .line_to(500, 380)
        .line_to(586, 608)
        .line_to(592, 608)
        .line_to(592, 380)
        .line_to(648, 380)
        .line_to(648, 700)
        .line_to(568, 700)
        .line_to(479, 462)
        .line_to(473, 462)
        .line_to(384, 700)
        .line_to(306, 700)
    )
    return [t, m]


def build_currency(p: SansWeightParams) -> List[ContourBuilder]:
    ring = [
        humanist_oval_contour(290, 290, 152, 152, 0.59, 0.59, clockwise=False),
        humanist_oval_contour(290, 290, 88, 88, 0.60, 0.60, clockwise=True),
    ]
    r1 = bar_segment_contour((108, 108), (192, 192), 62)
    r2 = bar_segment_contour((472, 472), (388, 388), 62)
    r3 = bar_segment_contour((108, 472), (192, 388), 62)
    r4 = bar_segment_contour((472, 108), (388, 192), 62)
    return union_contours(ring + [r1, r2, r3, r4])


def build_micro(p: SansWeightParams) -> List[ContourBuilder]:
    xh = METRICS.x_height
    desc = METRICS.descender
    c = (
        ContourBuilder((74, desc))
        .line_to(160, desc)
        .line_to(160, 48)
        .curve_to((192, 8), (242, -10), (300, -10), smooth=False)
        .curve_to((356, -10), (398, 14), (420, 62), smooth=False)
        .line_to(422, 0)
        .line_to(500, 0)
        .line_to(500, xh)
        .line_to(414, xh)
        .line_to(414, 184)
        .vh_to(284, 66, 0.56, 0.58)
        .hv_to(160, 190, 0.58, 0.56)
        .line_to(160, xh)
        .line_to(74, xh)
    )
    return [c]


def build_ordmasculine(p: SansWeightParams) -> List[ContourBuilder]:
    # Superscript 'o' (y: 446..708) + crisp 54u underline at y: 332..386 (60u clear gap!)
    return [
        humanist_oval_contour(190, 577, 126, 131, 0.59, 0.59, clockwise=False),
        humanist_oval_contour(190, 577, 64, 75, 0.60, 0.60, clockwise=True),
        rect_contour(62, 332, 318, 386),
    ]


def build_ordfeminine(p: SansWeightParams) -> List[ContourBuilder]:
    # Optically weight-compensated superscript 'a' (y: 446..708, stem 58u, waist 46u)
    # + crisp 54u underline at y: 332..386 (60u clear daylight gap!).
    outer = (
        ContourBuilder((162, 446))
        .curve_to((206, 446), (242, 460), (262, 486), smooth=False)
        .line_to(264, 450)
        .line_to(320, 450)
        .line_to(320, 614)
        .vh_to(194, 708, 0.58, 0.58)
        .curve_to((146, 708), (108, 696), (78, 676), smooth=False)
        .line_to(96, 628)
        .curve_to((122, 648), (152, 658), (188, 658), smooth=True)
        .hv_to(262, 606, 0.56, 0.56)
        .line_to(262, 594)
        .curve_to((188, 592), (60, 566), (60, 506), smooth=True)
        .vh_to(162, 446, 0.58, 0.58)
    )
    inner = (
        ContourBuilder((174, 492))
        .hv_to(118, 514, 0.58, 0.58)
        .curve_to((118, 540), (186, 550), (262, 550), smooth=False)
        .line_to(262, 518)
        .vh_to(174, 492, 0.56, 0.58)
    )
    bar = rect_contour(62, 332, 320, 386)
    return [outer, inner, bar]


def _scale_contours(
    contours: List[ContourBuilder], sx: float, sy: float, dx: float, dy: float
) -> List[ContourBuilder]:
    out: List[ContourBuilder] = []
    for cb in contours:
        nc = ContourBuilder((cb.start[0] * sx + dx, cb.start[1] * sy + dy))
        for op in cb.ops:
            if op[0] == "line":
                nc.line_to(op[1][0] * sx + dx, op[1][1] * sy + dy)
            elif op[0] == "curve":
                c1, c2, end, sm = op[1], op[2], op[3], op[4]
                nc.curve_to(
                    (c1[0] * sx + dx, c1[1] * sy + dy),
                    (c2[0] * sx + dx, c2[1] * sy + dy),
                    (end[0] * sx + dx, end[1] * sy + dy),
                    smooth=sm,
                )
        out.append(nc)
    return out


def build_onesuperior(p: SansWeightParams) -> List[ContourBuilder]:
    from glyphs_sans_figs_punct import build_one
    return _scale_contours(build_one(p), 0.64, 0.60, 26, 296)


def build_twosuperior(p: SansWeightParams) -> List[ContourBuilder]:
    from glyphs_sans_figs_punct import build_two
    return _scale_contours(build_two(p), 0.62, 0.58, 20, 304)


def build_threesuperior(p: SansWeightParams) -> List[ContourBuilder]:
    from glyphs_sans_figs_punct import build_three
    return _scale_contours(build_three(p), 0.62, 0.58, 20, 304)


def _fraction_glyph(
    num_fn: Callable[[SansWeightParams], List[ContourBuilder]],
    den_fn: Callable[[SansWeightParams], List[ContourBuilder]],
    p: SansWeightParams,
) -> List[ContourBuilder]:
    num = _scale_contours(num_fn(p), 0.56, 0.54, 16, 332)
    den = _scale_contours(den_fn(p), 0.56, 0.54, 412, 0)
    slash = ContourBuilder((168, -12)).line_to(232, -12).line_to(568, 704).line_to(504, 704)
    return num + [slash] + den


def build_onequarter(p: SansWeightParams) -> List[ContourBuilder]:
    from glyphs_sans_figs_punct import build_four, build_one
    return _fraction_glyph(build_one, build_four, p)


def build_onehalf(p: SansWeightParams) -> List[ContourBuilder]:
    from glyphs_sans_figs_punct import build_one, build_two
    return _fraction_glyph(build_one, build_two, p)


def build_threequarters(p: SansWeightParams) -> List[ContourBuilder]:
    from glyphs_sans_figs_punct import build_four, build_three
    return _fraction_glyph(build_three, build_four, p)


# Chat UI Arrows: exact single-contour mitered/blunted polygons (zero fish-tail tips!)
def build_arrowright(p: SansWeightParams) -> List[ContourBuilder]:
    # w=680, centered at y=330, shaft 72u (294..366), 45° wings (70u thick), 16u blunted nose
    c = (
        ContourBuilder((68, 294))
        .line_to(478, 294)
        .line_to(340, 156)
        .line_to(390, 106)
        .line_to(606, 322)
        .line_to(606, 338)
        .line_to(390, 554)
        .line_to(340, 504)
        .line_to(478, 366)
        .line_to(68, 366)
    )
    return [c]


def build_arrowleft(p: SansWeightParams) -> List[ContourBuilder]:
    return _rotate_180(build_arrowright(p), 340, 330)


def build_arrowup(p: SansWeightParams) -> List[ContourBuilder]:
    # w=600, shaft x: 264..336 (72u), y: 36..636, 16u blunted top nose
    c = (
        ContourBuilder((264, 36))
        .line_to(336, 36)
        .line_to(336, 508)
        .line_to(474, 370)
        .line_to(524, 420)
        .line_to(308, 636)
        .line_to(292, 636)
        .line_to(76, 420)
        .line_to(126, 370)
        .line_to(264, 508)
    )
    return [c]


def build_arrowdown(p: SansWeightParams) -> List[ContourBuilder]:
    return _rotate_180(build_arrowup(p), 300, 336)


def build_arrowupright(p: SansWeightParams) -> List[ContourBuilder]:
    # w=640, exact 9-point single CCW polygon with crisp corner at (548, 548)
    c = (
        ContourBuilder((102, 152))
        .line_to(152, 102)
        .line_to(478, 428)
        .line_to(478, 248)
        .line_to(548, 248)
        .line_to(548, 548)
        .line_to(248, 548)
        .line_to(248, 478)
        .line_to(428, 478)
    )
    return [c]


def build_arrowdownright(p: SansWeightParams) -> List[ContourBuilder]:
    # Vertical mirror of arrowupright around y=325
    c = (
        ContourBuilder((152, 548))
        .line_to(102, 498)
        .line_to(428, 172)
        .line_to(248, 172)
        .line_to(248, 102)
        .line_to(548, 102)
        .line_to(548, 402)
        .line_to(478, 402)
        .line_to(478, 222)
    )
    return [c]


def build_arrowhookleft(p: SansWeightParams) -> List[ContourBuilder]:
    # Reply / return arrow (↩): single clean CCW contour, 16u blunted nose at x=76, zero fish-tail!
    c = (
        ContourBuilder((76, 178))
        .line_to(244, 10)
        .line_to(292, 58)
        .line_to(198, 152)
        .line_to(430, 152)
        .hv_to(604, 330, 0.58, 0.58)
        .vh_to(430, 508, 0.58, 0.58)
        .line_to(316, 508)
        .line_to(316, 438)
        .line_to(426, 438)
        .hv_to(532, 330, 0.58, 0.58)
        .vh_to(426, 222, 0.58, 0.58)
        .line_to(198, 222)
        .line_to(292, 316)
        .line_to(244, 364)
        .line_to(76, 196)
    )
    return [c]


# ---------------------------------------------------------------------------
# Agent Reply Math, Currencies, Typographic & Logic Symbols (Review 1 #3)
# ---------------------------------------------------------------------------

def build_approxequal(p: SansWeightParams) -> List[ContourBuilder]:
    # Stacked humanist tildes around y=190 and y=370
    t = build_asciitilde(p)
    return [c.translated(0, -148) for c in t] + [c.translated(0, 32) for c in t]


def build_infinity(p: SansWeightParams) -> List[ContourBuilder]:
    # Crisp figure-8 infinity (x: 48..672, y: 112..460) with symmetric diagonal bridge
    outer = (
        ContourBuilder((214, 112))
        .curve_to((284, 112), (332, 162), (360, 224), smooth=False)
        .curve_to((388, 162), (436, 112), (506, 112), smooth=True)
        .hv_to(672, 286, 0.58, 0.58)
        .vh_to(506, 460, 0.58, 0.58)
        .curve_to((436, 460), (388, 410), (360, 348), smooth=False)
        .curve_to((332, 410), (284, 460), (214, 460), smooth=True)
        .hv_to(48, 286, 0.58, 0.58)
        .vh_to(214, 112, 0.58, 0.58)
    )
    hole_l = humanist_oval_contour(214, 286, 94, 104, 0.59, 0.59, clockwise=True)
    hole_r = humanist_oval_contour(506, 286, 94, 104, 0.59, 0.59, clockwise=True)
    return [outer, hole_l, hole_r]


def build_radical(p: SansWeightParams) -> List[ContourBuilder]:
    # Mathematical square root / radical sign (√, U+221A, w=580), CCW positive winding
    return [
        ContourBuilder((40, 276))
        .line_to(40, 218)
        .line_to(82, 238)
        .line_to(178, -14)
        .line_to(252, -14)
        .line_to(476, 662)
        .line_to(550, 662)
        .line_to(550, 728)
        .line_to(434, 728)
        .line_to(220, 112)
        .line_to(212, 112)
        .line_to(116, 314)
    ]


def build_pi(p: SansWeightParams) -> List[ContourBuilder]:
    # Lowercase pi (π, U+03C0, w=584)
    top_bar = rect_contour(44, 444, 540, 520)
    leg_l = rect_contour(146, 0, 226, 480)
    leg_r = (
        ContourBuilder((458, -8))
        .curve_to((486, -8), (512, -2), (532, 10), smooth=False)
        .line_to(520, 76)
        .curve_to((504, 68), (488, 64), (472, 64), smooth=True)
        .hv_to(436, 128, 0.56, 0.58)
        .line_to(436, 480)
        .line_to(356, 480)
        .line_to(356, 122)
        .vh_to(458, -8, 0.58, 0.58)
    )
    return union_contours([top_bar, leg_l, leg_r])


def build_Delta(p: SansWeightParams) -> List[ContourBuilder]:
    # Greek capital Delta (Δ) & Increment (∆), w=612
    outer = (
        ContourBuilder((34, 0))
        .line_to(578, 0)
        .line_to(346, 700)
        .line_to(266, 700)
    )
    inner = (
        ContourBuilder((138, 74))
        .line_to(302, 580)
        .line_to(310, 580)
        .line_to(474, 74)
    )
    return [outer, inner]


def build_Omega(p: SansWeightParams) -> List[ContourBuilder]:
    # Greek capital Omega (Ω) & Ohm sign (Ω), w=684
    outer = (
        ContourBuilder((52, 0))
        .line_to(272, 0)
        .line_to(272, 76)
        .curve_to((186, 124), (144, 232), (144, 368), smooth=False)
        .vh_to(342, 634, 0.59, 0.59)
        .hv_to(540, 368, 0.59, 0.59)
        .curve_to((540, 232), (498, 124), (412, 76), smooth=False)
        .line_to(412, 0)
        .line_to(632, 0)
        .line_to(632, 76)
        .line_to(510, 76)
        .curve_to((588, 148), (628, 250), (628, 372), smooth=False)
        .vh_to(342, 712, 0.585, 0.59)
        .hv_to(56, 372, 0.59, 0.585)
        .curve_to((56, 250), (96, 148), (174, 76), smooth=False)
        .line_to(52, 76)
    )
    return [outer]


def build_arrowboth(p: SansWeightParams) -> List[ContourBuilder]:
    # Double-headed left-right arrow (↔, U+2194, w=740), single CCW polygon
    return [
        ContourBuilder((54, 322))
        .line_to(254, 122)
        .line_to(302, 170)
        .line_to(176, 296)
        .line_to(564, 296)
        .line_to(438, 170)
        .line_to(486, 122)
        .line_to(686, 322)
        .line_to(686, 338)
        .line_to(486, 538)
        .line_to(438, 490)
        .line_to(564, 364)
        .line_to(176, 364)
        .line_to(302, 490)
        .line_to(254, 538)
        .line_to(54, 338)
    ]


def build_arrowdblright(p: SansWeightParams) -> List[ContourBuilder]:
    # Double rightwards arrow (⇒, U+21D2, w=700)
    b1 = rect_contour(64, 206, 466, 272)
    b2 = rect_contour(64, 388, 466, 454)
    head = (
        ContourBuilder((322, 134))
        .line_to(374, 82)
        .line_to(636, 322)
        .line_to(636, 338)
        .line_to(374, 578)
        .line_to(322, 526)
        .line_to(534, 330)
    )
    return union_contours([b1, b2, head])


def build_checkmark(p: SansWeightParams) -> List[ContourBuilder]:
    # Crisp humanist checkmark (✓, U+2713, w=600), CCW positive winding
    return [
        ContourBuilder((58, 286))
        .line_to(210, 72)
        .line_to(258, 72)
        .line_to(544, 582)
        .line_to(478, 628)
        .line_to(232, 198)
        .line_to(116, 344)
    ]


def build_ballotx(p: SansWeightParams) -> List[ContourBuilder]:
    # Ballot X cross mark (✗, U+2717, w=560)
    s1 = bar_segment_contour((92, 86), (468, 566), 70)
    s2 = bar_segment_contour((92, 566), (468, 86), 70)
    return union_contours([s1, s2])


def build_perthousand(p: SansWeightParams) -> List[ContourBuilder]:
    # Per mille sign (‰, U+2030, w=980)
    top_o = humanist_oval_contour(188, 526, 128, 174, 0.585, 0.59, clockwise=False)
    top_i = humanist_oval_contour(188, 526, 62, 114, 0.60, 0.60, clockwise=True)
    b1_o = humanist_oval_contour(558, 164, 124, 174, 0.585, 0.59, clockwise=False)
    b1_i = humanist_oval_contour(558, 164, 58, 114, 0.60, 0.60, clockwise=True)
    b2_o = humanist_oval_contour(822, 164, 124, 174, 0.585, 0.59, clockwise=False)
    b2_i = humanist_oval_contour(822, 164, 58, 114, 0.60, 0.60, clockwise=True)
    slash = ContourBuilder((156, -12)).line_to(226, -12).line_to(542, 700).line_to(472, 700)
    return [top_o, top_i, b1_o, b1_i, b2_o, b2_i, slash]


def build_minute(p: SansWeightParams) -> List[ContourBuilder]:
    return [ContourBuilder((78, 446)).line_to(136, 446).line_to(188, 708).line_to(108, 708)]


def build_second(p: SansWeightParams) -> List[ContourBuilder]:
    m = build_minute(p)[0]
    return [m.translated(-12, 0), m.translated(148, 0)]


def build_numero(p: SansWeightParams) -> List[ContourBuilder]:
    # Numero sign (№, U+2116, w=920): compact N (58..524) + superscript o (696, 577) + underline
    n_c = (
        ContourBuilder((58, 0))
        .line_to(138, 0)
        .line_to(138, 548)
        .line_to(146, 548)
        .line_to(418, 0)
        .line_to(524, 0)
        .line_to(524, 700)
        .line_to(444, 700)
        .line_to(444, 152)
        .line_to(436, 152)
        .line_to(164, 700)
        .line_to(58, 700)
    )
    o_out = humanist_oval_contour(714, 577, 134, 131, 0.59, 0.59, clockwise=False)
    o_in = humanist_oval_contour(714, 577, 68, 75, 0.60, 0.60, clockwise=True)
    bar = rect_contour(582, 332, 852, 386)
    return [n_c, o_out, o_in, bar]


def build_rupee(p: SansWeightParams) -> List[ContourBuilder]:
    # Indian Rupee (₹, U+20B9, w=580)
    cap = METRICS.cap_height
    b_top = rect_contour(56, cap - 70, 524, cap)
    b_mid = rect_contour(56, 456, 524, 522)
    neck = (
        ContourBuilder((64, 636))
        .line_to(188, 636)
        .curve_to((280, 636), (344, 574), (344, 488), smooth=False)
        .curve_to((344, 404), (284, 344), (190, 344), smooth=False)
        .line_to(64, 344)
        .line_to(64, 280)
        .line_to(356, 0)
        .line_to(468, 0)
        .line_to(192, 272)
        .curve_to((336, 286), (434, 372), (434, 488), smooth=False)
        .curve_to((434, 558), (402, 616), (350, 650), smooth=False)
        .line_to(64, 650)
    )
    return union_contours([b_top, b_mid, neck])


def build_won(p: SansWeightParams) -> List[ContourBuilder]:
    # Korean Won (₩, U+20A9, w=884): W + two horizontal crossbars
    w_base = build_W(p)
    b1 = rect_contour(26, 224, 858, 284)
    b2 = rect_contour(26, 384, 858, 444)
    return union_contours(w_base + [b1, b2])


def build_ruble(p: SansWeightParams) -> List[ContourBuilder]:
    # Russian Ruble (₽, U+20BD, w=580): P bowl + extended lower bowl bar + lower crossbar
    p_base = [c.translated(32, 0) for c in build_P(p)]
    bowl_ext = rect_contour(44, 278, 190, 354)
    low_bar = rect_contour(44, 148, 396, 210)
    return union_contours(p_base + [bowl_ext, low_bar])


def _case_shift(fn: Callable[[SansWeightParams], List[ContourBuilder]], dy: float = 82.0):
    def _b(p: SansWeightParams) -> List[ContourBuilder]:
        return [c.translated(0, dy) for c in fn(p)]
    return _b


EXT_CONTOUR_BUILDERS: Dict[str, Tuple[int, int | None, Callable[[SansWeightParams], List[ContourBuilder]]]] = {
    # (advance_width, unicode_or_None, builder)
    "nbspace": (260, 0x00A0, lambda p: []),
    "thinspace": (160, 0x2009, lambda p: []),
    "narrownbspace": (160, 0x202F, lambda p: []),
    "softhyphen": (360, 0x00AD, build_hyphen),
    "hyphentwo": (360, 0x2010, build_hyphen),
    "nonbreakinghyphen": (360, 0x2011, build_hyphen),
    "dotlessi": (246, 0x0131, build_dotlessi),
    "dotlessj": (256, 0x0237, build_dotlessj),
    "AE": (900, 0x00C6, build_AE),
    "ae": (848, 0x00E6, build_ae),
    "OE": (936, 0x0152, build_OE),
    "oe": (868, 0x0153, build_oe),
    "Oslash": (684, 0x00D8, build_Oslash),
    "oslash": (580, 0x00F8, build_oslash),
    "Eth": (668, 0x00D0, build_Eth),
    "eth": (576, 0x00F0, build_eth),
    "Dcroat": (668, 0x0110, build_Dcroat),
    "dcroat": (576, 0x0111, build_dcroat),
    "Thorn": (596, 0x00DE, build_Thorn),
    "thorn": (576, 0x00FE, build_thorn),
    "Germandbls": (668, 0x1E9E, build_Germandbls),
    "germandbls": (612, 0x00DF, build_germandbls),
    "IJ": (782, 0x0132, build_IJ),
    "ij": (492, 0x0133, build_ij),
    "kgreenlandic": (516, 0x0138, build_kgreenlandic),
    "Ldot": (568, 0x013F, build_Ldot),
    "ldot": (396, 0x0140, build_ldot),
    "napostrophe": (736, 0x0149, build_napostrophe),
    "Lslash": (556, 0x0141, build_Lslash),
    "lslash": (284, 0x0142, build_lslash),
    "Hbar": (680, 0x0126, build_Hbar),
    "hbar": (584, 0x0127, build_hbar),
    "Tbar": (584, 0x0166, build_Tbar),
    "tbar": (354, 0x0167, build_tbar),
    "longs": (312, 0x017F, build_longs),
    "Eng": (692, 0x014A, build_Eng),
    "eng": (584, 0x014B, build_eng),
    # Combining marks (width=0)
    "gravecomb": (0, 0x0300, build_gravecomb),
    "acutecomb": (0, 0x0301, build_acutecomb),
    "circumflexcomb": (0, 0x0302, build_circumflexcomb),
    "tildecomb": (0, 0x0303, build_tildecomb),
    "macroncomb": (0, 0x0304, build_macroncomb),
    "brevecomb": (0, 0x0306, build_brevecomb),
    "dotaccentcomb": (0, 0x0307, build_dotaccentcomb),
    "dieresiscomb": (0, 0x0308, build_dieresiscomb),
    "ringabovecomb": (0, 0x030A, build_ringabovecomb),
    "hungarumlautcomb": (0, 0x030B, build_hungarumlautcomb),
    "caroncomb": (0, 0x030C, build_caroncomb),
    "commaaccentcomb": (0, 0x0326, build_commaaccentcomb),
    "cedillacomb": (0, 0x0327, build_cedillacomb),
    "ogonekcomb": (0, 0x0328, build_ogonekcomb),
    # Unencoded capital-height marks
    "gravecomb.cap": (0, None, build_gravecomb_cap),
    "acutecomb.cap": (0, None, build_acutecomb_cap),
    "circumflexcomb.cap": (0, None, build_circumflexcomb_cap),
    "tildecomb.cap": (0, None, build_tildecomb_cap),
    "macroncomb.cap": (0, None, build_macroncomb_cap),
    "brevecomb.cap": (0, None, build_brevecomb_cap),
    "dotaccentcomb.cap": (0, None, build_dotaccentcomb_cap),
    "dieresiscomb.cap": (0, None, build_dieresiscomb_cap),
    "ringabovecomb.cap": (0, None, build_ringabovecomb_cap),
    "hungarumlautcomb.cap": (0, None, build_hungarumlautcomb_cap),
    "caroncomb.cap": (0, None, build_caroncomb_cap),
    "caroncomb.alt": (0, None, build_caroncomb_alt),
    # Spacing modifier letters / accents
    "acute": (320, 0x00B4, _spacing_mark(build_acutecomb)),
    "dieresis": (360, 0x00A8, _spacing_mark(build_dieresiscomb, 180)),
    "macron": (360, 0x00AF, _spacing_mark(build_macroncomb, 180)),
    "cedilla": (320, 0x00B8, _spacing_mark(build_cedillacomb)),
    "breve": (360, 0x02D8, _spacing_mark(build_brevecomb, 180)),
    "dotaccent": (300, 0x02D9, _spacing_mark(build_dotaccentcomb, 150)),
    "ring": (320, 0x02DA, _spacing_mark(build_ringabovecomb)),
    "ogonek": (320, 0x02DB, _spacing_mark(build_ogonekcomb)),
    "tilde": (420, 0x02DC, _spacing_mark(build_tildecomb, 210)),
    "hungarumlaut": (380, 0x02DD, _spacing_mark(build_hungarumlautcomb, 190)),
    "circumflex": (360, 0x02C6, _spacing_mark(build_circumflexcomb, 180)),
    "caron": (360, 0x02C7, _spacing_mark(build_caroncomb, 180)),
    # Latin-1, Currencies, Typographic & Agent Reply Symbols
    "exclamdown": (276, 0x00A1, build_exclamdown),
    "questiondown": (476, 0x00BF, build_questiondown),
    "guilsinglleft": (324, 0x2039, build_guilsinglleft),
    "guilsinglright": (324, 0x203A, build_guilsinglright),
    "guillemotleft": (496, 0x00AB, build_guillemotleft),
    "guillemotright": (496, 0x00BB, build_guillemotright),
    "quotesinglbase": (244, 0x201A, build_quotesinglbase),
    "quotedblbase": (424, 0x201E, build_quotedblbase),
    "dagger": (454, 0x2020, build_dagger),
    "daggerdbl": (454, 0x2021, build_daggerdbl),
    "section": (520, 0x00A7, build_section),
    "paragraph": (584, 0x00B6, build_paragraph),
    "copyright": (740, 0x00A9, build_copyright),
    "registered": (740, 0x00AE, build_registered),
    "trademark": (680, 0x2122, build_trademark),
    "currency": (580, 0x00A4, build_currency),
    "rupee": (580, 0x20B9, build_rupee),
    "won": (884, 0x20A9, build_won),
    "ruble": (580, 0x20BD, build_ruble),
    "perthousand": (980, 0x2030, build_perthousand),
    "minute": (248, 0x2032, build_minute),
    "second": (408, 0x2033, build_second),
    "numero": (920, 0x2116, build_numero),
    "brokenbar": (280, 0x00A6, build_brokenbar),
    "logicalnot": (580, 0x00AC, build_logicalnot),
    "plusminus": (TABULAR_FIG_WIDTH, 0x00B1, build_plusminus),
    "minus": (TABULAR_FIG_WIDTH, 0x2212, build_minus),
    "multiply": (TABULAR_FIG_WIDTH, 0x00D7, build_multiply),
    "divide": (TABULAR_FIG_WIDTH, 0x00F7, build_divide),
    "notequal": (TABULAR_FIG_WIDTH, 0x2260, build_notequal),
    "lessequal": (TABULAR_FIG_WIDTH, 0x2264, build_lessequal),
    "greaterequal": (TABULAR_FIG_WIDTH, 0x2265, build_greaterequal),
    "approxequal": (TABULAR_FIG_WIDTH, 0x2248, build_approxequal),
    "infinity": (720, 0x221E, build_infinity),
    "radical": (580, 0x221A, build_radical),
    "pi": (584, 0x03C0, build_pi),
    "Delta": (612, 0x0394, build_Delta),
    "increment": (612, 0x2206, build_Delta),
    "Omega": (684, 0x03A9, build_Omega),
    "ohm": (684, 0x2126, build_Omega),
    "checkmark": (600, 0x2713, build_checkmark),
    "ballotx": (560, 0x2717, build_ballotx),
    "micro": (576, 0x00B5, build_micro),
    "ordfeminine": (380, 0x00AA, build_ordfeminine),
    "ordmasculine": (380, 0x00BA, build_ordmasculine),
    "onesuperior": (330, 0x00B9, build_onesuperior),
    "twosuperior": (380, 0x00B2, build_twosuperior),
    "threesuperior": (380, 0x00B3, build_threesuperior),
    "onequarter": (760, 0x00BC, build_onequarter),
    "onehalf": (760, 0x00BD, build_onehalf),
    "threequarters": (760, 0x00BE, build_threequarters),
    # Chat UI Arrows
    "arrowleft": (680, 0x2190, build_arrowleft),
    "arrowup": (600, 0x2191, build_arrowup),
    "arrowright": (680, 0x2192, build_arrowright),
    "arrowdown": (600, 0x2193, build_arrowdown),
    "arrowboth": (740, 0x2194, build_arrowboth),
    "arrowupright": (640, 0x2197, build_arrowupright),
    "arrowdownright": (640, 0x2198, build_arrowdownright),
    "arrowhookleft": (680, 0x21A9, build_arrowhookleft),
    "arrowdblright": (700, 0x21D2, build_arrowdblright),
    # Case-sensitive variants for extended punctuation
    "hyphentwo.case": (360, None, _case_shift(build_hyphen, 82)),
    "nonbreakinghyphen.case": (360, None, _case_shift(build_hyphen, 82)),
    "guilsinglleft.case": (324, None, _case_shift(build_guilsinglleft, 82)),
    "guilsinglright.case": (324, None, _case_shift(build_guilsinglright, 82)),
    "guillemotleft.case": (496, None, _case_shift(build_guillemotleft, 82)),
    "guillemotright.case": (496, None, _case_shift(build_guillemotright, 82)),
    "exclamdown.case": (276, None, _case_shift(build_exclamdown, 180)),
    "questiondown.case": (476, None, _case_shift(build_questiondown, 180)),
}


# ---------------------------------------------------------------------------
# Precomposed Accented European Letters (UFO Component Recipes)
# (glyph_name, unicode_or_None, base_glyph, mark_glyph, anchor_name)
# ---------------------------------------------------------------------------

COMPOSITE_RECIPES: List[Tuple[str, int | None, str, str, str]] = [
    # Uppercase Latin-1 & GF Latin Core
    ("Agrave", 0x00C0, "A", "gravecomb.cap", "top"),
    ("Aacute", 0x00C1, "A", "acutecomb.cap", "top"),
    ("Acircumflex", 0x00C2, "A", "circumflexcomb.cap", "top"),
    ("Atilde", 0x00C3, "A", "tildecomb.cap", "top"),
    ("Adieresis", 0x00C4, "A", "dieresiscomb.cap", "top"),
    ("Aring", 0x00C5, "A", "ringabovecomb.cap", "top"),
    ("Acaron", 0x01CD, "A", "caroncomb.cap", "top"),
    ("Amacron", 0x0100, "A", "macroncomb.cap", "top"),
    ("Abreve", 0x0102, "A", "brevecomb.cap", "top"),
    ("Aogonek", 0x0104, "A", "ogonekcomb", "ogonek"),
    ("Ccedilla", 0x00C7, "C", "cedillacomb", "bottom"),
    ("Cacute", 0x0106, "C", "acutecomb.cap", "top"),
    ("Ccircumflex", 0x0108, "C", "circumflexcomb.cap", "top"),
    ("Cdotaccent", 0x010A, "C", "dotaccentcomb.cap", "top"),
    ("Ccaron", 0x010C, "C", "caroncomb.cap", "top"),
    ("Dcaron", 0x010E, "D", "caroncomb.cap", "top"),
    ("Egrave", 0x00C8, "E", "gravecomb.cap", "top"),
    ("Eacute", 0x00C9, "E", "acutecomb.cap", "top"),
    ("Ecircumflex", 0x00CA, "E", "circumflexcomb.cap", "top"),
    ("Edieresis", 0x00CB, "E", "dieresiscomb.cap", "top"),
    ("Emacron", 0x0112, "E", "macroncomb.cap", "top"),
    ("Ebreve", 0x0114, "E", "brevecomb.cap", "top"),
    ("Edotaccent", 0x0116, "E", "dotaccentcomb.cap", "top"),
    ("Eogonek", 0x0118, "E", "ogonekcomb", "ogonek"),
    ("Ecaron", 0x011A, "E", "caroncomb.cap", "top"),
    ("Gcircumflex", 0x011C, "G", "circumflexcomb.cap", "top"),
    ("Gbreve", 0x011E, "G", "brevecomb.cap", "top"),
    ("Gdotaccent", 0x0120, "G", "dotaccentcomb.cap", "top"),
    ("Gcommaaccent", 0x0122, "G", "commaaccentcomb", "bottom"),
    ("Hcircumflex", 0x0124, "H", "circumflexcomb.cap", "top"),
    ("Igrave", 0x00CC, "I", "gravecomb.cap", "top"),
    ("Iacute", 0x00CD, "I", "acutecomb.cap", "top"),
    ("Icircumflex", 0x00CE, "I", "circumflexcomb.cap", "top"),
    ("Idieresis", 0x00CF, "I", "dieresiscomb.cap", "top"),
    ("Itilde", 0x0128, "I", "tildecomb.cap", "top"),
    ("Imacron", 0x012A, "I", "macroncomb.cap", "top"),
    ("Ibreve", 0x012C, "I", "brevecomb.cap", "top"),
    ("Iogonek", 0x012E, "I", "ogonekcomb", "ogonek"),
    ("Idotaccent", 0x0130, "I", "dotaccentcomb.cap", "top"),
    ("Icaron", 0x01CF, "I", "caroncomb.cap", "top"),
    ("Jcircumflex", 0x0134, "J", "circumflexcomb.cap", "top"),
    ("Kcommaaccent", 0x0136, "K", "commaaccentcomb", "bottom"),
    ("Lacute", 0x0139, "L", "acutecomb.cap", "top"),
    ("Lcommaaccent", 0x013B, "L", "commaaccentcomb", "bottom"),
    ("Lcaron", 0x013D, "L", "caroncomb.alt", "top"),
    ("Ntilde", 0x00D1, "N", "tildecomb.cap", "top"),
    ("Nacute", 0x0143, "N", "acutecomb.cap", "top"),
    ("Ncommaaccent", 0x0145, "N", "commaaccentcomb", "bottom"),
    ("Ncaron", 0x0147, "N", "caroncomb.cap", "top"),
    ("Ograve", 0x00D2, "O", "gravecomb.cap", "top"),
    ("Oacute", 0x00D3, "O", "acutecomb.cap", "top"),
    ("Ocircumflex", 0x00D4, "O", "circumflexcomb.cap", "top"),
    ("Otilde", 0x00D5, "O", "tildecomb.cap", "top"),
    ("Odieresis", 0x00D6, "O", "dieresiscomb.cap", "top"),
    ("Omacron", 0x014C, "O", "macroncomb.cap", "top"),
    ("Obreve", 0x014E, "O", "brevecomb.cap", "top"),
    ("Ohungarumlaut", 0x0150, "O", "hungarumlautcomb.cap", "top"),
    ("Ocaron", 0x01D1, "O", "caroncomb.cap", "top"),
    ("Racute", 0x0154, "R", "acutecomb.cap", "top"),
    ("Rcommaaccent", 0x0156, "R", "commaaccentcomb", "bottom"),
    ("Rcaron", 0x0158, "R", "caroncomb.cap", "top"),
    ("Sacute", 0x015A, "S", "acutecomb.cap", "top"),
    ("Scircumflex", 0x015C, "S", "circumflexcomb.cap", "top"),
    ("Scedilla", 0x015E, "S", "cedillacomb", "bottom"),
    ("Scaron", 0x0160, "S", "caroncomb.cap", "top"),
    ("Scommaaccent", 0x0218, "S", "commaaccentcomb", "bottom"),
    ("Tcedilla", 0x0162, "T", "cedillacomb", "bottom"),
    ("Tcaron", 0x0164, "T", "caroncomb.cap", "top"),
    ("Tcommaaccent", 0x021A, "T", "commaaccentcomb", "bottom"),
    ("Ugrave", 0x00D9, "U", "gravecomb.cap", "top"),
    ("Uacute", 0x00DA, "U", "acutecomb.cap", "top"),
    ("Ucircumflex", 0x00DB, "U", "circumflexcomb.cap", "top"),
    ("Udieresis", 0x00DC, "U", "dieresiscomb.cap", "top"),
    ("Ucaron", 0x01D3, "U", "caroncomb.cap", "top"),
    ("Udieresismacron", 0x01D5, "Udieresis", "macroncomb.cap", "top"),
    ("Udieresisacute", 0x01D7, "Udieresis", "acutecomb.cap", "top"),
    ("Udieresiscaron", 0x01D9, "Udieresis", "caroncomb.cap", "top"),
    ("Udieresisgrave", 0x01DB, "Udieresis", "gravecomb.cap", "top"),
    ("Utilde", 0x0168, "U", "tildecomb.cap", "top"),
    ("Umacron", 0x016A, "U", "macroncomb.cap", "top"),
    ("Ubreve", 0x016C, "U", "brevecomb.cap", "top"),
    ("Uring", 0x016E, "U", "ringabovecomb.cap", "top"),
    ("Uhungarumlaut", 0x0170, "U", "hungarumlautcomb.cap", "top"),
    ("Uogonek", 0x0172, "U", "ogonekcomb", "ogonek"),
    ("Wcircumflex", 0x0174, "W", "circumflexcomb.cap", "top"),
    ("Wgrave", 0x1E80, "W", "gravecomb.cap", "top"),
    ("Wacute", 0x1E82, "W", "acutecomb.cap", "top"),
    ("Wdieresis", 0x1E84, "W", "dieresiscomb.cap", "top"),
    ("Yacute", 0x00DD, "Y", "acutecomb.cap", "top"),
    ("Ycircumflex", 0x0176, "Y", "circumflexcomb.cap", "top"),
    ("Ydieresis", 0x0178, "Y", "dieresiscomb.cap", "top"),
    ("Ygrave", 0x1EF2, "Y", "gravecomb.cap", "top"),
    ("Zacute", 0x0179, "Z", "acutecomb.cap", "top"),
    ("Zdotaccent", 0x017B, "Z", "dotaccentcomb.cap", "top"),
    ("Zcaron", 0x017D, "Z", "caroncomb.cap", "top"),

    # Lowercase Latin-1 & GF Latin Core
    ("agrave", 0x00E0, "a", "gravecomb", "top"),
    ("aacute", 0x00E1, "a", "acutecomb", "top"),
    ("acircumflex", 0x00E2, "a", "circumflexcomb", "top"),
    ("atilde", 0x00E3, "a", "tildecomb", "top"),
    ("adieresis", 0x00E4, "a", "dieresiscomb", "top"),
    ("aring", 0x00E5, "a", "ringabovecomb", "top"),
    ("amacron", 0x0101, "a", "macroncomb", "top"),
    ("acaron", 0x01CE, "a", "caroncomb", "top"),
    ("abreve", 0x0103, "a", "brevecomb", "top"),
    ("aogonek", 0x0105, "a", "ogonekcomb", "ogonek"),
    ("ccedilla", 0x00E7, "c", "cedillacomb", "bottom"),
    ("cacute", 0x0107, "c", "acutecomb", "top"),
    ("ccircumflex", 0x0109, "c", "circumflexcomb", "top"),
    ("cdotaccent", 0x010B, "c", "dotaccentcomb", "top"),
    ("ccaron", 0x010D, "c", "caroncomb", "top"),
    ("dcaron", 0x010F, "d", "caroncomb.alt", "top"),
    ("egrave", 0x00E8, "e", "gravecomb", "top"),
    ("eacute", 0x00E9, "e", "acutecomb", "top"),
    ("ecircumflex", 0x00EA, "e", "circumflexcomb", "top"),
    ("edieresis", 0x00EB, "e", "dieresiscomb", "top"),
    ("emacron", 0x0113, "e", "macroncomb", "top"),
    ("ebreve", 0x0115, "e", "brevecomb", "top"),
    ("edotaccent", 0x0117, "e", "dotaccentcomb", "top"),
    ("eogonek", 0x0119, "e", "ogonekcomb", "ogonek"),
    ("ecaron", 0x011B, "e", "caroncomb", "top"),
    ("gcircumflex", 0x011D, "g", "circumflexcomb", "top"),
    ("gbreve", 0x011F, "g", "brevecomb", "top"),
    ("gdotaccent", 0x0121, "g", "dotaccentcomb", "top"),
    ("gcommaaccent", 0x0123, "g", "acutecomb", "top"),
    ("hcircumflex", 0x0125, "h", "circumflexcomb.cap", "top"),
    ("igrave", 0x00EC, "dotlessi", "gravecomb", "top"),
    ("iacute", 0x00ED, "dotlessi", "acutecomb", "top"),
    ("icircumflex", 0x00EE, "dotlessi", "circumflexcomb", "top"),
    ("idieresis", 0x00EF, "dotlessi", "dieresiscomb", "top"),
    ("itilde", 0x0129, "dotlessi", "tildecomb", "top"),
    ("imacron", 0x012B, "dotlessi", "macroncomb", "top"),
    ("ibreve", 0x012D, "dotlessi", "brevecomb", "top"),
    ("icaron", 0x01D0, "dotlessi", "caroncomb", "top"),
    ("iogonek", 0x012F, "i", "ogonekcomb", "ogonek"),
    # Review 3: i-ogonek without its dot, used when an accent is typed after it (Lithuanian)
    ("iogonek.dotless", None, "dotlessi", "ogonekcomb", "ogonek"),
    ("i.loclTRK", None, "dotlessi", "dotaccentcomb", "top"),
    ("jcircumflex", 0x0135, "dotlessj", "circumflexcomb", "top"),
    ("kcommaaccent", 0x0137, "k", "commaaccentcomb", "bottom"),
    ("lacute", 0x013A, "l", "acutecomb.cap", "top"),
    ("lcommaaccent", 0x013C, "l", "commaaccentcomb", "bottom"),
    ("lcaron", 0x013E, "l", "caroncomb.alt", "top"),
    ("ntilde", 0x00F1, "n", "tildecomb", "top"),
    ("nacute", 0x0144, "n", "acutecomb", "top"),
    ("ncommaaccent", 0x0146, "n", "commaaccentcomb", "bottom"),
    ("ncaron", 0x0148, "n", "caroncomb", "top"),
    ("ograve", 0x00F2, "o", "gravecomb", "top"),
    ("oacute", 0x00F3, "o", "acutecomb", "top"),
    ("ocircumflex", 0x00F4, "o", "circumflexcomb", "top"),
    ("otilde", 0x00F5, "o", "tildecomb", "top"),
    ("odieresis", 0x00F6, "o", "dieresiscomb", "top"),
    ("omacron", 0x014D, "o", "macroncomb", "top"),
    ("obreve", 0x014F, "o", "brevecomb", "top"),
    ("ohungarumlaut", 0x0151, "o", "hungarumlautcomb", "top"),
    ("ocaron", 0x01D2, "o", "caroncomb", "top"),
    ("racute", 0x0155, "r", "acutecomb", "top"),
    ("rcommaaccent", 0x0157, "r", "commaaccentcomb", "bottom"),
    ("rcaron", 0x0159, "r", "caroncomb", "top"),
    ("sacute", 0x015B, "s", "acutecomb", "top"),
    ("scircumflex", 0x015D, "s", "circumflexcomb", "top"),
    ("scedilla", 0x015F, "s", "cedillacomb", "bottom"),
    ("scaron", 0x0161, "s", "caroncomb", "top"),
    ("scommaaccent", 0x0219, "s", "commaaccentcomb", "bottom"),
    ("tcedilla", 0x0163, "t", "cedillacomb", "bottom"),
    ("tcaron", 0x0165, "t", "caroncomb.alt", "top"),
    ("tcommaaccent", 0x021B, "t", "commaaccentcomb", "bottom"),
    ("ugrave", 0x00F9, "u", "gravecomb", "top"),
    ("uacute", 0x00FA, "u", "acutecomb", "top"),
    ("ucircumflex", 0x00FB, "u", "circumflexcomb", "top"),
    ("udieresis", 0x00FC, "u", "dieresiscomb", "top"),
    ("ucaron", 0x01D4, "u", "caroncomb", "top"),
    ("udieresismacron", 0x01D6, "udieresis", "macroncomb", "top"),
    ("udieresisacute", 0x01D8, "udieresis", "acutecomb", "top"),
    ("udieresiscaron", 0x01DA, "udieresis", "caroncomb", "top"),
    ("udieresisgrave", 0x01DC, "udieresis", "gravecomb", "top"),
    ("utilde", 0x0169, "u", "tildecomb", "top"),
    ("umacron", 0x016B, "u", "macroncomb", "top"),
    ("ubreve", 0x016D, "u", "brevecomb", "top"),
    ("uring", 0x016F, "u", "ringabovecomb", "top"),
    ("uhungarumlaut", 0x0171, "u", "hungarumlautcomb", "top"),
    ("uogonek", 0x0173, "u", "ogonekcomb", "ogonek"),
    ("wcircumflex", 0x0175, "w", "circumflexcomb", "top"),
    ("wgrave", 0x1E81, "w", "gravecomb", "top"),
    ("wacute", 0x1E83, "w", "acutecomb", "top"),
    ("wdieresis", 0x1E85, "w", "dieresiscomb", "top"),
    ("yacute", 0x00FD, "y", "acutecomb", "top"),
    ("ydieresis", 0x00FF, "y", "dieresiscomb", "top"),
    ("ycircumflex", 0x0177, "y", "circumflexcomb", "top"),
    ("ygrave", 0x1EF3, "y", "gravecomb", "top"),
    ("zacute", 0x017A, "z", "acutecomb", "top"),
    ("zdotaccent", 0x017C, "z", "dotaccentcomb", "top"),
    ("zcaron", 0x017E, "z", "caroncomb", "top"),
]
