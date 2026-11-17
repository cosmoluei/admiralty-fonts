"""
Numerals (proportional, tabular, slashed zero), serif-tailored currencies,
special European base letters, punctuation, symbols, combining marks, and
OpenType assembly for Admiralty Serif Regular (1000 UPM) — matching ~2.25:1
literary contrast and crisp 26-28u bracketed serifs.
"""

from __future__ import annotations
from typing import Callable, Dict, List, Tuple

from design_system import (
    ContourBuilder,
    DUPLEX_ADVANCE_WIDTHS,
    METRICS,
    TABULAR_FIG_WIDTH,
    UNICODE_MAP,
    bar_segment_contour,
    humanist_oval_contour,
    lerp_x,
    rect_contour,
    union_contours,
)
from glyphs_sans_figs_punct import FIG_CAP, FIG_TOP, FIG_BOT, FIG_PUNCT_GLYPH_BUILDERS, build_quoteright
from glyphs_sans_latin_ext import EXT_CONTOUR_BUILDERS, _fraction_glyph, _scale_contours
from glyphs_serif_caps import (
    SERIF_CAP_BUILDERS,
    build_D as build_serif_D,
    build_H as build_serif_H,
    build_I as build_serif_I,
    build_J as build_serif_J,
    build_L as build_serif_L,
    build_O as build_serif_O,
    build_S as build_serif_S,
    build_T as build_serif_T,
    build_W as build_serif_W,
)
from glyphs_serif_lc import (
    SERIF_LC_BUILDERS,
    build_c as build_serif_c,
    build_d as build_serif_d,
    build_h as build_serif_h,
    build_i as build_serif_i,
    build_j as build_serif_j,
    build_l as build_serif_l,
    build_n as build_serif_n,
    build_o as build_serif_o,
    build_t as build_serif_t,
)
from serif_primitives import (
    SERIF_REGULAR,
    SerifWeightParams,
    diag_foot_serif,
    diag_head_serif,
    foot_pad_ccw,
    head_pad_ccw,
    vstem_serifed,
)


# ---------------------------------------------------------------------------
# Serif Numerals 0-9 (~2.25:1 contrast: 96-104u stems / 44u hairlines)
# ---------------------------------------------------------------------------

def _serif_zero_rings(p: SerifWeightParams) -> List[ContourBuilder]:
    cx, cy = 282, 345
    rx_out, ry_out = 228, 355
    rx_in = rx_out - p.fig_bowl_v   # 124 (104u vertical bellies)
    ry_in = ry_out - p.fig_stem_h   # 305 (50u top/bottom hairlines)
    return [
        humanist_oval_contour(cx, cy, rx_out, ry_out, 0.575, 0.59, clockwise=False),
        humanist_oval_contour(cx, cy, rx_in, ry_in, 0.605, 0.605, clockwise=True),
    ]


def build_serif_zero(p: SerifWeightParams) -> List[ContourBuilder]:
    rings = _serif_zero_rings(p)
    dot = humanist_oval_contour(282, 345, 32, 35, 0.60, 0.60, clockwise=False)
    return [rings[0], rings[1], dot]


def build_serif_zero_slash(p: SerifWeightParams) -> List[ContourBuilder]:
    rings = _serif_zero_rings(p)
    slash = bar_segment_contour((146, 92), (418, 598), 48)
    return union_contours([rings[0], rings[1], slash])


def build_serif_one(p: SerifWeightParams) -> List[ContourBuilder]:
    stem_flag = (
        ContourBuilder((176, 0))
        .line_to(272, 0)
        .line_to(272, FIG_CAP)
        .line_to(216, FIG_CAP)
        .line_to(54, 578)
        .line_to(74, 538)
        .line_to(176, 610)
    )
    foot = foot_pad_ccw(176, 272, 0, ext_l=82, ext_r=82, sh=30, brk=34)
    return union_contours([stem_flag, foot])


def build_serif_one_tnum(p: SerifWeightParams) -> List[ContourBuilder]:
    dx = (TABULAR_FIG_WIDTH - DUPLEX_ADVANCE_WIDTHS["one"]) / 2.0
    return [c.translated(dx, 0) for c in build_serif_one(p)]


def build_serif_two(p: SerifWeightParams) -> List[ContourBuilder]:
    bh = p.fig_stem_h  # 50
    c = (
        ContourBuilder((42, 0))
        .line_to(502, 0)
        .line_to(512, 160)
        .line_to(476, 160)
        .curve_to((468, 84), (446, bh), (388, bh), smooth=False)
        .line_to(148, bh)
        .curve_to((304, 198), (488, 348), (488, 512), smooth=False)
        .vh_to(272, FIG_TOP, 0.58, 0.58)
        .hv_to(62, 578, 0.58, 0.56)
        .vh_to(106, 534, 0.58, 0.58)
        .hv_to(148, 578, 0.58, 0.58)
        .vh_to(264, 658, 0.48, 0.58)
        .hv_to(388, 508, 0.58, 0.58)
        .curve_to((388, 368), (222, 232), (42, 38), smooth=False)
    )
    return [c]


def build_serif_three(p: SerifWeightParams) -> List[ContourBuilder]:
    c = (
        ContourBuilder((262, FIG_BOT))
        .hv_to(506, 190, 0.58, 0.58)
        .curve_to((506, 290), (442, 352), (344, 370), smooth=False)
        .curve_to((424, 392), (482, 448), (482, 532), smooth=False)
        .vh_to(268, FIG_TOP, 0.58, 0.58)
        .curve_to((174, FIG_TOP), (96, 660), (62, 594), smooth=False)
        .line_to(98, 562)
        .curve_to((138, 626), (196, 662), (260, 662), smooth=True)
        .hv_to(384, 526, 0.58, 0.58)
        .vh_to(240, 396, 0.58, 0.58)
        .line_to(188, 396)
        .line_to(188, 346)
        .line_to(250, 346)
        .hv_to(404, 192, 0.58, 0.58)
        .vh_to(258, 40, 0.58, 0.58)
        .curve_to((184, 40), (126, 68), (88, 126), smooth=False)
        .line_to(48, 96)
        .curve_to((92, 20), (166, FIG_BOT), (262, FIG_BOT), smooth=True)
    )
    return [c]


def build_serif_four(p: SerifWeightParams) -> List[ContourBuilder]:
    outer = (
        ContourBuilder((346, 0))
        .line_to(442, 0)
        .line_to(442, 176)
        .line_to(534, 176)
        .line_to(534, 226)
        .line_to(442, 226)
        .line_to(442, FIG_CAP)
        .line_to(356, FIG_CAP)
        .line_to(32, 218)
        .line_to(32, 176)
        .line_to(346, 176)
    )
    inner = (
        ContourBuilder((92, 226))
        .line_to(340, 598)
        .line_to(346, 598)
        .line_to(346, 226)
    )
    foot = foot_pad_ccw(346, 442, 0, ext_l=56, ext_r=54, sh=30, brk=32)
    return union_contours([outer, inner, foot])


def build_serif_five(p: SerifWeightParams) -> List[ContourBuilder]:
    c = (
        ContourBuilder((262, FIG_BOT))
        .hv_to(506, 220, 0.58, 0.58)
        .vh_to(278, 446, 0.58, 0.58)
        .curve_to((228, 446), (184, 434), (146, 412), smooth=False)
        .line_to(164, 640)
        .line_to(468, 640)
        .line_to(486, 706)
        .line_to(450, 706)
        .curve_to((442, 692), (428, 690), (400, 690), smooth=False)
        .line_to(110, 690)
        .line_to(86, 344)
        .line_to(128, 326)
        .curve_to((168, 374), (214, 396), (268, 396), smooth=False)
        .hv_to(406, 218, 0.58, 0.58)
        .vh_to(260, 40, 0.58, 0.58)
        .curve_to((188, 40), (130, 68), (92, 124), smooth=False)
        .line_to(52, 92)
        .curve_to((94, 18), (170, FIG_BOT), (262, FIG_BOT), smooth=True)
    )
    return [c]


def build_serif_six(p: SerifWeightParams) -> List[ContourBuilder]:
    outer = (
        ContourBuilder((290, FIG_BOT))
        .hv_to(518, 224, 0.58, 0.585)
        .vh_to(304, 442, 0.585, 0.58)
        .curve_to((228, 442), (168, 414), (134, 362), smooth=False)
        .curve_to((144, 552), (228, 662), (344, 662), smooth=False)
        .curve_to((394, 662), (434, 640), (468, 606), smooth=False)
        .line_to(500, 644)
        .curve_to((456, 682), (402, FIG_TOP), (338, FIG_TOP), smooth=True)
        .curve_to((154, FIG_TOP), (46, 548), (46, 316), smooth=True)
        .vh_to(290, FIG_BOT, 0.585, 0.58)
    )
    inner = (
        ContourBuilder((290, 40))
        .hv_to(146, 218, 0.59, 0.59)
        .vh_to(288, 392, 0.59, 0.59)
        .hv_to(418, 220, 0.59, 0.59)
        .vh_to(290, 40, 0.59, 0.59)
    )
    return [outer, inner]


def build_serif_seven(p: SerifWeightParams) -> List[ContourBuilder]:
    bh = p.fig_stem_h  # 50
    c = (
        ContourBuilder((152, 0))
        .line_to(254, 0)
        .line_to(488, FIG_CAP - 44)
        .line_to(488, FIG_CAP)
        .line_to(50, FIG_CAP)
        .line_to(40, FIG_CAP - 156)
        .line_to(76, FIG_CAP - 156)
        .curve_to((84, FIG_CAP - 80), (108, FIG_CAP - bh), (166, FIG_CAP - bh), smooth=False)
        .line_to(414, FIG_CAP - bh)
    )
    return [c]


def build_serif_eight(p: SerifWeightParams) -> List[ContourBuilder]:
    cx = 282
    outer = (
        ContourBuilder((cx, FIG_BOT))
        .hv_to(518, 182, 0.58, 0.58)
        .curve_to((518, 270), (458, 328), (368, 360), smooth=False)
        .curve_to((444, 392), (496, 446), (496, 524), smooth=False)
        .vh_to(cx, FIG_TOP, 0.58, 0.58)
        .hv_to(68, 524, 0.58, 0.58)
        .curve_to((68, 446), (120, 392), (196, 360), smooth=False)
        .curve_to((106, 328), (46, 270), (46, 182), smooth=False)
        .vh_to(cx, FIG_BOT, 0.58, 0.58)
    )
    in_top = humanist_oval_contour(cx, 526, 120, 136, 0.59, 0.59, clockwise=True)
    in_bot = humanist_oval_contour(cx, 190, 138, 150, 0.59, 0.59, clockwise=True)
    return [outer, in_top, in_bot]


def build_serif_nine(p: SerifWeightParams) -> List[ContourBuilder]:
    outer = (
        ContourBuilder((222, FIG_BOT))
        .curve_to((406, FIG_BOT), (514, 142), (514, 374), smooth=True)
        .vh_to(270, FIG_TOP, 0.585, 0.58)
        .hv_to(42, 466, 0.58, 0.585)
        .vh_to(256, 248, 0.585, 0.58)
        .curve_to((332, 248), (392, 276), (426, 328), smooth=False)
        .curve_to((416, 138), (332, 40), (216, 40), smooth=False)
        .curve_to((166, 40), (126, 54), (92, 84), smooth=False)
        .line_to(60, 46)
        .curve_to((104, 8), (158, FIG_BOT), (222, FIG_BOT), smooth=True)
    )
    inner = (
        ContourBuilder((270, 298))
        .hv_to(142, 470, 0.59, 0.59)
        .vh_to(270, 662, 0.59, 0.59)
        .hv_to(414, 472, 0.59, 0.59)
        .vh_to(270, 298, 0.59, 0.59)
    )
    return [outer, inner]


def _centered_tnum(fn: Callable[[SerifWeightParams], List[ContourBuilder]], prop_name: str):
    dx = (TABULAR_FIG_WIDTH - DUPLEX_ADVANCE_WIDTHS[prop_name]) / 2.0
    def _b(p: SerifWeightParams) -> List[ContourBuilder]:
        return [c.translated(dx, 0) for c in fn(p)]
    return _b


# ---------------------------------------------------------------------------
# Serif Special European Base Letters & Currencies
# ---------------------------------------------------------------------------

def build_serif_dotlessi(p: SerifWeightParams) -> List[ContourBuilder]:
    return [vstem_serifed(78, 170, 0, METRICS.x_height, bl=42, br=42, tl=44, tl_flag=True, sh=28, brk=32)]


def build_serif_dotlessj(p: SerifWeightParams) -> List[ContourBuilder]:
    from glyphs_serif_lc import build_j
    return build_j(p)[:-1]


def build_serif_AE(p: SerifWeightParams) -> List[ContourBuilder]:
    cap = METRICS.cap_height
    bh = p.cap_stem_h  # 50
    yb0, yb1 = 212, 262
    xl_b0 = lerp_x(98, 0, 434, 578, yb0)
    xl_b1 = lerp_x(98, 0, 434, 578, yb1)

    outer = (
        ContourBuilder((32, 0))
        .line_to(98, 0)
        .line_to(xl_b0, yb0)
        .line_to(434, yb0)
        .line_to(434, 0)
        .line_to(852, 0)
        .line_to(860, 162)
        .line_to(824, 162)
        .curve_to((816, 86), (794, bh), (736, bh), smooth=False)
        .line_to(536, bh)
        .line_to(536, 335)
        .line_to(722, 335)
        .curve_to((758, 335), (772, 318), (778, 272), smooth=False)
        .line_to(812, 272)
        .line_to(812, 448)
        .line_to(778, 448)
        .curve_to((772, 402), (758, 385), (722, 385), smooth=False)
        .line_to(536, 385)
        .line_to(536, cap - bh)
        .line_to(724, cap - bh)
        .curve_to((780, cap - bh), (802, cap - 86), (808, cap - 158), smooth=False)
        .line_to(844, cap - 158)
        .line_to(836, cap)
        .line_to(392, cap)
    )
    inner = (
        ContourBuilder((xl_b1, yb1))
        .line_to(428, 578)
        .line_to(434, 578)
        .line_to(434, yb1)
    )
    f_left = diag_foot_serif(
        32, 98, 0, lerp_x(32, 0, 392, cap, yb0), xl_b0, yb0,
        ext_l=24, ext_r=26, sh=30, brk=32,
    )
    f_mid = foot_pad_ccw(434, 536, 0, 44, 0, sh=30, brk=32)
    return union_contours([outer, inner, f_left, f_mid])


def build_serif_OE(p: SerifWeightParams) -> List[ContourBuilder]:
    cap = METRICS.cap_height
    bh = p.cap_stem_h  # 50
    outer = (
        ContourBuilder((298, -12))
        .curve_to((370, -12), (424, 14), (456, 58), smooth=False)
        .line_to(458, 0)
        .line_to(890, 0)
        .line_to(898, 162)
        .line_to(862, 162)
        .curve_to((854, 86), (832, bh), (774, bh), smooth=False)
        .line_to(558, bh)
        .line_to(558, 335)
        .line_to(756, 335)
        .curve_to((792, 335), (806, 318), (812, 272), smooth=False)
        .line_to(846, 272)
        .line_to(846, 448)
        .line_to(812, 448)
        .curve_to((806, 402), (792, 385), (756, 385), smooth=False)
        .line_to(558, 385)
        .line_to(558, cap - bh)
        .line_to(758, cap - bh)
        .curve_to((814, cap - bh), (836, cap - 86), (842, cap - 158), smooth=False)
        .line_to(878, cap - 158)
        .line_to(870, cap)
        .line_to(458, cap)
        .line_to(456, 642)
        .curve_to((424, 686), (370, 712), (298, 712), smooth=True)
        .hv_to(50, 350, 0.58, 0.59)
        .vh_to(298, -12, 0.59, 0.58)
    )
    inner = (
        ContourBuilder((312, 38))
        .hv_to(160, 350, 0.59, 0.605)
        .vh_to(312, 662, 0.605, 0.59)
        .hv_to(456, 528, 0.56, 0.56)
        .line_to(456, 172)
        .vh_to(312, 38, 0.56, 0.56)
    )
    return [outer, inner]


def build_serif_ae(p: SerifWeightParams) -> List[ContourBuilder]:
    outer = (
        ContourBuilder((208, -10))
        .curve_to((288, -10), (374, 18), (420, 76), smooth=False)
        .line_to(426, 76)
        .curve_to((468, 18), (534, -10), (616, -10), smooth=True)
        .curve_to((702, -10), (764, 26), (800, 94), smooth=False)
        .line_to(768, 124)
        .curve_to((728, 64), (674, 38), (618, 38), smooth=True)
        .curve_to((536, 38), (476, 118), (472, 240), smooth=False)
        .line_to(808, 240)
        .line_to(808, 276)
        .vh_to(610, 530, 0.58, 0.58)
        .curve_to((536, 530), (468, 500), (426, 444), smooth=False)
        .line_to(420, 444)
        .curve_to((386, 500), (328, 530), (262, 530), smooth=True)
        .hv_to(70, 418, 0.58, 0.56)
        .vh_to(114, 376, 0.58, 0.58)
        .hv_to(156, 418, 0.58, 0.58)
        .vh_to(254, 482, 0.48, 0.58)
        .hv_to(382, 356, 0.56, 0.56)
        .line_to(382, 310)
        .curve_to((266, 306), (48, 266), (48, 132), smooth=True)
        .vh_to(208, -10, 0.58, 0.58)
    )
    in_a = (
        ContourBuilder((222, 38))
        .hv_to(140, 134, 0.58, 0.58)
        .curve_to((140, 214), (260, 258), (382, 262), smooth=False)
        .line_to(382, 136)
        .vh_to(222, 38, 0.56, 0.58)
    )
    in_e = (
        ContourBuilder((472, 288))
        .line_to(472, 344)
        .vh_to(604, 482, 0.56, 0.58)
        .curve_to((672, 482), (720, 410), (726, 288), smooth=False)
    )
    return [outer, in_a, in_e]


def build_serif_oe(p: SerifWeightParams) -> List[ContourBuilder]:
    outer = (
        ContourBuilder((250, -10))
        .curve_to((328, -10), (392, 18), (430, 76), smooth=False)
        .line_to(436, 76)
        .curve_to((476, 18), (540, -10), (622, -10), smooth=True)
        .curve_to((708, -10), (770, 26), (806, 94), smooth=False)
        .line_to(774, 124)
        .curve_to((734, 64), (680, 38), (624, 38), smooth=True)
        .curve_to((542, 38), (482, 118), (478, 240), smooth=False)
        .line_to(814, 240)
        .line_to(814, 276)
        .vh_to(618, 530, 0.58, 0.58)
        .curve_to((544, 530), (476, 500), (436, 444), smooth=False)
        .line_to(430, 444)
        .curve_to((392, 500), (328, 530), (250, 530), smooth=True)
        .hv_to(48, 260, 0.58, 0.585)
        .vh_to(250, -10, 0.585, 0.58)
    )
    in_o = (
        ContourBuilder((268, 38))
        .hv_to(146, 260, 0.59, 0.605)
        .vh_to(268, 482, 0.605, 0.59)
        .hv_to(390, 340, 0.56, 0.56)
        .line_to(390, 180)
        .vh_to(268, 38, 0.56, 0.56)
    )
    in_e = (
        ContourBuilder((478, 288))
        .line_to(478, 344)
        .vh_to(612, 482, 0.56, 0.58)
        .curve_to((680, 482), (728, 410), (734, 288), smooth=False)
    )
    return [outer, in_o, in_e]


def build_serif_Oslash(p: SerifWeightParams) -> List[ContourBuilder]:
    return union_contours(build_serif_O(p) + [bar_segment_contour((92, -38), (592, 738), 50)])


def build_serif_oslash(p: SerifWeightParams) -> List[ContourBuilder]:
    return union_contours(build_serif_o(p) + [bar_segment_contour((86, -32), (494, 552), 48)])


def build_serif_Eth(p: SerifWeightParams) -> List[ContourBuilder]:
    return union_contours(build_serif_D(p) + [rect_contour(18, 330, 306, 380)])


def build_serif_dcroat(p: SerifWeightParams) -> List[ContourBuilder]:
    return union_contours(build_serif_d(p) + [rect_contour(284, 562, 554, 610)])


def build_serif_eth(p: SerifWeightParams) -> List[ContourBuilder]:
    # Literary book-serif eth (ð, w=576): 96u bowl walls / 48u crowns, clean 48u bar (2 contours!)
    outer = (
        ContourBuilder((286, -10))
        .hv_to(518, 252, 0.585, 0.585)
        .curve_to((518, 444), (410, 634), (196, 760), smooth=False)
        .line_to(146, 704)
        .curve_to((262, 628), (350, 532), (394, 422), smooth=False)
        .curve_to((358, 464), (304, 484), (244, 484), smooth=False)
        .hv_to(52, 240, 0.585, 0.585)
        .vh_to(286, -10, 0.585, 0.585)
    )
    inner = (
        ContourBuilder((282, 38))
        .hv_to(148, 242, 0.59, 0.605)
        .vh_to(272, 434, 0.605, 0.59)
        .hv_to(422, 252, 0.58, 0.58)
        .vh_to(282, 38, 0.58, 0.58)
    )
    cross = bar_segment_contour((188, 566), (456, 698), 48)
    return union_contours([outer, inner, cross])


def build_serif_Thorn(p: SerifWeightParams) -> List[ContourBuilder]:
    cap = METRICS.cap_height
    xl0, xl1 = 82, 184
    bh = p.cap_stem_h  # 50
    stem = vstem_serifed(xl0, xl1, 0, cap, bl=48, br=56, tl=48, tr=56, sh=30, brk=34)
    bowl_out = (
        ContourBuilder((140, 172))
        .line_to(316, 172)
        .hv_to(546, 378, 0.58, 0.58)
        .vh_to(316, 584, 0.58, 0.58)
        .line_to(140, 584)
    )
    bowl_in = (
        ContourBuilder((xl1, 172 + bh))
        .line_to(xl1, 584 - bh)
        .line_to(306, 584 - bh)
        .hv_to(438, 378, 0.59, 0.59)
        .vh_to(306, 172 + bh, 0.59, 0.59)
    )
    return union_contours([bowl_out, bowl_in, stem])


def build_serif_thorn(p: SerifWeightParams) -> List[ContourBuilder]:
    asc = METRICS.ascender
    desc = METRICS.descender
    top = METRICS.x_height + METRICS.lc_overshoot
    bot = -METRICS.lc_overshoot
    stem = vstem_serifed(72, 164, desc, asc, bl=42, br=48, tl=44, tl_flag=True, sh=28, brk=32)
    bowl_out = (
        ContourBuilder((140, 68))
        .curve_to((182, 18), (246, bot), (326, bot), smooth=False)
        .hv_to(528, 260, 0.58, 0.585)
        .vh_to(326, top, 0.585, 0.58)
        .curve_to((248, top), (188, 500), (158, 448), smooth=False)
        .line_to(140, 448)
    )
    bowl_in = (
        ContourBuilder((306, 38))
        .hv_to(164, 180, 0.56, 0.56)
        .line_to(164, 340)
        .vh_to(306, 482, 0.56, 0.56)
        .hv_to(430, 260, 0.59, 0.605)
        .vh_to(306, 38, 0.605, 0.59)
    )
    return union_contours([bowl_out, bowl_in, stem])


def build_serif_Germandbls(p: SerifWeightParams) -> List[ContourBuilder]:
    # Editorial serifed Capital Eszett (ẞ, U+1E9E, w=668) matching cap contrast & 30u serif
    cap = METRICS.cap_height
    bh = p.cap_stem_h  # 50
    stem = vstem_serifed(82, 184, 0, cap, bl=46, br=38, tl=46, sh=30, brk=34)
    roof_bowls = (
        ContourBuilder((140, cap - bh))
        .line_to(344, cap - bh)
        .hv_to(436, 530, 0.58, 0.58)
        .curve_to((436, 456), (384, 408), (282, 378), smooth=False)
        .line_to(282, 326)
        .curve_to((424, 304), (496, 250), (496, 174), smooth=False)
        .vh_to(378, 38, 0.58, 0.58)
        .curve_to((324, 38), (272, 48), (222, 68), smooth=False)
        .line_to(206, 18)
        .curve_to((262, -2), (324, -10), (390, -10), smooth=True)
        .hv_to(602, 178, 0.58, 0.58)
        .curve_to((602, 278), (536, 340), (424, 366), smooth=False)
        .curve_to((490, 404), (528, 464), (528, 538), smooth=False)
        .curve_to((528, 624), (456, cap), (354, cap), smooth=False)
        .line_to(140, cap)
    )
    return union_contours([stem, roof_bowls])


def build_serif_germandbls(p: SerifWeightParams) -> List[ContourBuilder]:
    from glyphs_sans_latin_ext import build_germandbls
    base = build_germandbls(p)
    foot = foot_pad_ccw(76, 162, 0, ext_l=44, ext_r=0, sh=28, brk=32)
    return union_contours(base + [foot])


def build_serif_IJ(p: SerifWeightParams) -> List[ContourBuilder]:
    return build_serif_I(p) + [c.translated(286, 0) for c in build_serif_J(p)]


def build_serif_ij(p: SerifWeightParams) -> List[ContourBuilder]:
    return build_serif_i(p) + [c.translated(236, 0) for c in build_serif_j(p)]


def build_serif_kgreenlandic(p: SerifWeightParams) -> List[ContourBuilder]:
    xh = METRICS.x_height
    sL = vstem_serifed(74, 166, 0, xh, bl=42, br=34, tl=44, tl_flag=True, sh=28, brk=32)
    arms = (
        ContourBuilder((152, 224))
        .line_to(220, 284)
        .line_to(394, 0)
        .line_to(494, 0)
        .line_to(274, 342)
        .line_to(472, xh)
        .line_to(392, xh)
        .line_to(152, 294)
    )
    h_arm = diag_head_serif(
        392, 472, xh, lerp_x(392, xh, 152, 294, 342), 274, 342,
        ext_l=22, ext_r=22, sh=28, brk=28,
    )
    f_leg = diag_foot_serif(
        394, 494, 0, 220, lerp_x(494, 0, 274, 342, 284), 284,
        ext_l=18, ext_r=22, sh=28, brk=28,
    )
    return union_contours([sL, arms, h_arm, f_leg])


def build_serif_Ldot(p: SerifWeightParams) -> List[ContourBuilder]:
    return build_serif_L(p) + [humanist_oval_contour(348, 368, 48, 48, 0.62, 0.62, clockwise=False)]


def build_serif_ldot(p: SerifWeightParams) -> List[ContourBuilder]:
    return build_serif_l(p) + [humanist_oval_contour(298, 286, 46, 46, 0.62, 0.62, clockwise=False)]


def build_serif_napostrophe(p: SerifWeightParams) -> List[ContourBuilder]:
    q = [c.translated(-24, 0) for c in build_quoteright(p)]
    n = [c.translated(166, 0) for c in build_serif_n(p)]
    return q + n


def build_serif_Tbar(p: SerifWeightParams) -> List[ContourBuilder]:
    return union_contours(build_serif_T(p) + [rect_contour(122, 342, 462, 392)])


def build_serif_tbar(p: SerifWeightParams) -> List[ContourBuilder]:
    return union_contours(build_serif_t(p) + [rect_contour(42, 244, 286, 292)])


def build_serif_longs(p: SerifWeightParams) -> List[ContourBuilder]:
    # Serif long s (ſ, w=312): sweeping 92u stem, 48u top arch crown, teardrop lobe, 28u foot serif
    stem_arch = (
        ContourBuilder((104, 0))
        .line_to(196, 0)
        .line_to(196, 614)
        .vh_to(260, 706, 0.58, 0.58)
        .hv_to(276, 672, 0.55, 0.55)
        .vh_to(312, 636, 0.58, 0.58)
        .hv_to(352, 680, 0.58, 0.58)
        .vh_to(262, 754, 0.58, 0.58)
        .hv_to(104, 604, 0.58, 0.58)
    )
    l_stub = rect_contour(36, 472, 160, METRICS.x_height)
    foot = foot_pad_ccw(104, 196, 0, ext_l=46, ext_r=58, sh=28, brk=32)
    return union_contours([stem_arch, l_stub, foot])


def build_serif_Lslash(p: SerifWeightParams) -> List[ContourBuilder]:
    return union_contours(build_serif_L(p) + [bar_segment_contour((18, 258), (274, 444), 50)])


def build_serif_lslash(p: SerifWeightParams) -> List[ContourBuilder]:
    l_base = [c.translated(10, 0) for c in build_serif_l(p)]
    return union_contours(l_base + [bar_segment_contour((18, 310), (258, 468), 48)])


def build_serif_Hbar(p: SerifWeightParams) -> List[ContourBuilder]:
    return union_contours(build_serif_H(p) + [rect_contour(24, 510, 656, 560)])


def build_serif_hbar(p: SerifWeightParams) -> List[ContourBuilder]:
    return union_contours(build_serif_h(p) + [rect_contour(18, 568, 292, 616)])


def build_serif_dollar(p: SerifWeightParams) -> List[ContourBuilder]:
    s_scaled = [c.translated(6, 0) for c in build_serif_S(p)]
    bar = rect_contour(265, -92, 315, 784)  # 50u slender vertical bar
    return union_contours(s_scaled + [bar])


def build_serif_cent(p: SerifWeightParams) -> List[ContourBuilder]:
    c_shifted = [c.translated(10, 0) for c in build_serif_c(p)]
    bar = rect_contour(262, -96, 310, 616)  # 48u slender vertical bar
    return union_contours(c_shifted + [bar])


def build_serif_euro(p: SerifWeightParams) -> List[ContourBuilder]:
    top, bot = 700, -10
    c_body = (
        ContourBuilder((372, bot))
        .curve_to((456, bot), (526, 20), (568, 78), smooth=False)
        .line_to(536, 112)
        .curve_to((496, 62), (442, 38), (376, 38), smooth=True)
        .hv_to(196, 345, 0.59, 0.605)
        .vh_to(376, 652, 0.605, 0.59)
        .curve_to((446, 652), (498, 616), (518, 536), smooth=False)
        .line_to(554, 536)
        .line_to(562, 694)
        .line_to(526, 694)
        .line_to(516, 662)
        .curve_to((476, 688), (426, top), (372, top), smooth=False)
        .hv_to(90, 345, 0.585, 0.595)
        .vh_to(372, bot, 0.595, 0.585)
    )
    b1 = rect_contour(28, 256, 444, 304)
    b2 = rect_contour(28, 392, 464, 440)
    return union_contours([c_body, b1, b2])


def build_serif_sterling(p: SerifWeightParams) -> List[ContourBuilder]:
    bh = p.fig_stem_h  # 50
    body = (
        ContourBuilder((48, 0))
        .line_to(522, 0)
        .line_to(532, 152)
        .line_to(496, 152)
        .curve_to((488, 82), (464, bh), (408, bh), smooth=False)
        .line_to(206, bh)
        .curve_to((228, 134), (240, 208), (240, 296), smooth=False)
        .line_to(240, 494)
        .vh_to(350, 652, 0.58, 0.58)
        .curve_to((404, 652), (446, 628), (476, 578), smooth=False)
        .line_to(518, 614)
        .curve_to((478, 672), (418, 700), (344, 700), smooth=True)
        .hv_to(142, 492, 0.58, 0.58)
        .line_to(142, 290)
        .curve_to((142, 198), (122, 118), (48, 42), smooth=False)
    )
    cross = rect_contour(52, 362, 328, 412)
    return union_contours([body, cross])


def build_serif_yen(p: SerifWeightParams) -> List[ContourBuilder]:
    sx0, sx1 = 242, 338
    y_body = (
        ContourBuilder((sx0, 0))
        .line_to(sx1, 0)
        .line_to(sx1, 316)
        .line_to(536, 690)
        .line_to(478, 690)
        .line_to(298, 388)
        .line_to(288, 388)
        .line_to(128, 690)
        .line_to(28, 690)
        .line_to(sx0, 316)
    )
    foot = foot_pad_ccw(sx0, sx1, 0, 62, 62, sh=30, brk=32)
    h_tl = diag_head_serif(
        28, 128, 690, lerp_x(28, 690, sx0, 316, 388), 288, 388,
        ext_l=22, ext_r=22, sh=30, brk=30,
    )
    h_tr = diag_head_serif(
        478, 536, 690, 298, lerp_x(536, 690, sx1, 316, 388), 388,
        ext_l=24, ext_r=22, sh=30, brk=30,
    )
    b1 = rect_contour(92, 154, 488, 204)
    b2 = rect_contour(92, 274, 488, 324)
    return union_contours([y_body, foot, h_tl, h_tr, b1, b2])


def build_serif_won(p: SerifWeightParams) -> List[ContourBuilder]:
    b1 = rect_contour(26, 226, 858, 276)
    b2 = rect_contour(26, 386, 858, 436)
    return union_contours(build_serif_W(p) + [b1, b2])


def build_serif_Eng(p: SerifWeightParams) -> List[ContourBuilder]:
    cap = METRICS.cap_height
    sL = vstem_serifed(84, 142, 0, cap, bl=46, br=48, tl=46, sh=30, brk=34)
    sR_top = head_pad_ccw(550, 608, cap, ext_l=46, ext_r=46, sh=30, brk=34)
    diag_hook = (
        ContourBuilder((516, 0))
        .line_to(550, 0)
        .line_to(550, -64)
        .vh_to(428, -172, 0.58, 0.58)
        .curve_to((398, -172), (372, -162), (350, -144), smooth=False)
        .line_to(326, -196)
        .curve_to((358, -218), (394, -224), (434, -224), smooth=True)
        .hv_to(608, -62, 0.58, 0.58)
        .line_to(608, cap)
        .line_to(550, cap)
        .line_to(550, 98)
        .line_to(192, cap)
        .line_to(96, cap)
    )
    return union_contours([sL, sR_top, diag_hook])


def build_serif_eng(p: SerifWeightParams) -> List[ContourBuilder]:
    xh = METRICS.x_height
    top = xh + METRICS.lc_overshoot
    sL = vstem_serifed(74, 166, 0, xh, bl=42, br=34, tl=44, tl_flag=True, sh=28, brk=32)
    arch_hook = (
        ContourBuilder((148, 344))
        .line_to(166, 344)
        .curve_to((166, 420), (226, 482), (306, 482), smooth=False)
        .hv_to(418, 330, 0.56, 0.58)
        .line_to(418, -64)
        .vh_to(324, -172, 0.58, 0.58)
        .curve_to((300, -172), (278, -164), (258, -148), smooth=False)
        .line_to(236, -198)
        .curve_to((266, -218), (298, -224), (334, -224), smooth=True)
        .hv_to(510, -62, 0.58, 0.58)
        .line_to(510, 338)
        .vh_to(328, top, 0.58, 0.58)
        .curve_to((246, top), (184, 498), (148, 438), smooth=False)
    )
    return union_contours([sL, arch_hook])


SERIF_FIG_PUNCT_OVERRIDES: Dict[str, Callable[[SerifWeightParams], List[ContourBuilder]]] = {
    "zero": build_serif_zero,
    "one": build_serif_one,
    "two": build_serif_two,
    "three": build_serif_three,
    "four": build_serif_four,
    "five": build_serif_five,
    "six": build_serif_six,
    "seven": build_serif_seven,
    "eight": build_serif_eight,
    "nine": build_serif_nine,
    "zero.tnum": _centered_tnum(build_serif_zero, "zero"),
    "one.tnum": build_serif_one_tnum,
    "two.tnum": _centered_tnum(build_serif_two, "two"),
    "three.tnum": _centered_tnum(build_serif_three, "three"),
    "four.tnum": _centered_tnum(build_serif_four, "four"),
    "five.tnum": _centered_tnum(build_serif_five, "five"),
    "six.tnum": _centered_tnum(build_serif_six, "six"),
    "seven.tnum": _centered_tnum(build_serif_seven, "seven"),
    "eight.tnum": _centered_tnum(build_serif_eight, "eight"),
    "nine.tnum": _centered_tnum(build_serif_nine, "nine"),
    "zero.slash": build_serif_zero_slash,
    "zero.tnum.slash": _centered_tnum(build_serif_zero_slash, "zero.slash"),
    "dollar": build_serif_dollar,
    "cent": build_serif_cent,
    "euro": build_serif_euro,
    "sterling": build_serif_sterling,
    "yen": build_serif_yen,
}

SERIF_EXT_OVERRIDES: Dict[str, Callable[[SerifWeightParams], List[ContourBuilder]]] = {
    "dotlessi": build_serif_dotlessi,
    "dotlessj": build_serif_dotlessj,
    "AE": build_serif_AE,
    "ae": build_serif_ae,
    "OE": build_serif_OE,
    "oe": build_serif_oe,
    "Oslash": build_serif_Oslash,
    "oslash": build_serif_oslash,
    "Eth": build_serif_Eth,
    "eth": build_serif_eth,
    "Dcroat": build_serif_Eth,
    "dcroat": build_serif_dcroat,
    "Thorn": build_serif_Thorn,
    "thorn": build_serif_thorn,
    "Germandbls": build_serif_Germandbls,
    "germandbls": build_serif_germandbls,
    "IJ": build_serif_IJ,
    "ij": build_serif_ij,
    "kgreenlandic": build_serif_kgreenlandic,
    "Ldot": build_serif_Ldot,
    "ldot": build_serif_ldot,
    "napostrophe": build_serif_napostrophe,
    "Lslash": build_serif_Lslash,
    "lslash": build_serif_lslash,
    "Hbar": build_serif_Hbar,
    "hbar": build_serif_hbar,
    "Tbar": build_serif_Tbar,
    "tbar": build_serif_tbar,
    "longs": build_serif_longs,
    "Eng": build_serif_Eng,
    "eng": build_serif_eng,
    "won": build_serif_won,
    "onesuperior": lambda p: _scale_contours(build_serif_one(p), 0.64, 0.60, 26, 296),
    "twosuperior": lambda p: _scale_contours(build_serif_two(p), 0.62, 0.58, 20, 304),
    "threesuperior": lambda p: _scale_contours(build_serif_three(p), 0.62, 0.58, 20, 304),
    "onequarter": lambda p: _fraction_glyph(build_serif_one, build_serif_four, p),
    "onehalf": lambda p: _fraction_glyph(build_serif_one, build_serif_two, p),
    "threequarters": lambda p: _fraction_glyph(build_serif_three, build_serif_four, p),
}


def build_all_serif_glyphs(
    params: SerifWeightParams = SERIF_REGULAR,
) -> Dict[str, Tuple[int, int | None, List[ContourBuilder]]]:
    """Build all 415 Admiralty Serif Regular contour glyphs with 1:1 duplex advance widths."""
    core_map: Dict[str, Callable] = {
        **FIG_PUNCT_GLYPH_BUILDERS,
        **SERIF_CAP_BUILDERS,
        **SERIF_LC_BUILDERS,
        **SERIF_FIG_PUNCT_OVERRIDES,
    }

    result: Dict[str, Tuple[int, int | None, List[ContourBuilder]]] = {}
    for gname, width in DUPLEX_ADVANCE_WIDTHS.items():
        uni = UNICODE_MAP.get(gname)
        contours = core_map[gname](params)
        result[gname] = (width, uni, contours)

    for gname, (width, uni, sans_builder) in EXT_CONTOUR_BUILDERS.items():
        builder = SERIF_EXT_OVERRIDES.get(gname, sans_builder)
        contours = builder(params)
        result[gname] = (width, uni, contours)

    return result
