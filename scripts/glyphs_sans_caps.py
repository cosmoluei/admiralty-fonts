"""
Uppercase A-Z glyph builders for Admiralty Sans Regular (1000 UPM).
"""

from __future__ import annotations
from typing import Callable, Dict, List

from design_system import (
    ContourBuilder,
    METRICS,
    SansWeightParams,
    bar_segment_contour,
    humanist_oval_contour,
    lerp_x,
    rect_contour,
    union_contours,
)


def build_notdef(p: SansWeightParams) -> List[ContourBuilder]:
    return [
        rect_contour(80, 0, 520, 700, clockwise=False),
        rect_contour(144, 64, 456, 636, clockwise=True),
    ]


def build_space(p: SansWeightParams) -> List[ContourBuilder]:
    return []


def build_A(p: SansWeightParams) -> List[ContourBuilder]:
    cap = METRICS.cap_height
    yb0, yb1 = 194, 266
    xl_b0 = lerp_x(122, 0, 314, 576, yb0)
    xr_b0 = lerp_x(508, 0, 322, 576, yb0)
    xl_b1 = lerp_x(122, 0, 314, 576, yb1)
    xr_b1 = lerp_x(508, 0, 322, 576, yb1)

    outer = (
        ContourBuilder((28, 0))
        .line_to(122, 0)
        .line_to(xl_b0, yb0)
        .line_to(xr_b0, yb0)
        .line_to(508, 0)
        .line_to(608, 0)
        .line_to(366, cap)
        .line_to(270, cap)
    )
    inner = (
        ContourBuilder((xl_b1, yb1))
        .line_to(314, 576)
        .line_to(322, 576)
        .line_to(xr_b1, yb1)
    )
    return [outer, inner]


def build_B(p: SansWeightParams) -> List[ContourBuilder]:
    cap = METRICS.cap_height  # 700
    xl0, xl1 = 82, 82 + p.cap_stem_v  # 82..174
    outer = (
        ContourBuilder((xl0, 0))
        .line_to(336, 0)
        .hv_to(560, 192, 0.58, 0.58)
        .curve_to((560, 290), (500, 350), (416, 366), smooth=False)
        .curve_to((488, 386), (534, 442), (534, 528), smooth=False)
        .vh_to(322, cap, 0.58, 0.58)
        .line_to(xl0, cap)
    )
    inner_top = (
        ContourBuilder((xl1, 398))
        .line_to(xl1, 624)
        .line_to(310, 624)
        .hv_to(440, 511, 0.58, 0.58)
        .vh_to(312, 398, 0.58, 0.58)
    )
    inner_bot = (
        ContourBuilder((xl1, 76))
        .line_to(xl1, 326)
        .line_to(326, 326)
        .hv_to(464, 200, 0.58, 0.58)
        .vh_to(328, 76, 0.58, 0.58)
    )
    return [outer, inner_top, inner_bot]


def build_C(p: SansWeightParams) -> List[ContourBuilder]:
    top = METRICS.cap_height + METRICS.cap_overshoot  # 712
    bot = -METRICS.cap_overshoot                      # -12
    c = (
        ContourBuilder((356, bot))
        .curve_to((454, bot), (534, 24), (586, 94), smooth=False)
        .line_to(526, 152)
        .curve_to((482, 94), (424, 66), (358, 66), smooth=True)
        .hv_to(152, 350, 0.59, 0.60)
        .vh_to(358, 634, 0.60, 0.59)
        .curve_to((424, 634), (480, 608), (522, 554), smooth=False)
        .line_to(582, 612)
        .curve_to((530, 678), (452, top), (356, top), smooth=True)
        .hv_to(56, 350, 0.585, 0.59)
        .vh_to(356, bot, 0.59, 0.585)
    )
    return [c]


def build_D(p: SansWeightParams) -> List[ContourBuilder]:
    cap = METRICS.cap_height
    xl0, xl1 = 82, 82 + p.cap_stem_v  # 82..174
    outer = (
        ContourBuilder((xl0, 0))
        .line_to(312, 0)
        .hv_to(610, 350, 0.585, 0.59)
        .vh_to(312, cap, 0.59, 0.585)
        .line_to(xl0, cap)
    )
    inner = (
        ContourBuilder((xl1, 78))
        .line_to(xl1, 622)
        .line_to(306, 622)
        .hv_to(514, 350, 0.59, 0.60)
        .vh_to(306, 78, 0.60, 0.59)
    )
    return [outer, inner]


def build_E(p: SansWeightParams) -> List[ContourBuilder]:
    cap = METRICS.cap_height
    s = p.cap_stem_v   # 92
    bh = p.cap_stem_h  # 78
    xl0, xl1 = 82, 82 + s
    c = (
        ContourBuilder((xl0, 0))
        .line_to(518, 0)
        .line_to(518, bh)
        .line_to(xl1, bh)
        .line_to(xl1, 322)
        .line_to(468, 322)
        .line_to(468, 398)
        .line_to(xl1, 398)
        .line_to(xl1, cap - bh)
        .line_to(502, cap - bh)
        .line_to(502, cap)
        .line_to(xl0, cap)
    )
    return [c]


def build_F(p: SansWeightParams) -> List[ContourBuilder]:
    cap = METRICS.cap_height
    s = p.cap_stem_v
    bh = p.cap_stem_h
    xl0, xl1 = 82, 82 + s
    c = (
        ContourBuilder((xl0, 0))
        .line_to(xl1, 0)
        .line_to(xl1, 312)
        .line_to(456, 312)
        .line_to(456, 388)
        .line_to(xl1, 388)
        .line_to(xl1, cap - bh)
        .line_to(494, cap - bh)
        .line_to(494, cap)
        .line_to(xl0, cap)
    )
    return [c]


def build_G(p: SansWeightParams) -> List[ContourBuilder]:
    top = METRICS.cap_height + METRICS.cap_overshoot  # 712
    bot = -METRICS.cap_overshoot                      # -12
    c = (
        ContourBuilder((358, bot))
        .curve_to((458, bot), (542, 16), (602, 68), smooth=False)
        .line_to(602, 366)
        .line_to(348, 366)
        .line_to(348, 292)
        .line_to(514, 292)
        .line_to(514, 114)
        .curve_to((472, 80), (418, 66), (362, 66), smooth=False)
        .hv_to(152, 350, 0.59, 0.60)
        .vh_to(360, 634, 0.60, 0.59)
        .curve_to((430, 634), (488, 608), (532, 556), smooth=False)
        .line_to(592, 614)
        .curve_to((538, 678), (456, top), (358, top), smooth=True)
        .hv_to(56, 350, 0.585, 0.59)
        .vh_to(358, bot, 0.59, 0.585)
    )
    return [c]


def build_H(p: SansWeightParams) -> List[ContourBuilder]:
    s = p.cap_stem_v
    bh = p.cap_stem_h
    xl0, xl1 = 82, 82 + s
    xr1 = 598
    xr0 = xr1 - s
    yb0, yb1 = 318, 318 + bh
    cap = METRICS.cap_height
    c = (
        ContourBuilder((xl0, 0))
        .line_to(xl1, 0)
        .line_to(xl1, yb0)
        .line_to(xr0, yb0)
        .line_to(xr0, 0)
        .line_to(xr1, 0)
        .line_to(xr1, cap)
        .line_to(xr0, cap)
        .line_to(xr0, yb1)
        .line_to(xl1, yb1)
        .line_to(xl1, cap)
        .line_to(xl0, cap)
    )
    return [c]


def build_I(p: SansWeightParams) -> List[ContourBuilder]:
    # Compact symmetric crossbars (x: 42..266 inside w=308) for unmistakable
    # I / l / 1 disambiguation at 14px and 1:1 duplex width with Admiralty Serif.
    cap = METRICS.cap_height
    bh = 74
    xl, xr = 42, 266
    sx0, sx1 = 108, 200  # 92u stem
    c = (
        ContourBuilder((xl, 0))
        .line_to(xr, 0)
        .line_to(xr, bh)
        .line_to(sx1, bh)
        .line_to(sx1, cap - bh)
        .line_to(xr, cap - bh)
        .line_to(xr, cap)
        .line_to(xl, cap)
        .line_to(xl, cap - bh)
        .line_to(sx0, cap - bh)
        .line_to(sx0, bh)
        .line_to(xl, bh)
    )
    return [c]


def build_J(p: SansWeightParams) -> List[ContourBuilder]:
    cap = METRICS.cap_height
    bot = -METRICS.cap_overshoot  # -12
    c = (
        ContourBuilder((224, bot))
        .hv_to(418, 214, 0.58, 0.58)
        .line_to(418, cap)
        .line_to(326, cap)
        .line_to(326, 218)
        .vh_to(220, 66, 0.58, 0.58)
        .curve_to((168, 66), (130, 88), (104, 132), smooth=False)
        .line_to(40, 82)
        .curve_to((80, 20), (144, bot), (224, bot), smooth=True)
    )
    return [c]


def build_K(p: SansWeightParams) -> List[ContourBuilder]:
    cap = METRICS.cap_height  # 700
    xl0, xl1 = 82, 174
    # Classic humanist stepped-arm K: upper arm meets stem at (174, 318);
    # lower leg springs cleanly from upper arm at (284, 416) -> (590, 0).
    c = (
        ContourBuilder((xl0, 0))
        .line_to(xl1, 0)
        .line_to(xl1, 272)
        .line_to(248, 352)
        .line_to(480, 0)
        .line_to(590, 0)
        .line_to(314, 412)
        .line_to(568, cap)
        .line_to(458, cap)
        .line_to(xl1, 368)
        .line_to(xl1, cap)
        .line_to(xl0, cap)
    )
    return [c]


def build_L(p: SansWeightParams) -> List[ContourBuilder]:
    cap = METRICS.cap_height
    xl0, xl1 = 82, 82 + p.cap_stem_v
    bh = p.cap_stem_h
    c = (
        ContourBuilder((xl0, 0))
        .line_to(498, 0)
        .line_to(498, bh)
        .line_to(xl1, bh)
        .line_to(xl1, cap)
        .line_to(xl0, cap)
    )
    return [c]


def build_M(p: SansWeightParams) -> List[ContourBuilder]:
    cap = METRICS.cap_height
    # Upright outer stems (78..164 and 652..738) + crisp center V reaching baseline
    c = (
        ContourBuilder((78, 0))
        .line_to(164, 0)
        .line_to(164, 538)
        .line_to(172, 538)
        .line_to(372, 0)
        .line_to(444, 0)
        .line_to(644, 538)
        .line_to(652, 538)
        .line_to(652, 0)
        .line_to(738, 0)
        .line_to(738, cap)
        .line_to(624, cap)
        .line_to(412, 134)
        .line_to(404, 134)
        .line_to(192, cap)
        .line_to(78, cap)
    )
    return [c]


def build_N(p: SansWeightParams) -> List[ContourBuilder]:
    cap = METRICS.cap_height
    c = (
        ContourBuilder((82, 0))
        .line_to(168, 0)
        .line_to(168, 548)
        .line_to(176, 548)
        .line_to(496, 0)
        .line_to(610, 0)
        .line_to(610, cap)
        .line_to(524, cap)
        .line_to(524, 152)
        .line_to(516, 152)
        .line_to(196, cap)
        .line_to(82, cap)
    )
    return [c]


def build_O(p: SansWeightParams) -> List[ContourBuilder]:
    cx, cy = 342, 350
    rx_out = 286
    ry_out = 350 + METRICS.cap_overshoot  # 362
    rx_in = rx_out - p.cap_bowl_v         # 190
    ry_in = ry_out - p.cap_stem_h         # 284
    return [
        humanist_oval_contour(cx, cy, rx_out, ry_out, 0.58, 0.59, clockwise=False),
        humanist_oval_contour(cx, cy, rx_in, ry_in, 0.60, 0.60, clockwise=True),
    ]


def build_P(p: SansWeightParams) -> List[ContourBuilder]:
    cap = METRICS.cap_height
    xl0, xl1 = 82, 82 + p.cap_stem_v  # 82..174
    outer = (
        ContourBuilder((xl0, 0))
        .line_to(xl1, 0)
        .line_to(xl1, 278)
        .line_to(318, 278)
        .hv_to(544, 489, 0.58, 0.58)
        .vh_to(318, cap, 0.58, 0.58)
        .line_to(xl0, cap)
    )
    inner = (
        ContourBuilder((xl1, 354))
        .line_to(xl1, 624)
        .line_to(310, 624)
        .hv_to(448, 489, 0.59, 0.59)
        .vh_to(310, 354, 0.59, 0.59)
    )
    return [outer, inner]


def build_Q(p: SansWeightParams) -> List[ContourBuilder]:
    # O base + dignified calm humanist tail sweeping gently to (620, -108)
    o_parts = build_O(p)
    tail = (
        ContourBuilder((372, 54))
        .curve_to((424, -44), (496, -112), (596, -112), smooth=True)
        .curve_to((612, -112), (626, -110), (638, -106), smooth=False)
        .line_to(624, -36)
        .curve_to((550, -36), (498, 4), (456, 76), smooth=False)
    )
    return union_contours([o_parts[0], o_parts[1], tail])


def build_R(p: SansWeightParams) -> List[ContourBuilder]:
    cap = METRICS.cap_height
    xl0, xl1 = 82, 82 + p.cap_stem_v
    outer = (
        ContourBuilder((xl0, 0))
        .line_to(xl1, 0)
        .line_to(xl1, 328)
        .line_to(268, 328)
        .line_to(468, 0)
        .line_to(572, 0)
        .line_to(362, 346)
        .curve_to((458, 360), (532, 418), (532, 514), smooth=True)
        .vh_to(316, cap, 0.58, 0.58)
        .line_to(xl0, cap)
    )
    inner = (
        ContourBuilder((xl1, 402))
        .line_to(xl1, 624)
        .line_to(308, 624)
        .hv_to(436, 513, 0.59, 0.59)
        .vh_to(308, 402, 0.59, 0.59)
    )
    return [outer, inner]


def build_S(p: SansWeightParams) -> List[ContourBuilder]:
    top = METRICS.cap_height + METRICS.cap_overshoot  # 712
    bot = -METRICS.cap_overshoot                      # -12
    c = (
        ContourBuilder((282, bot))
        .hv_to(518, 186, 0.58, 0.56)
        .curve_to((518, 324), (416, 368), (294, 404), smooth=True)
        .curve_to((202, 430), (168, 464), (168, 520), smooth=True)
        .vh_to(296, 634, 0.58, 0.58)
        .curve_to((368, 634), (424, 610), (468, 570), smooth=False)
        .line_to(514, 636)
        .curve_to((458, 686), (384, top), (296, top), smooth=True)
        .hv_to(72, 516, 0.58, 0.56)
        .curve_to((72, 380), (174, 336), (294, 300), smooth=True)
        .curve_to((388, 272), (422, 238), (422, 182), smooth=True)
        .vh_to(282, 66, 0.58, 0.58)
        .curve_to((198, 66), (136, 94), (90, 140), smooth=False)
        .line_to(42, 70)
        .curve_to((102, 14), (186, bot), (282, bot), smooth=True)
    )
    return [c]


def build_T(p: SansWeightParams) -> List[ContourBuilder]:
    cap = METRICS.cap_height
    bh = p.cap_stem_h  # 78
    sx0, sx1 = 246, 246 + p.cap_stem_v  # 246..338 inside w=584
    c = (
        ContourBuilder((sx0, 0))
        .line_to(sx1, 0)
        .line_to(sx1, cap - bh)
        .line_to(550, cap - bh)
        .line_to(550, cap)
        .line_to(34, cap)
        .line_to(34, cap - bh)
        .line_to(sx0, cap - bh)
    )
    return [c]


def build_U(p: SansWeightParams) -> List[ContourBuilder]:
    cap = METRICS.cap_height
    bot = -METRICS.cap_overshoot  # -12
    c = (
        ContourBuilder((336, bot))
        .hv_to(590, 258, 0.58, 0.59)
        .line_to(590, cap)
        .line_to(498, cap)
        .line_to(498, 262)
        .vh_to(336, 68, 0.59, 0.58)
        .hv_to(174, 262, 0.58, 0.59)
        .line_to(174, cap)
        .line_to(82, cap)
        .line_to(82, 258)
        .vh_to(336, bot, 0.59, 0.58)
    )
    return [c]


def build_V(p: SansWeightParams) -> List[ContourBuilder]:
    cap = METRICS.cap_height
    c = (
        ContourBuilder((258, 0))
        .line_to(354, 0)
        .line_to(584, cap)
        .line_to(488, cap)
        .line_to(310, 124)
        .line_to(302, 124)
        .line_to(126, cap)
        .line_to(28, cap)
    )
    return [c]


def build_W(p: SansWeightParams) -> List[ContourBuilder]:
    cap = METRICS.cap_height
    c = (
        ContourBuilder((192, 0))
        .line_to(286, 0)
        .line_to(438, 536)
        .line_to(446, 536)
        .line_to(598, 0)
        .line_to(692, 0)
        .line_to(856, cap)
        .line_to(764, cap)
        .line_to(648, 136)
        .line_to(640, 136)
        .line_to(484, 680)
        .line_to(400, 680)
        .line_to(244, 136)
        .line_to(236, 136)
        .line_to(120, cap)
        .line_to(28, cap)
    )
    return [c]


def build_X(p: SansWeightParams) -> List[ContourBuilder]:
    cap = METRICS.cap_height
    # Both diagonals wound CCW: bottom-left -> bottom-right -> top-right -> top-left
    d1 = (
        ContourBuilder((458, 0))
        .line_to(564, 0)
        .line_to(146, cap)
        .line_to(42, cap)
    )
    d2 = (
        ContourBuilder((38, 0))
        .line_to(138, 0)
        .line_to(560, cap)
        .line_to(462, cap)
    )
    return union_contours([d1, d2])


def build_Y(p: SansWeightParams) -> List[ContourBuilder]:
    cap = METRICS.cap_height
    sx0, sx1 = 246, 338
    c = (
        ContourBuilder((sx0, 0))
        .line_to(sx1, 0)
        .line_to(sx1, 286)
        .line_to(558, cap)
        .line_to(458, cap)
        .line_to(296, 378)
        .line_to(288, 378)
        .line_to(126, cap)
        .line_to(26, cap)
        .line_to(sx0, 286)
    )
    return [c]


def build_Z(p: SansWeightParams) -> List[ContourBuilder]:
    cap = METRICS.cap_height
    bh = p.cap_stem_h  # 78
    c = (
        ContourBuilder((42, 0))
        .line_to(534, 0)
        .line_to(534, bh)
        .line_to(158, bh)
        .line_to(528, cap - bh + 8)
        .line_to(528, cap)
        .line_to(54, cap)
        .line_to(54, cap - bh)
        .line_to(414, cap - bh)
        .line_to(42, bh - 8)
    )
    return [c]


CAP_GLYPH_BUILDERS: Dict[str, Callable[[SansWeightParams], List[ContourBuilder]]] = {
    ".notdef": build_notdef,
    "space": build_space,
    "A": build_A,
    "B": build_B,
    "C": build_C,
    "D": build_D,
    "E": build_E,
    "F": build_F,
    "G": build_G,
    "H": build_H,
    "I": build_I,
    "J": build_J,
    "K": build_K,
    "L": build_L,
    "M": build_M,
    "N": build_N,
    "O": build_O,
    "P": build_P,
    "Q": build_Q,
    "R": build_R,
    "S": build_S,
    "T": build_T,
    "U": build_U,
    "V": build_V,
    "W": build_W,
    "X": build_X,
    "Y": build_Y,
    "Z": build_Z,
}
