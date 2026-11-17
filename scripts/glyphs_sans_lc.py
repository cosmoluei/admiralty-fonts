"""
Lowercase a-z glyph builders for Admiralty Sans Regular (1000 UPM).
Preserves the approved Milestone 1 shapes (a, d, e, g, i, l, m, n, o, r, s, t, y)
and completes b, c, f, h, j, k, p, q, u, v, w, x, z on the exact same humanist skeleton.
"""

from __future__ import annotations
from typing import Callable, Dict, List

from design_system import (
    ContourBuilder,
    METRICS,
    SansWeightParams,
    humanist_oval_contour,
    union_contours,
)


def build_a(p: SansWeightParams) -> List[ContourBuilder]:
    top = METRICS.x_height + METRICS.lc_overshoot
    bot = -METRICS.lc_overshoot
    outer = (
        ContourBuilder((214, bot))
        .curve_to((290, bot), (362, 18), (396, 68), smooth=False)
        .line_to(398, 0)
        .line_to(474, 0)
        .line_to(474, 350)
        .vh_to(268, top, 0.58, 0.58)
        .curve_to((192, top), (132, 510), (88, 476), smooth=False)
        .line_to(110, 410)
        .curve_to((150, 440), (202, 458), (260, 458), smooth=True)
        .hv_to(390, 346, 0.56, 0.56)
        .line_to(390, 304)
        .curve_to((274, 302), (54, 256), (54, 136), smooth=True)
        .vh_to(214, bot, 0.58, 0.58)
    )
    inner = (
        ContourBuilder((228, 58))
        .hv_to(140, 138, 0.58, 0.58)
        .curve_to((140, 206), (264, 244), (390, 246), smooth=False)
        .line_to(390, 146)
        .vh_to(228, 58, 0.56, 0.58)
    )
    return [outer, inner]


def build_b(p: SansWeightParams) -> List[ContourBuilder]:
    asc = METRICS.ascender
    top = METRICS.x_height + METRICS.lc_overshoot
    bot = -METRICS.lc_overshoot
    outer = (
        ContourBuilder((74, 0))
        .line_to(152, 0)
        .line_to(154, 74)
        .curve_to((186, 22), (248, bot), (326, bot), smooth=True)
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


def build_c(p: SansWeightParams) -> List[ContourBuilder]:
    top = METRICS.x_height + METRICS.lc_overshoot  # 530
    bot = -METRICS.lc_overshoot                    # -10
    c = (
        ContourBuilder((286, bot))
        .curve_to((366, bot), (428, 22), (468, 82), smooth=False)
        .line_to(414, 136)
        .curve_to((382, 88), (338, 62), (288, 62), smooth=True)
        .hv_to(144, 260, 0.59, 0.60)
        .vh_to(288, 458, 0.60, 0.59)
        .curve_to((338, 458), (380, 434), (410, 390), smooth=False)
        .line_to(464, 444)
        .curve_to((424, 500), (364, top), (286, top), smooth=True)
        .hv_to(54, 260, 0.585, 0.585)
        .vh_to(286, bot, 0.585, 0.585)
    )
    return [c]


def build_d(p: SansWeightParams) -> List[ContourBuilder]:
    asc = METRICS.ascender
    top = METRICS.x_height + METRICS.lc_overshoot
    bot = -METRICS.lc_overshoot
    outer = (
        ContourBuilder((250, bot))
        .curve_to((328, bot), (390, 22), (422, 74), smooth=False)
        .line_to(424, 0)
        .line_to(502, 0)
        .line_to(502, asc)
        .line_to(416, asc)
        .line_to(416, 452)
        .curve_to((384, 502), (326, top), (252, top), smooth=True)
        .hv_to(54, 260, 0.585, 0.585)
        .vh_to(250, bot, 0.585, 0.585)
    )
    inner = (
        ContourBuilder((268, 62))
        .hv_to(144, 260, 0.59, 0.60)
        .vh_to(268, 458, 0.60, 0.59)
        .hv_to(416, 332, 0.56, 0.56)
        .line_to(416, 188)
        .vh_to(268, 62, 0.56, 0.56)
    )
    return [outer, inner]


def build_e(p: SansWeightParams) -> List[ContourBuilder]:
    top = METRICS.x_height + METRICS.lc_overshoot
    bot = -METRICS.lc_overshoot
    outer = (
        ContourBuilder((288, bot))
        .curve_to((376, bot), (444, 24), (484, 88), smooth=False)
        .line_to(436, 146)
        .curve_to((398, 92), (348, 62), (292, 62), smooth=True)
        .curve_to((204, 62), (146, 132), (142, 236), smooth=False)
        .line_to(498, 236)
        .line_to(498, 278)
        .vh_to(282, top, 0.58, 0.58)
        .hv_to(54, 260, 0.585, 0.585)
        .vh_to(288, bot, 0.585, 0.585)
    )
    inner = (
        ContourBuilder((144, 302))
        .curve_to((152, 396), (208, 458), (280, 458), smooth=True)
        .curve_to((352, 458), (406, 396), (412, 302), smooth=False)
    )
    return [outer, inner]


def build_f(p: SansWeightParams) -> List[ContourBuilder]:
    xh = METRICS.x_height  # 520
    # Calm humanist f: compact top arch (ends at x=336 inside w=348) so 'fi' & 'fl'
    # space naturally without crashing even without ligatures.
    c = (
        ContourBuilder((106, 0))
        .line_to(192, 0)
        .line_to(192, 448)
        .line_to(312, 448)
        .line_to(312, xh)
        .line_to(192, xh)
        .line_to(192, 608)
        .vh_to(272, 682, 0.58, 0.58)
        .curve_to((296, 682), (316, 678), (334, 670), smooth=False)
        .line_to(348, 738)
        .curve_to((322, 748), (294, 752), (262, 752), smooth=True)
        .hv_to(106, 604, 0.58, 0.58)
        .line_to(106, xh)
        .line_to(36, xh)
        .line_to(36, 448)
        .line_to(106, 448)
    )
    return [c]


def build_g(p: SansWeightParams) -> List[ContourBuilder]:
    xh = METRICS.x_height
    top = xh + METRICS.lc_overshoot
    bowl_bot = -8
    desc_bot = METRICS.descender - 4
    outer = (
        ContourBuilder((250, bowl_bot))
        .curve_to((326, bowl_bot), (384, 22), (412, 72), smooth=False)
        .line_to(412, -20)
        .vh_to(254, -150, 0.58, 0.58)
        .curve_to((194, -150), (146, -138), (110, -118), smooth=False)
        .line_to(86, -184)
        .curve_to((136, -212), (194, desc_bot), (260, desc_bot), smooth=True)
        .hv_to(498, -22, 0.59, 0.59)
        .line_to(498, xh)
        .line_to(420, xh)
        .line_to(418, 452)
        .curve_to((386, 502), (328, top), (254, top), smooth=True)
        .hv_to(54, 260, 0.585, 0.585)
        .vh_to(250, bowl_bot, 0.585, 0.585)
    )
    inner = (
        ContourBuilder((268, 64))
        .hv_to(144, 260, 0.59, 0.60)
        .vh_to(268, 458, 0.60, 0.59)
        .hv_to(412, 334, 0.56, 0.56)
        .line_to(412, 190)
        .vh_to(268, 64, 0.56, 0.56)
    )
    return [outer, inner]


def build_h(p: SansWeightParams) -> List[ContourBuilder]:
    asc = METRICS.ascender
    top = METRICS.x_height + METRICS.lc_overshoot
    c = (
        ContourBuilder((76, 0))
        .line_to(162, 0)
        .line_to(162, 338)
        .curve_to((162, 404), (222, 454), (304, 454), smooth=True)
        .hv_to(422, 326, 0.56, 0.58)
        .line_to(422, 0)
        .line_to(508, 0)
        .line_to(508, 338)
        .vh_to(324, top, 0.58, 0.58)
        .curve_to((248, top), (192, 498), (162, 444), smooth=False)
        .line_to(162, asc)
        .line_to(76, asc)
    )
    return [c]


def build_i(p: SansWeightParams) -> List[ContourBuilder]:
    x0, x1 = 80, 80 + p.lc_stem_v
    xh = METRICS.x_height
    stem = ContourBuilder((x0, 0)).line_to(x1, 0).line_to(x1, xh).line_to(x0, xh)
    dot = humanist_oval_contour(123, 656, 50, 50, 0.62, 0.62, clockwise=False)
    return [stem, dot]


def build_j(p: SansWeightParams) -> List[ContourBuilder]:
    xh = METRICS.x_height
    desc_bot = METRICS.descender - 4  # -224
    # Stem x: 96..182 inside w=256, calm left descender curve
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
    dot = humanist_oval_contour(139, 656, 50, 50, 0.62, 0.62, clockwise=False)
    return [stem, dot]


def build_k(p: SansWeightParams) -> List[ContourBuilder]:
    asc = METRICS.ascender
    xh = METRICS.x_height
    xl0, xl1 = 76, 162
    c = (
        ContourBuilder((xl0, 0))
        .line_to(xl1, 0)
        .line_to(xl1, 206)
        .line_to(226, 270)
        .line_to(404, 0)
        .line_to(504, 0)
        .line_to(284, 326)
        .line_to(484, xh)
        .line_to(382, xh)
        .line_to(xl1, 296)
        .line_to(xl1, asc)
        .line_to(xl0, asc)
    )
    return [c]


def build_l(p: SansWeightParams) -> List[ContourBuilder]:
    asc = METRICS.ascender
    c = (
        ContourBuilder((162, -8))
        .curve_to((182, -8), (202, -5), (220, 0), smooth=False)
        .line_to(220, 66)
        .curve_to((190, 62), (160, 78), (160, 122), smooth=True)
        .line_to(160, asc)
        .line_to(74, asc)
        .line_to(74, 102)
        .vh_to(162, -8, 0.60, 0.60)
    )
    return [c]


def build_m(p: SansWeightParams) -> List[ContourBuilder]:
    xh = METRICS.x_height
    top = xh + METRICS.lc_overshoot
    c = (
        ContourBuilder((76, 0))
        .line_to(162, 0)
        .line_to(162, 340)
        .curve_to((162, 404), (216, 454), (292, 454), smooth=True)
        .hv_to(398, 328, 0.56, 0.58)
        .line_to(398, 0)
        .line_to(482, 0)
        .line_to(482, 340)
        .curve_to((482, 404), (536, 454), (612, 454), smooth=True)
        .hv_to(718, 328, 0.56, 0.58)
        .line_to(718, 0)
        .line_to(804, 0)
        .line_to(804, 340)
        .vh_to(632, top, 0.58, 0.58)
        .curve_to((556, top), (502, 496), (474, 438), smooth=False)
        .curve_to((456, 496), (398, top), (312, top), smooth=True)
        .curve_to((236, top), (184, 498), (156, 444), smooth=False)
        .line_to(154, xh)
        .line_to(76, xh)
    )
    return [c]


def build_n(p: SansWeightParams) -> List[ContourBuilder]:
    xh = METRICS.x_height
    top = xh + METRICS.lc_overshoot
    c = (
        ContourBuilder((76, 0))
        .line_to(162, 0)
        .line_to(162, 338)
        .curve_to((162, 404), (222, 454), (304, 454), smooth=True)
        .hv_to(422, 326, 0.56, 0.58)
        .line_to(422, 0)
        .line_to(508, 0)
        .line_to(508, 338)
        .vh_to(324, top, 0.58, 0.58)
        .curve_to((244, top), (186, 498), (156, 444), smooth=False)
        .line_to(154, xh)
        .line_to(76, xh)
    )
    return [c]


def build_o(p: SansWeightParams) -> List[ContourBuilder]:
    cx, cy = 290, 260
    rx_out = 236
    ry_out = 260 + METRICS.lc_overshoot
    rx_in = rx_out - p.lc_bowl_v
    ry_in = ry_out - p.lc_stem_h
    return [
        humanist_oval_contour(
            cx, cy, rx_out, ry_out, p.outer_tension, p.outer_tension, clockwise=False
        ),
        humanist_oval_contour(
            cx, cy, rx_in, ry_in, p.inner_tension, p.inner_tension, clockwise=True
        ),
    ]


def build_p(p: SansWeightParams) -> List[ContourBuilder]:
    xh = METRICS.x_height
    desc = METRICS.descender
    top = xh + METRICS.lc_overshoot
    bot = -METRICS.lc_overshoot
    outer = (
        ContourBuilder((74, desc))
        .line_to(160, desc)
        .line_to(160, 68)
        .curve_to((192, 18), (250, bot), (324, bot), smooth=True)
        .hv_to(522, 260, 0.585, 0.585)
        .vh_to(326, top, 0.585, 0.585)
        .curve_to((248, top), (186, 498), (154, 446), smooth=False)
        .line_to(152, xh)
        .line_to(74, xh)
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


def build_q(p: SansWeightParams) -> List[ContourBuilder]:
    xh = METRICS.x_height
    desc = METRICS.descender
    top = xh + METRICS.lc_overshoot
    bot = -METRICS.lc_overshoot
    outer = (
        ContourBuilder((416, desc))
        .line_to(502, desc)
        .line_to(502, xh)
        .line_to(424, xh)
        .line_to(422, 446)
        .curve_to((390, 498), (328, top), (250, top), smooth=True)
        .hv_to(54, 260, 0.585, 0.585)
        .vh_to(252, bot, 0.585, 0.585)
        .curve_to((326, bot), (384, 18), (416, 68), smooth=False)
    )
    inner = (
        ContourBuilder((268, 62))
        .hv_to(144, 260, 0.59, 0.60)
        .vh_to(268, 458, 0.60, 0.59)
        .hv_to(416, 332, 0.56, 0.56)
        .line_to(416, 188)
        .vh_to(268, 62, 0.56, 0.56)
    )
    return [outer, inner]


def build_r(p: SansWeightParams) -> List[ContourBuilder]:
    xh = METRICS.x_height
    top = xh + METRICS.lc_overshoot
    c = (
        ContourBuilder((76, 0))
        .line_to(162, 0)
        .line_to(162, 326)
        .curve_to((162, 402), (216, 450), (288, 450), smooth=True)
        .curve_to((306, 450), (320, 446), (332, 440), smooth=False)
        .line_to(348, 516)
        .curve_to((330, 526), (308, top), (284, top), smooth=True)
        .curve_to((224, top), (180, 496), (156, 440), smooth=False)
        .line_to(154, xh)
        .line_to(76, xh)
    )
    return [c]


def build_s(p: SansWeightParams) -> List[ContourBuilder]:
    top = METRICS.x_height + METRICS.lc_overshoot
    bot = -METRICS.lc_overshoot
    c = (
        ContourBuilder((228, bot))
        .hv_to(422, 140, 0.58, 0.56)
        .curve_to((422, 246), (340, 280), (242, 305), smooth=True)
        .curve_to((168, 324), (142, 348), (142, 386), smooth=True)
        .vh_to(244, 460, 0.58, 0.58)
        .curve_to((298, 460), (344, 442), (380, 414), smooth=False)
        .line_to(408, 476)
        .curve_to((362, 512), (306, top), (242, top), smooth=True)
        .hv_to(60, 384, 0.58, 0.56)
        .curve_to((60, 278), (144, 244), (242, 219), smooth=True)
        .curve_to((316, 200), (338, 176), (338, 138), smooth=True)
        .vh_to(228, 60, 0.58, 0.58)
        .curve_to((164, 60), (114, 80), (76, 112), smooth=False)
        .line_to(46, 48)
        .curve_to((96, 10), (158, bot), (228, bot), smooth=True)
    )
    return [c]


def build_t(p: SansWeightParams) -> List[ContourBuilder]:
    xh = METRICS.x_height
    bot = -METRICS.lc_overshoot
    c = (
        ContourBuilder((234, bot))
        .curve_to((272, bot), (302, -3), (324, 8), smooth=False)
        .line_to(324, 76)
        .curve_to((300, 67), (276, 62), (250, 62), smooth=True)
        .hv_to(190, 146, 0.55, 0.58)
        .line_to(190, 448)
        .line_to(308, 448)
        .line_to(308, xh)
        .line_to(190, xh)
        .line_to(190, 648)
        .line_to(104, 648)
        .line_to(104, xh)
        .line_to(48, xh)
        .line_to(48, 448)
        .line_to(104, 448)
        .line_to(104, 144)
        .vh_to(234, bot, 0.58, 0.58)
    )
    return [c]


def build_u(p: SansWeightParams) -> List[ContourBuilder]:
    xh = METRICS.x_height
    bot = -METRICS.lc_overshoot
    c = (
        ContourBuilder((254, bot))
        .curve_to((332, bot), (390, 22), (420, 76), smooth=False)
        .line_to(422, 0)
        .line_to(500, 0)
        .line_to(500, xh)
        .line_to(414, xh)
        .line_to(414, 184)
        .vh_to(274, 66, 0.56, 0.58)
        .hv_to(160, 194, 0.58, 0.56)
        .line_to(160, xh)
        .line_to(74, xh)
        .line_to(74, 182)
        .vh_to(254, bot, 0.58, 0.58)
    )
    return [c]


def build_v(p: SansWeightParams) -> List[ContourBuilder]:
    xh = METRICS.x_height
    c = (
        ContourBuilder((208, 0))
        .line_to(296, 0)
        .line_to(476, xh)
        .line_to(388, xh)
        .line_to(256, 108)
        .line_to(248, 108)
        .line_to(118, xh)
        .line_to(28, xh)
    )
    return [c]


def build_w(p: SansWeightParams) -> List[ContourBuilder]:
    xh = METRICS.x_height
    c = (
        ContourBuilder((164, 0))
        .line_to(252, 0)
        .line_to(374, 396)
        .line_to(382, 396)
        .line_to(504, 0)
        .line_to(592, 0)
        .line_to(728, xh)
        .line_to(642, xh)
        .line_to(550, 114)
        .line_to(542, 114)
        .line_to(418, 508)
        .line_to(338, 508)
        .line_to(214, 114)
        .line_to(206, 114)
        .line_to(114, xh)
        .line_to(28, xh)
    )
    return [c]


def build_x(p: SansWeightParams) -> List[ContourBuilder]:
    xh = METRICS.x_height
    d1 = ContourBuilder((364, 0)).line_to(462, 0).line_to(134, xh).line_to(38, xh)
    d2 = ContourBuilder((36, 0)).line_to(130, 0).line_to(460, xh).line_to(368, xh)
    return union_contours([d1, d2])


def build_y(p: SansWeightParams) -> List[ContourBuilder]:
    xh = METRICS.x_height
    c = (
        ContourBuilder((116, -224))
        .curve_to((182, -224), (233, -161), (259.5, -81.5), smooth=True)
        .line_to(460, xh)
        .line_to(372, xh)
        .line_to(234, 106)
        .line_to(228, 106)
        .line_to(128, xh)
        .line_to(36, xh)
        .line_to(180, -56)
        .line_to(168, -92)
        .curve_to((152, -140), (124, -150), (86, -150), smooth=False)
        .line_to(72, -218)
        .curve_to((86, -222), (100, -224), (116, -224), smooth=True)
    )
    return [c]


def build_z(p: SansWeightParams) -> List[ContourBuilder]:
    xh = METRICS.x_height
    bh = p.lc_stem_h  # 74
    c = (
        ContourBuilder((40, 0))
        .line_to(434, 0)
        .line_to(434, bh)
        .line_to(146, bh)
        .line_to(428, xh - bh + 8)
        .line_to(428, xh)
        .line_to(48, xh)
        .line_to(48, xh - bh)
        .line_to(322, xh - bh)
        .line_to(40, bh - 8)
    )
    return [c]


LC_GLYPH_BUILDERS: Dict[str, Callable[[SansWeightParams], List[ContourBuilder]]] = {
    "a": build_a,
    "b": build_b,
    "c": build_c,
    "d": build_d,
    "e": build_e,
    "f": build_f,
    "g": build_g,
    "h": build_h,
    "i": build_i,
    "j": build_j,
    "k": build_k,
    "l": build_l,
    "m": build_m,
    "n": build_n,
    "o": build_o,
    "p": build_p,
    "q": build_q,
    "r": build_r,
    "s": build_s,
    "t": build_t,
    "u": build_u,
    "v": build_v,
    "w": build_w,
    "x": build_x,
    "y": build_y,
    "z": build_z,
}
