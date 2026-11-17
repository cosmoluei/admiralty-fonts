"""
Proportional & tabular lining numerals (0-9), slashed zero variants, Basic Latin
ASCII punctuation/symbols, smart typography, currencies, and case-sensitive (.case)
variants for Admiralty Sans Regular (1000 UPM).
"""

from __future__ import annotations
import math
from typing import Callable, Dict, List

from design_system import (
    ContourBuilder,
    DUPLEX_ADVANCE_WIDTHS,
    METRICS,
    SansWeightParams,
    TABULAR_FIG_WIDTH,
    bar_segment_contour,
    humanist_oval_contour,
    rect_contour,
    union_contours,
)

FIG_CAP = 690
FIG_TOP = 700
FIG_BOT = -10


# ---------------------------------------------------------------------------
# Numerals 0-9 (Proportional Default)
# ---------------------------------------------------------------------------

def _zero_rings(p: SansWeightParams) -> List[ContourBuilder]:
    cx, cy = 282, 345
    rx_out, ry_out = 226, 355  # x: 56..508 (452u wide vs Cap O 572u), y: -10..700
    rx_in = rx_out - p.fig_bowl_v   # 134
    ry_in = ry_out - p.fig_stem_h   # 279
    return [
        humanist_oval_contour(cx, cy, rx_out, ry_out, 0.585, 0.59, clockwise=False),
        humanist_oval_contour(cx, cy, rx_in, ry_in, 0.605, 0.605, clockwise=True),
    ]


def build_zero(p: SansWeightParams) -> List[ContourBuilder]:
    # Distinctly narrower than Cap O (452u vs 572u) + subtle humanist center dot
    # so "O0" is unmistakable at 12-14 px while staying quiet in "$1,250.00".
    rings = _zero_rings(p)
    dot = humanist_oval_contour(282, 345, 31, 34, 0.60, 0.60, clockwise=False)
    return [rings[0], rings[1], dot]


def build_zero_slash(p: SansWeightParams) -> List[ContourBuilder]:
    rings = _zero_rings(p)
    slash = bar_segment_contour((146, 98), (418, 592), 58)
    return union_contours([rings[0], rings[1], slash])


def build_one(p: SansWeightParams) -> List[ContourBuilder]:
    # Centered inside duplex width 436 with calm horizontal base (Fix #6: evens out 2011 / 1,111)
    bh = 74
    c = (
        ContourBuilder((72, 0))
        .line_to(368, 0)
        .line_to(368, bh)
        .line_to(268, bh)
        .line_to(268, FIG_CAP)
        .line_to(194, FIG_CAP)
        .line_to(66, 578)
        .line_to(98, 518)
        .line_to(180, 588)
        .line_to(180, bh)
        .line_to(72, bh)
    )
    return [c]


def build_one_tnum(p: SansWeightParams) -> List[ContourBuilder]:
    # Centered inside w=580 with a calm horizontal base for clean numeric columns
    bh = 74
    c = (
        ContourBuilder((138, 0))
        .line_to(446, 0)
        .line_to(446, bh)
        .line_to(338, bh)
        .line_to(338, FIG_CAP)
        .line_to(262, FIG_CAP)
        .line_to(118, 572)
        .line_to(154, 508)
        .line_to(250, 590)
        .line_to(250, bh)
        .line_to(138, bh)
    )
    return [c]


def build_two(p: SansWeightParams) -> List[ContourBuilder]:
    bh = p.fig_stem_h  # 76
    c = (
        ContourBuilder((48, 0))
        .line_to(498, 0)
        .line_to(498, bh)
        .line_to(172, bh)
        .curve_to((312, 212), (484, 352), (484, 508), smooth=False)
        .vh_to(274, FIG_TOP, 0.58, 0.58)
        .curve_to((182, FIG_TOP), (108, 662), (56, 592), smooth=False)
        .line_to(116, 538)
        .curve_to((156, 594), (208, 624), (270, 624), smooth=True)
        .hv_to(394, 504, 0.58, 0.58)
        .curve_to((394, 378), (236, 246), (48, 66), smooth=False)
    )
    return [c]


def build_three(p: SansWeightParams) -> List[ContourBuilder]:
    c = (
        ContourBuilder((264, FIG_BOT))
        .hv_to(500, 186, 0.58, 0.58)
        .curve_to((500, 282), (442, 344), (356, 364), smooth=False)
        .curve_to((430, 386), (478, 444), (478, 526), smooth=False)
        .vh_to(268, FIG_TOP, 0.58, 0.58)
        .curve_to((180, FIG_TOP), (108, 666), (58, 604), smooth=False)
        .line_to(116, 548)
        .curve_to((154, 598), (204, 624), (264, 624), smooth=True)
        .hv_to(388, 518, 0.58, 0.58)
        .vh_to(246, 400, 0.58, 0.58)
        .line_to(192, 400)
        .line_to(192, 328)
        .line_to(252, 328)
        .hv_to(408, 192, 0.58, 0.58)
        .vh_to(262, 66, 0.58, 0.58)
        .curve_to((192, 66), (136, 94), (96, 144), smooth=False)
        .line_to(38, 88)
        .curve_to((90, 22), (168, FIG_BOT), (264, FIG_BOT), smooth=True)
    )
    return [c]


def build_four(p: SansWeightParams) -> List[ContourBuilder]:
    outer = (
        ContourBuilder((352, 0))
        .line_to(438, 0)
        .line_to(438, 172)
        .line_to(532, 172)
        .line_to(532, 246)
        .line_to(438, 246)
        .line_to(438, FIG_CAP)
        .line_to(336, FIG_CAP)
        .line_to(34, 234)
        .line_to(34, 172)
        .line_to(352, 172)
    )
    inner = (
        ContourBuilder((126, 246))
        .line_to(346, 588)
        .line_to(352, 588)
        .line_to(352, 246)
    )
    return [outer, inner]


def build_five(p: SansWeightParams) -> List[ContourBuilder]:
    c = (
        ContourBuilder((264, FIG_BOT))
        .hv_to(500, 220, 0.58, 0.58)
        .vh_to(278, 446, 0.58, 0.58)
        .curve_to((232, 446), (192, 436), (160, 418), smooth=False)
        .line_to(176, 614)
        .line_to(474, 614)
        .line_to(474, FIG_CAP)
        .line_to(102, FIG_CAP)
        .line_to(80, 344)
        .line_to(142, 316)
        .curve_to((178, 354), (218, 372), (266, 372), smooth=False)
        .hv_to(408, 218, 0.58, 0.58)
        .vh_to(262, 66, 0.58, 0.58)
        .curve_to((194, 66), (138, 92), (98, 138), smooth=False)
        .line_to(42, 80)
        .curve_to((94, 18), (172, FIG_BOT), (264, FIG_BOT), smooth=True)
    )
    return [c]


def build_six(p: SansWeightParams) -> List[ContourBuilder]:
    outer = (
        ContourBuilder((290, FIG_BOT))
        .hv_to(512, 224, 0.585, 0.585)
        .vh_to(304, 446, 0.585, 0.585)
        .curve_to((232, 446), (176, 420), (140, 372), smooth=False)
        .curve_to((148, 536), (226, 626), (336, 626), smooth=False)
        .curve_to((384, 626), (424, 610), (458, 582), smooth=False)
        .line_to(504, 646)
        .curve_to((458, 682), (402, FIG_TOP), (336, FIG_TOP), smooth=True)
        .curve_to((158, FIG_TOP), (52, 548), (52, 316), smooth=True)
        .vh_to(290, FIG_BOT, 0.585, 0.585)
    )
    inner = (
        ContourBuilder((290, 64))
        .hv_to(146, 218, 0.59, 0.59)
        .vh_to(288, 374, 0.59, 0.59)
        .hv_to(422, 220, 0.59, 0.59)
        .vh_to(290, 64, 0.59, 0.59)
    )
    return [outer, inner]


def build_seven(p: SansWeightParams) -> List[ContourBuilder]:
    bh = p.fig_stem_h  # 76
    c = (
        ContourBuilder((156, 0))
        .line_to(252, 0)
        .line_to(486, FIG_CAP - bh + 12)
        .line_to(486, FIG_CAP)
        .line_to(46, FIG_CAP)
        .line_to(46, FIG_CAP - bh)
        .line_to(388, FIG_CAP - bh)
    )
    return [c]


def build_eight(p: SansWeightParams) -> List[ContourBuilder]:
    cx = 282
    outer = (
        ContourBuilder((cx, FIG_BOT))
        .hv_to(512, 182, 0.58, 0.58)
        .curve_to((512, 268), (458, 326), (376, 358), smooth=False)
        .curve_to((446, 390), (490, 444), (490, 522), smooth=False)
        .vh_to(cx, FIG_TOP, 0.58, 0.58)
        .hv_to(74, 522, 0.58, 0.58)
        .curve_to((74, 444), (118, 390), (188, 358), smooth=False)
        .curve_to((106, 326), (52, 268), (52, 182), smooth=False)
        .vh_to(cx, FIG_BOT, 0.58, 0.58)
    )
    inner_top = humanist_oval_contour(cx, 514, 120, 114, 0.59, 0.59, clockwise=True)
    inner_bot = humanist_oval_contour(cx, 190, 138, 126, 0.59, 0.59, clockwise=True)
    return [outer, inner_top, inner_bot]


def build_nine(p: SansWeightParams) -> List[ContourBuilder]:
    # Rotational humanist sibling of 6 around (280, 345)
    outer = (
        ContourBuilder((224, FIG_BOT))
        .curve_to((402, FIG_BOT), (508, 142), (508, 374), smooth=True)
        .vh_to(270, FIG_TOP, 0.585, 0.585)
        .hv_to(48, 466, 0.585, 0.585)
        .vh_to(256, 244, 0.585, 0.585)
        .curve_to((328, 244), (384, 270), (420, 318), smooth=False)
        .curve_to((412, 154), (334, 64), (224, 64), smooth=False)
        .curve_to((176, 64), (136, 80), (102, 108), smooth=False)
        .line_to(56, 44)
        .curve_to((102, 8), (158, FIG_BOT), (224, FIG_BOT), smooth=True)
    )
    inner = (
        ContourBuilder((270, 316))
        .hv_to(138, 470, 0.59, 0.59)
        .vh_to(270, 626, 0.59, 0.59)
        .hv_to(414, 472, 0.59, 0.59)
        .vh_to(270, 316, 0.59, 0.59)
    )
    return [outer, inner]


def _centered_tabular(
    prop_builder: Callable[[SansWeightParams], List[ContourBuilder]],
    prop_name: str,
) -> Callable[[SansWeightParams], List[ContourBuilder]]:
    dx = (TABULAR_FIG_WIDTH - DUPLEX_ADVANCE_WIDTHS[prop_name]) / 2.0

    def _builder(p: SansWeightParams) -> List[ContourBuilder]:
        return [c.translated(dx, 0) for c in prop_builder(p)]

    return _builder


# ---------------------------------------------------------------------------
# Punctuation, Brackets, Math & Currency Symbols
# ---------------------------------------------------------------------------

def _dot_squircle(cx: float, cy: float, r: float = 54.0) -> ContourBuilder:
    return humanist_oval_contour(cx, cy, r, r, 0.62, 0.62, clockwise=False)


def _comma_shape(cx: float, top_y: float) -> ContourBuilder:
    """Calm humanist comma/quote tail: clear squircle head + tapered downward curve."""
    # Head spans top_y-102..top_y, tail sweeps down to top_y-236
    y_mid = top_y - 52
    return (
        ContourBuilder((cx - 26, top_y - 236))
        .curve_to((cx + 28, top_y - 208), (cx + 54, top_y - 144), (cx + 54, y_mid), smooth=True)
        .vh_to(cx, top_y, 0.60, 0.60)
        .hv_to(cx - 52, y_mid, 0.60, 0.60)
        .vh_to(cx - 6, top_y - 102, 0.58, 0.58)
        .curve_to((cx - 8, top_y - 144), (cx - 26, top_y - 178), (cx - 56, top_y - 202), smooth=False)
    )


def build_period(p: SansWeightParams) -> List[ContourBuilder]:
    return [_dot_squircle(124, 52, 54)]


def build_comma(p: SansWeightParams) -> List[ContourBuilder]:
    return [_comma_shape(128, 106)]


def build_colon(p: SansWeightParams) -> List[ContourBuilder]:
    return [_dot_squircle(128, 52, 54), _dot_squircle(128, 424, 54)]


def build_semicolon(p: SansWeightParams) -> List[ContourBuilder]:
    return [_comma_shape(130, 106), _dot_squircle(128, 424, 54)]


def build_periodcentered(p: SansWeightParams) -> List[ContourBuilder]:
    return [_dot_squircle(130, 268, 54)]


def build_ellipsis(p: SansWeightParams) -> List[ContourBuilder]:
    return [
        _dot_squircle(124, 52, 52),
        _dot_squircle(360, 52, 52),
        _dot_squircle(596, 52, 52),
    ]


def build_bullet(p: SansWeightParams) -> List[ContourBuilder]:
    return [humanist_oval_contour(180, 276, 98, 98, 0.60, 0.60, clockwise=False)]


def build_exclam(p: SansWeightParams) -> List[ContourBuilder]:
    cap = METRICS.cap_height
    stem = (
        ContourBuilder((100, 186))
        .line_to(176, 186)
        .line_to(184, 490)
        .line_to(184, cap)
        .line_to(92, cap)
        .line_to(92, 490)
    )
    return [stem, _dot_squircle(138, 52, 54)]


def build_question(p: SansWeightParams) -> List[ContourBuilder]:
    top = METRICS.cap_height + METRICS.cap_overshoot  # 712
    stem = (
        ContourBuilder((186, 188))
        .line_to(272, 188)
        .line_to(272, 252)
        .curve_to((272, 316), (308, 352), (366, 398), smooth=False)
        .curve_to((416, 438), (442, 484), (442, 544), smooth=True)
        .vh_to(244, top, 0.58, 0.58)
        .curve_to((154, top), (84, 678), (38, 614), smooth=False)
        .line_to(98, 560)
        .curve_to((136, 610), (184, 636), (242, 636), smooth=True)
        .hv_to(350, 536, 0.58, 0.58)
        .curve_to((350, 492), (328, 460), (278, 420), smooth=True)
        .curve_to((212, 368), (186, 322), (186, 246), smooth=False)
    )
    return [stem, _dot_squircle(229, 52, 54)]


def build_quotesingle(p: SansWeightParams) -> List[ContourBuilder]:
    cap = METRICS.cap_height
    c = (
        ContourBuilder((82, 446))
        .line_to(146, 446)
        .line_to(156, cap)
        .line_to(72, cap)
    )
    return [c]


def build_quotedbl(p: SansWeightParams) -> List[ContourBuilder]:
    s = build_quotesingle(p)[0]
    return [s.translated(-8, 0), s.translated(148, 0)]


def build_quoteright(p: SansWeightParams) -> List[ContourBuilder]:
    return [_comma_shape(126, 706)]


def build_quoteleft(p: SansWeightParams) -> List[ContourBuilder]:
    # 180-degree rotated sibling of quoteright around (122, 588)
    cx, bot_y = 118, 470
    y_mid = bot_y + 52
    c = (
        ContourBuilder((cx + 26, bot_y + 236))
        .curve_to((cx - 28, bot_y + 208), (cx - 54, bot_y + 144), (cx - 54, y_mid), smooth=True)
        .vh_to(cx, bot_y, 0.60, 0.60)
        .hv_to(cx + 52, y_mid, 0.60, 0.60)
        .vh_to(cx + 6, bot_y + 102, 0.58, 0.58)
        .curve_to((cx + 8, bot_y + 144), (cx + 26, bot_y + 178), (cx + 56, bot_y + 202), smooth=False)
    )
    return [c]


def build_quotedblleft(p: SansWeightParams) -> List[ContourBuilder]:
    q = build_quoteleft(p)[0]
    return [q.translated(-6, 0), q.translated(174, 0)]


def build_quotedblright(p: SansWeightParams) -> List[ContourBuilder]:
    q = build_quoteright(p)[0]
    return [q.translated(-10, 0), q.translated(170, 0)]


def build_grave(p: SansWeightParams) -> List[ContourBuilder]:
    c = (
        ContourBuilder((168, 548))
        .line_to(226, 548)
        .line_to(146, 714)
        .line_to(72, 714)
    )
    return [c]


def build_hyphen(p: SansWeightParams) -> List[ContourBuilder]:
    return [rect_contour(52, 232, 308, 304)]


def build_endash(p: SansWeightParams) -> List[ContourBuilder]:
    return [rect_contour(44, 234, 516, 302)]


def build_emdash(p: SansWeightParams) -> List[ContourBuilder]:
    return [rect_contour(36, 234, 884, 302)]


def build_underscore(p: SansWeightParams) -> List[ContourBuilder]:
    return [rect_contour(16, -124, 504, -54)]


def build_parenleft(p: SansWeightParams) -> List[ContourBuilder]:
    c = (
        ContourBuilder((228, -136))
        .line_to(290, -104)
        .curve_to((198, 22), (156, 152), (156, 304), smooth=True)
        .curve_to((156, 456), (198, 586), (290, 712), smooth=True)
        .line_to(228, 744)
        .curve_to((118, 608), (68, 464), (68, 304), smooth=True)
        .curve_to((68, 144), (118, 0), (228, -136), smooth=True)
    )
    return [c]


def build_parenright(p: SansWeightParams) -> List[ContourBuilder]:
    w = DUPLEX_ADVANCE_WIDTHS["parenright"]  # 336
    c = (
        ContourBuilder((w - 228, 744))
        .line_to(w - 290, 712)
        .curve_to((w - 198, 586), (w - 156, 456), (w - 156, 304), smooth=True)
        .curve_to((w - 156, 152), (w - 198, 22), (w - 290, -104), smooth=True)
        .line_to(w - 228, -136)
        .curve_to((w - 118, 0), (w - 68, 144), (w - 68, 304), smooth=True)
        .curve_to((w - 68, 464), (w - 118, 608), (w - 228, 744), smooth=True)
    )
    return [c]


def build_bracketleft(p: SansWeightParams) -> List[ContourBuilder]:
    c = (
        ContourBuilder((82, -132))
        .line_to(278, -132)
        .line_to(278, -64)
        .line_to(162, -64)
        .line_to(162, 672)
        .line_to(278, 672)
        .line_to(278, 740)
        .line_to(82, 740)
    )
    return [c]


def build_bracketright(p: SansWeightParams) -> List[ContourBuilder]:
    w = DUPLEX_ADVANCE_WIDTHS["bracketright"]  # 336
    c = (
        ContourBuilder((w - 278, -132))
        .line_to(w - 82, -132)
        .line_to(w - 82, 740)
        .line_to(w - 278, 740)
        .line_to(w - 278, 672)
        .line_to(w - 162, 672)
        .line_to(w - 162, -64)
        .line_to(w - 278, -64)
    )
    return [c]


def build_braceleft(p: SansWeightParams) -> List[ContourBuilder]:
    c = (
        ContourBuilder((246, -132))
        .line_to(302, -132)
        .line_to(302, -66)
        .line_to(258, -66)
        .hv_to(196, 12, 0.58, 0.58)
        .line_to(196, 206)
        .vh_to(118, 304, 0.58, 0.58)
        .hv_to(196, 402, 0.58, 0.58)
        .line_to(196, 596)
        .vh_to(258, 674, 0.58, 0.58)
        .line_to(302, 674)
        .line_to(302, 740)
        .line_to(246, 740)
        .hv_to(118, 608, 0.58, 0.58)
        .line_to(118, 412)
        .vh_to(48, 336, 0.58, 0.58)
        .line_to(48, 272)
        .hv_to(118, 196, 0.58, 0.58)
        .line_to(118, 0)
        .vh_to(246, -132, 0.58, 0.58)
    )
    return [c]


def build_braceright(p: SansWeightParams) -> List[ContourBuilder]:
    w = DUPLEX_ADVANCE_WIDTHS["braceright"]  # 368
    c = (
        ContourBuilder((w - 302, -132))
        .line_to(w - 246, -132)
        .hv_to(w - 118, 0, 0.58, 0.58)
        .line_to(w - 118, 196)
        .vh_to(w - 48, 272, 0.58, 0.58)
        .line_to(w - 48, 336)
        .hv_to(w - 118, 412, 0.58, 0.58)
        .line_to(w - 118, 608)
        .vh_to(w - 246, 740, 0.58, 0.58)
        .line_to(w - 302, 740)
        .line_to(w - 302, 674)
        .line_to(w - 258, 674)
        .hv_to(w - 196, 596, 0.58, 0.58)
        .line_to(w - 196, 402)
        .vh_to(w - 118, 304, 0.58, 0.58)
        .hv_to(w - 196, 206, 0.58, 0.58)
        .line_to(w - 196, 12)
        .vh_to(w - 258, -66, 0.58, 0.58)
        .line_to(w - 302, -66)
    )
    return [c]


def build_slash(p: SansWeightParams) -> List[ContourBuilder]:
    return [
        ContourBuilder((28, -110))
        .line_to(102, -110)
        .line_to(360, 740)
        .line_to(286, 740)
    ]


def build_backslash(p: SansWeightParams) -> List[ContourBuilder]:
    return [
        ContourBuilder((286, -110))
        .line_to(360, -110)
        .line_to(102, 740)
        .line_to(28, 740)
    ]


def build_bar(p: SansWeightParams) -> List[ContourBuilder]:
    return [rect_contour(104, -140, 176, 750)]


def build_plus(p: SansWeightParams) -> List[ContourBuilder]:
    h_bar = rect_contour(68, 240, 512, 312)
    v_bar = rect_contour(254, 54, 326, 498)
    return union_contours([h_bar, v_bar])


def build_equal(p: SansWeightParams) -> List[ContourBuilder]:
    return [
        rect_contour(68, 152, 512, 224),
        rect_contour(68, 328, 512, 400),
    ]


def build_less(p: SansWeightParams) -> List[ContourBuilder]:
    c = (
        ContourBuilder((68, 246))
        .line_to(504, 48)
        .line_to(504, 124)
        .line_to(164, 276)
        .line_to(504, 428)
        .line_to(504, 504)
        .line_to(68, 306)
    )
    return [c]


def build_greater(p: SansWeightParams) -> List[ContourBuilder]:
    c = (
        ContourBuilder((76, 48))
        .line_to(512, 246)
        .line_to(512, 306)
        .line_to(76, 504)
        .line_to(76, 428)
        .line_to(416, 276)
        .line_to(76, 124)
    )
    return [c]


def build_asciicircum(p: SansWeightParams) -> List[ContourBuilder]:
    c = (
        ContourBuilder((52, 420))
        .line_to(128, 420)
        .line_to(250, 628)
        .line_to(372, 420)
        .line_to(448, 420)
        .line_to(286, 706)
        .line_to(214, 706)
    )
    return [c]


def build_asciitilde(p: SansWeightParams) -> List[ContourBuilder]:
    c = (
        ContourBuilder((384, 198))
        .curve_to((444, 198), (492, 238), (522, 314), smooth=False)
        .line_to(460, 344)
        .curve_to((438, 290), (412, 268), (378, 268), smooth=True)
        .curve_to((340, 268), (304, 290), (262, 320), smooth=True)
        .curve_to((222, 350), (186, 368), (146, 368), smooth=True)
        .curve_to((92, 368), (52, 332), (34, 260), smooth=False)
        .line_to(96, 232)
        .curve_to((112, 278), (134, 298), (166, 298), smooth=True)
        .curve_to((200, 298), (236, 278), (278, 248), smooth=True)
        .curve_to((318, 218), (350, 198), (384, 198), smooth=True)
    )
    return [c]


def build_asterisk(p: SansWeightParams) -> List[ContourBuilder]:
    cx, cy = 210, 560
    r = 156
    arms = []
    for k in range(3):
        ang = math.pi / 2.0 + k * (math.pi / 3.0)
        dx = r * math.cos(ang)
        dy = r * math.sin(ang)
        arms.append(bar_segment_contour((cx - dx, cy - dy), (cx + dx, cy + dy), 58))
    return union_contours(arms)


def build_numbersign(p: SansWeightParams) -> List[ContourBuilder]:
    u1 = ContourBuilder((118, 0)).line_to(188, 0).line_to(254, FIG_CAP).line_to(184, FIG_CAP)
    u2 = ContourBuilder((326, 0)).line_to(396, 0).line_to(462, FIG_CAP).line_to(392, FIG_CAP)
    h1 = rect_contour(46, 188, 534, 254)
    h2 = rect_contour(46, 434, 534, 500)
    return union_contours([u1, u2, h1, h2])


def build_percent(p: SansWeightParams) -> List[ContourBuilder]:
    slash = ContourBuilder((144, -10)).line_to(212, -10).line_to(636, 700).line_to(568, 700)
    o_top_out = humanist_oval_contour(192, 532, 138, 168, 0.585, 0.585, clockwise=False)
    o_top_in = humanist_oval_contour(192, 532, 72, 108, 0.60, 0.60, clockwise=True)
    o_bot_out = humanist_oval_contour(588, 158, 138, 168, 0.585, 0.585, clockwise=False)
    o_bot_in = humanist_oval_contour(588, 158, 72, 108, 0.60, 0.60, clockwise=True)
    return [slash, o_top_out, o_top_in, o_bot_out, o_bot_in]


def build_degree(p: SansWeightParams) -> List[ContourBuilder]:
    return [
        humanist_oval_contour(190, 566, 136, 138, 0.59, 0.59, clockwise=False),
        humanist_oval_contour(190, 566, 76, 78, 0.60, 0.60, clockwise=True),
    ]


def build_ampersand(p: SansWeightParams) -> List[ContourBuilder]:
    # Classic humanist ampersand: figure-8 spine + calm upward-curving right arm
    top = METRICS.cap_height + METRICS.cap_overshoot  # 712
    bot = -METRICS.cap_overshoot                      # -12
    outer = (
        ContourBuilder((256, bot))
        .curve_to((344, bot), (416, 16), (474, 70), smooth=False)
        .line_to(538, 0)
        .line_to(638, 0)
        .line_to(528, 124)
        .curve_to((568, 184), (590, 252), (594, 326), smooth=False)
        .line_to(514, 326)
        .curve_to((510, 270), (494, 224), (468, 184), smooth=False)
        .line_to(296, 398)
        .curve_to((378, 444), (426, 500), (426, 574), smooth=False)
        .vh_to(266, top, 0.58, 0.58)
        .hv_to(104, 568, 0.58, 0.58)
        .curve_to((104, 502), (134, 448), (186, 392), smooth=False)
        .curve_to((92, 336), (44, 266), (44, 176), smooth=False)
        .vh_to(256, bot, 0.58, 0.58)
    )
    inner_top = (
        ContourBuilder((250, 446))
        .curve_to((206, 488), (186, 526), (186, 568), smooth=False)
        .vh_to(266, 642, 0.58, 0.58)
        .hv_to(346, 568, 0.58, 0.58)
        .curve_to((346, 516), (312, 476), (250, 446), smooth=False)
    )
    inner_bot = (
        ContourBuilder((260, 62))
        .hv_to(132, 180, 0.58, 0.58)
        .curve_to((132, 244), (168, 294), (236, 334), smooth=False)
        .line_to(422, 124)
        .curve_to((376, 82), (322, 62), (260, 62), smooth=False)
    )
    return [outer, inner_top, inner_bot]


def build_at(p: SansWeightParams) -> List[ContourBuilder]:
    # Clean open humanist @ spanning y: -110..700 inside w=840
    outer = (
        ContourBuilder((432, -116))
        .curve_to((522, -116), (600, -96), (664, -56), smooth=False)
        .line_to(632, 6)
        .curve_to((578, -28), (512, -46), (436, -46), smooth=True)
        .hv_to(132, 300, 0.585, 0.59)
        .vh_to(436, 632, 0.59, 0.585)
        .hv_to(720, 344, 0.585, 0.585)
        .curve_to((720, 224), (674, 160), (618, 160), smooth=True)
        .curve_to((580, 160), (562, 186), (562, 236), smooth=False)
        .line_to(562, 474)
        .line_to(490, 474)
        .line_to(488, 426)
        .curve_to((460, 464), (416, 484), (362, 484), smooth=False)
        .hv_to(218, 290, 0.585, 0.585)
        .vh_to(358, 98, 0.585, 0.585)
        .curve_to((416, 98), (464, 122), (494, 166), smooth=False)
        .curve_to((506, 118), (548, 92), (608, 92), smooth=False)
        .curve_to((714, 92), (792, 186), (792, 348), smooth=True)
        .vh_to(434, 700, 0.585, 0.585)
        .hv_to(54, 300, 0.59, 0.59)
        .vh_to(432, -116, 0.59, 0.59)
    )
    inner = (
        ContourBuilder((376, 164))
        .hv_to(294, 290, 0.59, 0.59)
        .vh_to(378, 418, 0.59, 0.59)
        .hv_to(488, 326, 0.56, 0.56)
        .line_to(488, 254)
        .vh_to(376, 164, 0.56, 0.56)
    )
    return [outer, inner]


def build_dollar(p: SansWeightParams) -> List[ContourBuilder]:
    s_glyph = [c.translated(6, 0) for c in _build_S_for_dollar(p)]
    bar = rect_contour(256, -92, 324, 784)
    return union_contours(s_glyph + [bar])


def _build_S_for_dollar(p: SansWeightParams) -> List[ContourBuilder]:
    top, bot = 700, -10
    c = (
        ContourBuilder((276, bot))
        .hv_to(506, 182, 0.58, 0.56)
        .curve_to((506, 316), (408, 360), (288, 396), smooth=True)
        .curve_to((198, 422), (164, 456), (164, 512), smooth=True)
        .vh_to(290, 626, 0.58, 0.58)
        .curve_to((360, 626), (414, 602), (456, 564), smooth=False)
        .line_to(502, 628)
        .curve_to((448, 676), (376, top), (290, top), smooth=True)
        .hv_to(70, 508, 0.58, 0.56)
        .curve_to((70, 376), (170, 332), (288, 296), smooth=True)
        .curve_to((380, 268), (414, 234), (414, 178), smooth=True)
        .vh_to(276, 64, 0.58, 0.58)
        .curve_to((194, 64), (134, 92), (90, 136), smooth=False)
        .line_to(42, 68)
        .curve_to((100, 14), (182, bot), (276, bot), smooth=True)
    )
    return [c]


def build_euro(p: SansWeightParams) -> List[ContourBuilder]:
    top, bot = 700, -10
    c_body = (
        ContourBuilder((372, bot))
        .curve_to((454, bot), (522, 20), (566, 78), smooth=False)
        .line_to(512, 134)
        .curve_to((474, 86), (428, 64), (372, 64), smooth=True)
        .hv_to(188, 345, 0.59, 0.60)
        .vh_to(372, 626, 0.60, 0.59)
        .curve_to((428, 626), (472, 604), (508, 560), smooth=False)
        .line_to(562, 616)
        .curve_to((518, 672), (452, top), (372, top), smooth=True)
        .hv_to(98, 345, 0.585, 0.59)
        .vh_to(372, bot, 0.59, 0.585)
    )
    b1 = rect_contour(28, 248, 444, 310)
    b2 = rect_contour(28, 384, 464, 446)
    return union_contours([c_body, b1, b2])


def build_sterling(p: SansWeightParams) -> List[ContourBuilder]:
    bh = 74
    body = (
        ContourBuilder((56, 0))
        .line_to(518, 0)
        .line_to(518, bh)
        .line_to(206, bh)
        .curve_to((226, 138), (234, 210), (234, 296), smooth=False)
        .line_to(234, 494)
        .vh_to(346, 624, 0.58, 0.58)
        .curve_to((398, 624), (438, 602), (468, 560), smooth=False)
        .line_to(526, 614)
        .curve_to((482, 672), (420, 700), (344, 700), smooth=True)
        .hv_to(146, 492, 0.58, 0.58)
        .line_to(146, 290)
        .curve_to((146, 198), (126, 122), (56, 56), smooth=False)
    )
    cross = rect_contour(52, 316, 412, 382)
    return union_contours([body, cross])


def build_yen(p: SansWeightParams) -> List[ContourBuilder]:
    sx0, sx1 = 248, 332
    y_body = (
        ContourBuilder((sx0, 0))
        .line_to(sx1, 0)
        .line_to(sx1, 316)
        .line_to(546, 690)
        .line_to(452, 690)
        .line_to(294, 400)
        .line_to(286, 400)
        .line_to(128, 690)
        .line_to(34, 690)
        .line_to(sx0, 316)
    )
    b1 = rect_contour(92, 148, 488, 210)
    b2 = rect_contour(92, 268, 488, 330)
    return union_contours([y_body, b1, b2])


def build_cent(p: SansWeightParams) -> List[ContourBuilder]:
    top, bot = 530, -10
    c_body = (
        ContourBuilder((296, bot))
        .curve_to((376, bot), (438, 22), (478, 82), smooth=False)
        .line_to(424, 136)
        .curve_to((392, 88), (348, 62), (298, 62), smooth=True)
        .hv_to(154, 260, 0.59, 0.60)
        .vh_to(298, 458, 0.60, 0.59)
        .curve_to((348, 458), (390, 434), (420, 390), smooth=False)
        .line_to(474, 444)
        .curve_to((434, 500), (374, top), (296, top), smooth=True)
        .hv_to(64, 260, 0.585, 0.585)
        .vh_to(296, bot, 0.585, 0.585)
    )
    bar = rect_contour(254, -96, 318, 616)
    return union_contours([c_body, bar])


def _shifted_case(
    base_builder: Callable[[SansWeightParams], List[ContourBuilder]],
    dy: float = METRICS.case_shift_y,
) -> Callable[[SansWeightParams], List[ContourBuilder]]:
    def _builder(p: SansWeightParams) -> List[ContourBuilder]:
        return [c.translated(0, dy) for c in base_builder(p)]

    return _builder


FIG_PUNCT_GLYPH_BUILDERS: Dict[str, Callable[[SansWeightParams], List[ContourBuilder]]] = {
    # Proportional lining figures
    "zero": build_zero,
    "one": build_one,
    "two": build_two,
    "three": build_three,
    "four": build_four,
    "five": build_five,
    "six": build_six,
    "seven": build_seven,
    "eight": build_eight,
    "nine": build_nine,
    # Tabular lining figures
    "zero.tnum": _centered_tabular(build_zero, "zero"),
    "one.tnum": build_one_tnum,
    "two.tnum": _centered_tabular(build_two, "two"),
    "three.tnum": _centered_tabular(build_three, "three"),
    "four.tnum": _centered_tabular(build_four, "four"),
    "five.tnum": _centered_tabular(build_five, "five"),
    "six.tnum": _centered_tabular(build_six, "six"),
    "seven.tnum": _centered_tabular(build_seven, "seven"),
    "eight.tnum": _centered_tabular(build_eight, "eight"),
    "nine.tnum": _centered_tabular(build_nine, "nine"),
    # Slashed zero variants
    "zero.slash": build_zero_slash,
    "zero.tnum.slash": _centered_tabular(build_zero_slash, "zero.slash"),
    # Punctuation & symbols
    "period": build_period,
    "comma": build_comma,
    "colon": build_colon,
    "semicolon": build_semicolon,
    "exclam": build_exclam,
    "question": build_question,
    "quotesingle": build_quotesingle,
    "quotedbl": build_quotedbl,
    "grave": build_grave,
    "asciicircum": build_asciicircum,
    "asciitilde": build_asciitilde,
    "hyphen": build_hyphen,
    "underscore": build_underscore,
    "parenleft": build_parenleft,
    "parenright": build_parenright,
    "bracketleft": build_bracketleft,
    "bracketright": build_bracketright,
    "braceleft": build_braceleft,
    "braceright": build_braceright,
    "slash": build_slash,
    "backslash": build_backslash,
    "bar": build_bar,
    "asterisk": build_asterisk,
    "plus": build_plus,
    "equal": build_equal,
    "less": build_less,
    "greater": build_greater,
    "numbersign": build_numbersign,
    "percent": build_percent,
    "ampersand": build_ampersand,
    "at": build_at,
    "dollar": build_dollar,
    "endash": build_endash,
    "emdash": build_emdash,
    "quoteleft": build_quoteleft,
    "quoteright": build_quoteright,
    "quotedblleft": build_quotedblleft,
    "quotedblright": build_quotedblright,
    "ellipsis": build_ellipsis,
    "bullet": build_bullet,
    "periodcentered": build_periodcentered,
    "degree": build_degree,
    "euro": build_euro,
    "sterling": build_sterling,
    "yen": build_yen,
    "cent": build_cent,
    # Case-sensitive punctuation (.case)
    "hyphen.case": _shifted_case(build_hyphen),
    "endash.case": _shifted_case(build_endash),
    "emdash.case": _shifted_case(build_emdash),
    "parenleft.case": _shifted_case(build_parenleft, dy=46),
    "parenright.case": _shifted_case(build_parenright, dy=46),
    "bracketleft.case": _shifted_case(build_bracketleft, dy=46),
    "bracketright.case": _shifted_case(build_bracketright, dy=46),
    "braceleft.case": _shifted_case(build_braceleft, dy=46),
    "braceright.case": _shifted_case(build_braceright, dy=46),
    "colon.case": _shifted_case(build_colon, dy=52),
    "periodcentered.case": _shifted_case(build_periodcentered),
}
