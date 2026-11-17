"""
Admiralty Mono Regular (1000 UPM, strict 600u fixed pitch) glyph builders,
anchor calculator, and OpenType feature definition (including off-by-default
ss01 code ligatures implemented via 600u cell-preserving contextual alternates).
"""

from __future__ import annotations
from typing import Callable, Dict, List, Tuple

from design_system import (
    ContourBuilder,
    DUPLEX_ADVANCE_WIDTHS,
    METRICS,
    SansWeightParams,
    UNICODE_MAP,
    bar_segment_contour,
    humanist_oval_contour,
    lerp_x,
    rect_contour,
    union_contours,
)
from glyphs_sans_caps import CAP_GLYPH_BUILDERS
from glyphs_sans_figs_punct import FIG_CAP, FIG_PUNCT_GLYPH_BUILDERS, build_quoteright
from glyphs_sans_latin_ext import (
    COMPOSITE_RECIPES,
    EXT_CONTOUR_BUILDERS,
    _rotate_180,
    _scale_contours,
)
from glyphs_sans_lc import LC_GLYPH_BUILDERS

MONO_WIDTH = 600

# Even stroke weights: 84u capitals / 86u lowercase (matching Mono 'n' and 'H' stems).
MONO_REGULAR = SansWeightParams(
    name="Regular",
    weight_value=400,
    lc_stem_v=86.0,
    lc_stem_h=72.0,
    lc_bowl_v=88.0,
    lc_join_thin=60.0,
    cap_stem_v=84.0,
    cap_stem_h=74.0,
    cap_bowl_v=88.0,
    fig_stem_v=84.0,
    fig_stem_h=72.0,
    fig_bowl_v=86.0,
)


def _fit_to_mono(
    contours: List[ContourBuilder],
    orig_width: int,
    sx: float = 1.0,
    target_pad: float | None = None,
) -> List[ContourBuilder]:
    """Center (and optionally gently proportion-adjust) a Sans glyph into the 600u cell."""
    if not contours:
        return []
    if sx != 1.0:
        cx_orig = orig_width / 2.0
        dx = 300.0 - cx_orig * sx
        return _scale_contours(contours, sx, 1.0, dx, 0.0)
    dx = (MONO_WIDTH - orig_width) / 2.0
    return [c.translated(dx, 0.0) for c in contours]


# ---------------------------------------------------------------------------
# Custom Redrawn 600u Letters (All Wide Caps at 84u stems; All Lowercase at 86u!)
# ---------------------------------------------------------------------------

def build_mono_A(p: SansWeightParams) -> List[ContourBuilder]:
    cap = METRICS.cap_height
    yb0, yb1 = 200, 274  # 74u bar
    xl_b0 = lerp_x(132, 0, 295, 602, yb0)
    xr_b0 = lerp_x(468, 0, 305, 602, yb0)
    xl_b1 = lerp_x(132, 0, 295, 602, yb1)
    xr_b1 = lerp_x(468, 0, 305, 602, yb1)
    outer = (
        ContourBuilder((38, 0))
        .line_to(132, 0)
        .line_to(xl_b0, yb0)
        .line_to(xr_b0, yb0)
        .line_to(468, 0)
        .line_to(562, 0)
        .line_to(356, cap)
        .line_to(244, cap)
    )
    inner = (
        ContourBuilder((xl_b1, yb1))
        .line_to(295, 602)
        .line_to(305, 602)
        .line_to(xr_b1, yb1)
    )
    return [outer, inner]


def build_mono_B(p: SansWeightParams) -> List[ContourBuilder]:
    cap = METRICS.cap_height
    outer = (
        ContourBuilder((72, 0))
        .line_to(316, 0)
        .hv_to(536, 196, 0.58, 0.58)
        .curve_to((536, 286), (484, 344), (402, 362), smooth=False)
        .curve_to((470, 382), (516, 442), (516, 524), smooth=False)
        .vh_to(304, cap, 0.58, 0.58)
        .line_to(72, cap)
    )
    in_top = (
        ContourBuilder((156, 402))
        .line_to(156, cap - 74)
        .line_to(292, cap - 74)
        .hv_to(430, 514, 0.58, 0.58)
        .vh_to(294, 402, 0.58, 0.58)
    )
    in_bot = (
        ContourBuilder((156, 74))
        .line_to(156, 332)
        .line_to(306, 332)
        .hv_to(450, 203, 0.58, 0.58)
        .vh_to(308, 74, 0.58, 0.58)
    )
    return [outer, in_top, in_bot]


def build_mono_C(p: SansWeightParams) -> List[ContourBuilder]:
    top = METRICS.cap_height + METRICS.cap_overshoot
    bot = -METRICS.cap_overshoot
    c = (
        ContourBuilder((320, bot))
        .curve_to((434, bot), (516, 54), (544, 174), smooth=False)
        .line_to(460, 192)
        .curve_to((438, 108), (388, 62), (322, 62), smooth=True)
        .hv_to(136, 350, 0.59, 0.60)
        .vh_to(322, 638, 0.60, 0.59)
        .curve_to((388, 638), (438, 592), (460, 508), smooth=False)
        .line_to(544, 526)
        .curve_to((516, 646), (434, top), (320, top), smooth=True)
        .hv_to(48, 350, 0.585, 0.59)
        .vh_to(320, bot, 0.59, 0.585)
    )
    return [c]


def build_mono_D(p: SansWeightParams) -> List[ContourBuilder]:
    cap = METRICS.cap_height
    outer = (
        ContourBuilder((66, 0))
        .line_to(282, 0)
        .hv_to(548, 350, 0.585, 0.59)
        .vh_to(282, cap, 0.59, 0.585)
        .line_to(66, cap)
    )
    inner = (
        ContourBuilder((150, 74))
        .line_to(150, cap - 74)
        .line_to(276, cap - 74)
        .hv_to(460, 350, 0.59, 0.60)
        .vh_to(276, 74, 0.60, 0.59)
    )
    return [outer, inner]


def build_mono_G(p: SansWeightParams) -> List[ContourBuilder]:
    top = METRICS.cap_height + METRICS.cap_overshoot
    bot = -METRICS.cap_overshoot
    c = (
        ContourBuilder((320, bot))
        .curve_to((414, bot), (492, 22), (546, 82), smooth=False)
        .line_to(546, 386)
        .line_to(306, 386)
        .line_to(306, 312)
        .line_to(462, 312)
        .line_to(462, 114)
        .curve_to((424, 78), (376, 62), (324, 62), smooth=True)
        .hv_to(136, 350, 0.59, 0.60)
        .vh_to(324, 638, 0.60, 0.59)
        .curve_to((392, 638), (442, 600), (464, 524), smooth=False)
        .line_to(546, 548)
        .curve_to((514, 654), (432, top), (320, top), smooth=True)
        .hv_to(48, 350, 0.585, 0.59)
        .vh_to(320, bot, 0.59, 0.585)
    )
    return [c]


def build_mono_H(p: SansWeightParams) -> List[ContourBuilder]:
    cap = METRICS.cap_height
    sL = rect_contour(64, 0, 148, cap)
    sR = rect_contour(452, 0, 536, cap)
    bar = rect_contour(140, 322, 460, 396)
    return union_contours([sL, sR, bar])


def build_mono_I(p: SansWeightParams) -> List[ContourBuilder]:
    # Wide double-barred capital I (x: 124..476, 84u stem 258..342) — unmistakable vs l, 1, |
    cap = METRICS.cap_height
    bh = 74
    c = (
        ContourBuilder((124, 0))
        .line_to(476, 0)
        .line_to(476, bh)
        .line_to(342, bh)
        .line_to(342, cap - bh)
        .line_to(476, cap - bh)
        .line_to(476, cap)
        .line_to(124, cap)
        .line_to(124, cap - bh)
        .line_to(258, cap - bh)
        .line_to(258, bh)
        .line_to(124, bh)
    )
    return [c]


def build_mono_J(p: SansWeightParams) -> List[ContourBuilder]:
    cap = METRICS.cap_height
    # Top crossbar (204..430) + 84u stem (346..430) + deep open hook
    hook = (
        ContourBuilder((256, -12))
        .hv_to(430, 206, 0.58, 0.58)
        .line_to(430, cap)
        .line_to(204, cap)
        .line_to(204, cap - 74)
        .line_to(346, cap - 74)
        .line_to(346, 210)
        .vh_to(250, 64, 0.58, 0.58)
        .curve_to((198, 64), (160, 88), (134, 134), smooth=False)
        .line_to(72, 86)
        .curve_to((112, 20), (176, -12), (256, -12), smooth=True)
    )
    return [hook]


def build_mono_K(p: SansWeightParams) -> List[ContourBuilder]:
    cap = METRICS.cap_height
    stem = rect_contour(72, 0, 156, cap)
    arm = ContourBuilder((120, 286)).line_to(223, 286).line_to(546, cap).line_to(443, cap)
    # Review 2: the leg now stops at y=372, inside the arm. At y=414 its top-left corner stuck
    # out 20u to the left of the arm and showed as a notch at the joint (worse in Bold).
    leg = ContourBuilder((454, 0)).line_to(552, 0).line_to(324, 372).line_to(226, 372)
    return union_contours([stem, arm, leg])


def build_mono_M(p: SansWeightParams) -> List[ContourBuilder]:
    # Redrawn 600u M: 84u outer stems (44..128, 472..556) + suspended central V
    cap = METRICS.cap_height
    c = (
        ContourBuilder((44, 0))
        .line_to(128, 0)
        .line_to(128, 520)
        .line_to(134, 520)
        .line_to(264, 154)
        .line_to(336, 154)
        .line_to(466, 520)
        .line_to(472, 520)
        .line_to(472, 0)
        .line_to(556, 0)
        .line_to(556, cap)
        .line_to(452, cap)
        .line_to(304, 294)
        .line_to(296, 294)
        .line_to(148, cap)
        .line_to(44, cap)
    )
    return [c]


def build_mono_N(p: SansWeightParams) -> List[ContourBuilder]:
    cap = METRICS.cap_height
    sL = rect_contour(64, 0, 148, cap)
    sR = rect_contour(452, 0, 536, cap)
    diag = ContourBuilder((440, 0)).line_to(536, 0).line_to(160, cap).line_to(64, cap)
    return union_contours([sL, sR, diag])


def build_mono_O(p: SansWeightParams) -> List[ContourBuilder]:
    # Native 600u O: 88u vertical bellies (rx 254..166), 74u crowns (ry 362..288)
    outer = humanist_oval_contour(300, 350, 254, 362, 0.585, 0.59, clockwise=False)
    inner = humanist_oval_contour(300, 350, 166, 288, 0.60, 0.60, clockwise=True)
    return [outer, inner]


def build_mono_P(p: SansWeightParams) -> List[ContourBuilder]:
    cap = METRICS.cap_height
    outer = (
        ContourBuilder((76, 0))
        .line_to(160, 0)
        .line_to(160, 262)
        .line_to(314, 262)
        .hv_to(534, 481, 0.585, 0.585)
        .vh_to(314, cap, 0.585, 0.585)
        .line_to(76, cap)
    )
    inner = (
        ContourBuilder((160, 336))
        .line_to(160, cap - 74)
        .line_to(304, cap - 74)
        .hv_to(446, 481, 0.59, 0.59)
        .vh_to(304, 336, 0.59, 0.59)
    )
    return [outer, inner]


def build_mono_Q(p: SansWeightParams) -> List[ContourBuilder]:
    o_parts = build_mono_O(p)
    tail = (
        ContourBuilder((516, -98))
        .curve_to((536, -98), (552, -94), (566, -86), smooth=False)
        .line_to(550, -24)
        .curve_to((538, -28), (528, -30), (518, -30), smooth=True)
        # Review 3: the tail now stops inside the bowl wall (y = 50); at 68 it poked into the counter
        .curve_to((482, -30), (456, 4), (411, 50), smooth=False)
        .line_to(341, 50)
        .curve_to((392, -40), (442, -98), (516, -98), smooth=True)
    )
    return union_contours([o_parts[0], o_parts[1], tail])


def build_mono_R(p: SansWeightParams) -> List[ContourBuilder]:
    cap = METRICS.cap_height
    outer = (
        ContourBuilder((72, 0))
        .line_to(156, 0)
        .line_to(156, 294)
        .line_to(262, 294)
        .line_to(446, 0)
        .line_to(552, 0)
        .line_to(362, 310)
        .curve_to((460, 332), (528, 404), (528, 497), smooth=True)
        .vh_to(312, cap, 0.585, 0.585)
        .line_to(72, cap)
    )
    inner = (
        ContourBuilder((156, 368))
        .line_to(156, cap - 74)
        .line_to(302, cap - 74)
        .hv_to(442, 497, 0.59, 0.59)
        .vh_to(302, 368, 0.59, 0.59)
    )
    return [outer, inner]


def build_mono_U(p: SansWeightParams) -> List[ContourBuilder]:
    cap = METRICS.cap_height
    bot = -METRICS.cap_overshoot
    c = (
        ContourBuilder((300, bot))
        .hv_to(536, 248, 0.585, 0.59)
        .line_to(536, cap)
        .line_to(452, cap)
        .line_to(452, 248)
        .vh_to(300, 62, 0.59, 0.585)
        .hv_to(148, 248, 0.585, 0.59)
        .line_to(148, cap)
        .line_to(64, cap)
        .line_to(64, 248)
        .vh_to(300, bot, 0.59, 0.585)
    )
    return [c]


def build_mono_V(p: SansWeightParams) -> List[ContourBuilder]:
    cap = METRICS.cap_height
    c = (
        ContourBuilder((256, 0))
        .line_to(344, 0)
        .line_to(556, cap)
        .line_to(466, cap)
        .line_to(304, 126)
        .line_to(296, 126)
        .line_to(134, cap)
        .line_to(44, cap)
    )
    return [c]


def build_mono_W(p: SansWeightParams) -> List[ContourBuilder]:
    # Redrawn 600u W: 84u optical strokes (30..570), central apex at y=526
    cap = METRICS.cap_height
    c = (
        ContourBuilder((126, 0))
        .line_to(216, 0)
        .line_to(296, 380)
        .line_to(304, 380)
        .line_to(384, 0)
        .line_to(474, 0)
        .line_to(570, cap)
        .line_to(482, cap)
        .line_to(426, 150)
        .line_to(420, 150)
        .line_to(336, 526)
        .line_to(264, 526)
        .line_to(180, 150)
        .line_to(174, 150)
        .line_to(118, cap)
        .line_to(30, cap)
    )
    return [c]


def build_mono_X(p: SansWeightParams) -> List[ContourBuilder]:
    cap = METRICS.cap_height
    d1 = ContourBuilder((456, 0)).line_to(556, 0).line_to(144, cap).line_to(44, cap)
    d2 = ContourBuilder((44, 0)).line_to(144, 0).line_to(556, cap).line_to(456, cap)
    return union_contours([d1, d2])


def build_mono_i(p: SansWeightParams) -> List[ContourBuilder]:
    # Classic monospaced 'i' (86u stem 257..343 + 72u flags + dot)
    xh = METRICS.x_height
    body = (
        ContourBuilder((132, 0))
        .line_to(468, 0)
        .line_to(468, 72)
        .line_to(343, 72)
        .line_to(343, xh)
        .line_to(148, xh)
        .line_to(148, xh - 72)
        .line_to(257, xh - 72)
        .line_to(257, 72)
        .line_to(132, 72)
    )
    dot = humanist_oval_contour(300, 658, 52, 52, 0.60, 0.60, clockwise=False)
    return [body, dot]


def build_mono_dotlessi(p: SansWeightParams) -> List[ContourBuilder]:
    return build_mono_i(p)[:1]


def build_mono_l(p: SansWeightParams) -> List[ContourBuilder]:
    # Distinct from I, 1, |: tall 740u top-left flag (134..338) + 86u stem (252..338) + curved foot
    asc = METRICS.ascender
    c = (
        ContourBuilder((362, -8))
        .curve_to((404, -8), (444, -2), (478, 10), smooth=False)
        .line_to(466, 78)
        .curve_to((436, 68), (408, 64), (380, 64), smooth=True)
        .hv_to(338, 134, 0.56, 0.58)
        .line_to(338, asc)
        .line_to(134, asc)
        .line_to(134, asc - 72)
        .line_to(252, asc - 72)
        .line_to(252, 118)
        .vh_to(362, -8, 0.58, 0.58)
    )
    return [c]


def build_mono_j(p: SansWeightParams) -> List[ContourBuilder]:
    xh = METRICS.x_height
    body = (
        ContourBuilder((224, -224))
        .hv_to(381, -62, 0.58, 0.58)
        .line_to(381, xh)
        .line_to(156, xh)
        .line_to(156, xh - 72)
        .line_to(295, xh - 72)
        .line_to(295, -64)
        .vh_to(216, -152, 0.58, 0.58)
        .curve_to((182, -152), (150, -142), (124, -124), smooth=False)
        .line_to(96, -188)
        .curve_to((134, -214), (178, -224), (224, -224), smooth=True)
    )
    dot = humanist_oval_contour(338, 658, 52, 52, 0.60, 0.60, clockwise=False)
    return [body, dot]


def build_mono_dotlessj(p: SansWeightParams) -> List[ContourBuilder]:
    return build_mono_j(p)[:1]


def build_mono_r(p: SansWeightParams) -> List[ContourBuilder]:
    # Balanced 600u 'r' with 86u stem (150..236) matching 'n'
    xh = METRICS.x_height
    top = xh + METRICS.lc_overshoot
    stem_foot = (
        ContourBuilder((100, 0))
        .line_to(324, 0)
        .line_to(324, 72)
        .line_to(236, 72)
        .line_to(236, 316)
        .curve_to((236, 404), (300, 450), (386, 450), smooth=True)
        .curve_to((426, 450), (462, 440), (492, 422), smooth=False)
        .line_to(518, 496)
        .curve_to((482, 520), (438, top), (390, top), smooth=True)
        .curve_to((314, top), (262, 494), (232, 434), smooth=False)
        .line_to(230, xh)
        .line_to(100, xh)
        .line_to(100, xh - 72)
        .line_to(150, xh - 72)
        .line_to(150, 72)
        .line_to(100, 72)
    )
    return [stem_foot]


def build_mono_f(p: SansWeightParams) -> List[ContourBuilder]:
    # Balanced 600u 'f' with 86u stem (209..295) matching 'n'
    xh = METRICS.x_height
    c = (
        ContourBuilder((128, 0))
        .line_to(396, 0)
        .line_to(396, 72)
        .line_to(295, 72)
        .line_to(295, 448)
        .line_to(468, 448)
        .line_to(468, xh)
        .line_to(295, xh)
        .line_to(295, 608)
        .vh_to(390, 680, 0.58, 0.58)
        .curve_to((422, 680), (452, 674), (476, 662), smooth=False)
        .line_to(494, 732)
        .curve_to((460, 746), (422, 752), (380, 752), smooth=True)
        .hv_to(209, 604, 0.58, 0.58)
        .line_to(209, xh)
        .line_to(108, xh)
        .line_to(108, 448)
        .line_to(209, 448)
        .line_to(209, 72)
        .line_to(128, 72)
    )
    return [c]


def build_mono_t(p: SansWeightParams) -> List[ContourBuilder]:
    # Balanced 600u 't' with 86u stem (201..287) matching 'n'
    xh = METRICS.x_height
    c = (
        ContourBuilder((352, -10))
        .curve_to((404, -10), (448, -2), (484, 14), smooth=False)
        .line_to(468, 84)
        .curve_to((434, 70), (400, 64), (364, 64), smooth=True)
        .hv_to(287, 148, 0.56, 0.58)
        .line_to(287, 448)
        .line_to(468, 448)
        .line_to(468, xh)
        .line_to(287, xh)
        .line_to(287, 652)
        .line_to(201, 652)
        .line_to(201, xh)
        .line_to(108, xh)
        .line_to(108, 448)
        .line_to(201, 448)
        .line_to(201, 144)
        .vh_to(352, -10, 0.58, 0.58)
    )
    return [c]


def build_mono_m(p: SansWeightParams) -> List[ContourBuilder]:
    # Redrawn 600u 'm': three exact 86u stems (34..120, 257..343, 480..566) matching 'n',
    # leaving two open 137u counters!
    xh = METRICS.x_height
    top = xh + METRICS.lc_overshoot
    c = (
        ContourBuilder((34, 0))
        .line_to(120, 0)
        .line_to(120, 344)
        .curve_to((120, 412), (148, 456), (190, 456), smooth=True)
        .hv_to(257, 344, 0.56, 0.58)
        .line_to(257, 0)
        .line_to(343, 0)
        .line_to(343, 344)
        .curve_to((343, 412), (371, 456), (413, 456), smooth=True)
        .hv_to(480, 344, 0.56, 0.58)
        .line_to(480, 0)
        .line_to(566, 0)
        .line_to(566, 356)
        .vh_to(434, top, 0.58, 0.58)
        .curve_to((384, top), (346, 498), (326, 444), smooth=False)
        .curve_to((308, 498), (266, top), (212, top), smooth=False)
        .curve_to((162, top), (128, 498), (108, 446), smooth=False)
        .line_to(104, xh)
        .line_to(34, xh)
    )
    return [c]


def build_mono_w(p: SansWeightParams) -> List[ContourBuilder]:
    # Redrawn 600u 'w': balanced 86u optical weight matching 'v' and 'n'
    xh = METRICS.x_height
    c = (
        ContourBuilder((128, 0))
        .line_to(214, 0)
        .line_to(296, 304)
        .line_to(304, 304)
        .line_to(386, 0)
        .line_to(472, 0)
        .line_to(570, xh)
        .line_to(484, xh)
        .line_to(426, 128)
        .line_to(420, 128)
        .line_to(334, 408)
        .line_to(266, 408)
        .line_to(180, 128)
        .line_to(174, 128)
        .line_to(116, xh)
        .line_to(30, xh)
    )
    return [c]


def build_mono_one(p: SansWeightParams) -> List[ContourBuilder]:
    # Unmistakable vs l & I: wide flat base (126..474) + sharp angled top beak (122, 558 -> 266, 690)
    c = (
        ContourBuilder((126, 0))
        .line_to(474, 0)
        .line_to(474, 72)
        .line_to(342, 72)
        .line_to(342, FIG_CAP)
        .line_to(262, FIG_CAP)
        .line_to(116, 566)
        .line_to(156, 504)
        .line_to(260, 594)
        .line_to(260, 72)
        .line_to(126, 72)
    )
    return [c]


def build_mono_zero(p: SansWeightParams) -> List[ContourBuilder]:
    # Centered narrow oval (rx=224, distinct from O rx=252) + clear 38u center dot!
    outer = humanist_oval_contour(300, 345, 224, 355, 0.58, 0.585, clockwise=False)
    inner = humanist_oval_contour(300, 345, 140, 287, 0.60, 0.60, clockwise=True)
    dot = humanist_oval_contour(300, 345, 38, 40, 0.60, 0.60, clockwise=False)
    return [outer, inner, dot]


def build_mono_zero_slash(p: SansWeightParams) -> List[ContourBuilder]:
    outer = humanist_oval_contour(300, 345, 224, 355, 0.58, 0.585, clockwise=False)
    inner = humanist_oval_contour(300, 345, 140, 287, 0.60, 0.60, clockwise=True)
    slash = bar_segment_contour((162, 92), (438, 598), 62)
    return union_contours([outer, inner, slash])


# ---------------------------------------------------------------------------
# Code-Optimized Punctuation, Brackets & Symbols for 13 px Disambiguation
# ---------------------------------------------------------------------------

def build_mono_period(p: SansWeightParams) -> List[ContourBuilder]:
    return [humanist_oval_contour(300, 56, 62, 62, 0.62, 0.62, clockwise=False)]


def build_mono_comma(p: SansWeightParams) -> List[ContourBuilder]:
    # Prominent sweeping tail to y=-148 so ',' vs '.' is effortless at 13 px!
    c = (
        ContourBuilder((266, -148))
        .curve_to((336, -114), (368, -36), (368, 52), smooth=True)
        .vh_to(302, 116, 0.60, 0.60)
        .hv_to(238, 52, 0.60, 0.60)
        .vh_to(294, -8, 0.58, 0.58)
        .curve_to((292, -52), (268, -90), (228, -116), smooth=False)
    )
    return [c]


def build_mono_colon(p: SansWeightParams) -> List[ContourBuilder]:
    return [
        humanist_oval_contour(300, 56, 60, 60, 0.62, 0.62, clockwise=False),
        humanist_oval_contour(300, 412, 60, 60, 0.62, 0.62, clockwise=False),
    ]


def build_mono_semicolon(p: SansWeightParams) -> List[ContourBuilder]:
    return build_mono_comma(p) + [
        humanist_oval_contour(302, 412, 60, 60, 0.62, 0.62, clockwise=False)
    ]


def build_mono_quotesingle(p: SansWeightParams) -> List[ContourBuilder]:
    # Crisp vertical tapered straight quote (x: 256..344, y: 432..700)
    return [
        ContourBuilder((266, 432))
        .line_to(334, 432)
        .line_to(346, 700)
        .line_to(254, 700)
    ]


def build_mono_quotedbl(p: SansWeightParams) -> List[ContourBuilder]:
    q = build_mono_quotesingle(p)[0]
    return [q.translated(-108, 0), q.translated(108, 0)]


def build_mono_grave(p: SansWeightParams) -> List[ContourBuilder]:
    # Strongly angled backtick (38° slant) so ` vs ' vs ‘ is unmistakable at 13 px!
    return [
        ContourBuilder((336, 524))
        .line_to(404, 524)
        .line_to(268, 714)
        .line_to(182, 714)
    ]


def build_mono_parenleft(p: SansWeightParams) -> List[ContourBuilder]:
    c = (
        ContourBuilder((398, -136))
        .line_to(462, -100)
        .curve_to((346, 26), (294, 156), (294, 304), smooth=True)
        .curve_to((294, 452), (346, 582), (462, 708), smooth=True)
        .line_to(398, 744)
        .curve_to((266, 608), (206, 462), (206, 304), smooth=True)
        .curve_to((206, 146), (266, 0), (398, -136), smooth=True)
    )
    return [c]


def build_mono_parenright(p: SansWeightParams) -> List[ContourBuilder]:
    return _rotate_180(build_mono_parenleft(p), 300, 304)


def build_mono_bracketleft(p: SansWeightParams) -> List[ContourBuilder]:
    c = (
        ContourBuilder((196, -132))
        .line_to(436, -132)
        .line_to(436, -62)
        .line_to(280, -62)
        .line_to(280, 670)
        .line_to(436, 670)
        .line_to(436, 740)
        .line_to(196, 740)
    )
    return [c]


def build_mono_bracketright(p: SansWeightParams) -> List[ContourBuilder]:
    return _rotate_180(build_mono_bracketleft(p), 300, 304)


def build_mono_braceleft(p: SansWeightParams) -> List[ContourBuilder]:
    # Bold, exaggerated center beak at x=128 so { } never looks like ( ) at 13 px!
    c = (
        ContourBuilder((368, -132))
        .line_to(456, -132)
        .line_to(456, -64)
        .line_to(384, -64)
        .hv_to(332, -8, 0.56, 0.58)
        .line_to(332, 206)
        .vh_to(224, 304, 0.58, 0.56)
        .hv_to(332, 402, 0.56, 0.58)
        .line_to(332, 616)
        .vh_to(384, 672, 0.58, 0.56)
        .line_to(456, 672)
        .line_to(456, 740)
        .line_to(368, 740)
        .hv_to(252, 624, 0.58, 0.58)
        .line_to(252, 396)
        .vh_to(132, 338, 0.58, 0.56)
        .line_to(132, 270)
        .hv_to(252, 212, 0.56, 0.58)
        .line_to(252, -16)
        .vh_to(368, -132, 0.58, 0.58)
    )
    return [c]


def build_mono_braceright(p: SansWeightParams) -> List[ContourBuilder]:
    return _rotate_180(build_mono_braceleft(p), 300, 304)


def build_mono_slash(p: SansWeightParams) -> List[ContourBuilder]:
    return [ContourBuilder((116, -96)).line_to(192, -96).line_to(484, 728).line_to(408, 728)]


def build_mono_backslash(p: SansWeightParams) -> List[ContourBuilder]:
    return [ContourBuilder((408, -96)).line_to(484, -96).line_to(192, 728).line_to(116, 728)]


def build_mono_bar(p: SansWeightParams) -> List[ContourBuilder]:
    return [rect_contour(262, -140, 338, 750)]


def build_mono_brokenbar(p: SansWeightParams) -> List[ContourBuilder]:
    return [rect_contour(262, -140, 338, 244), rect_contour(262, 366, 338, 750)]


def build_mono_underscore(p: SansWeightParams) -> List[ContourBuilder]:
    return [rect_contour(42, -120, 558, -50)]


def build_mono_hyphen(p: SansWeightParams) -> List[ContourBuilder]:
    return [rect_contour(116, 240, 484, 312)]


def build_mono_endash(p: SansWeightParams) -> List[ContourBuilder]:
    return [rect_contour(68, 240, 532, 312)]


def build_mono_emdash(p: SansWeightParams) -> List[ContourBuilder]:
    # Fills 600u cell cleanly edge-to-edge (24..576)
    return [rect_contour(24, 240, 576, 312)]


def build_mono_ellipsis(p: SansWeightParams) -> List[ContourBuilder]:
    return [
        humanist_oval_contour(108, 52, 46, 46, 0.62, 0.62, clockwise=False),
        humanist_oval_contour(300, 52, 46, 46, 0.62, 0.62, clockwise=False),
        humanist_oval_contour(492, 52, 46, 46, 0.62, 0.62, clockwise=False),
    ]


def build_mono_asterisk(p: SansWeightParams) -> List[ContourBuilder]:
    # Larger code-friendly 6-spoke star centered at (300, 460)
    cx, cy = 300, 460
    b1 = rect_contour(cx - 32, cy - 178, cx + 32, cy + 178)
    b2 = bar_segment_contour((cx - 154, cy - 89), (cx + 154, cy + 89), 62)
    b3 = bar_segment_contour((cx - 154, cy + 89), (cx + 154, cy - 89), 62)
    return union_contours([b1, b2, b3])


def build_mono_asciicircum(p: SansWeightParams) -> List[ContourBuilder]:
    return [
        ContourBuilder((96, 412))
        .line_to(176, 412)
        .line_to(300, 610)
        .line_to(424, 412)
        .line_to(504, 412)
        .line_to(338, 696)
        .line_to(262, 696)
    ]


def build_mono_asciitilde(p: SansWeightParams) -> List[ContourBuilder]:
    # Centered at y=276 (matching +, =, <, > operator axis!) for code expressions (~0, ~=)
    c = (
        ContourBuilder((408, 198))
        .curve_to((468, 198), (514, 238), (542, 314), smooth=False)
        .line_to(480, 342)
        .curve_to((460, 288), (434, 268), (402, 268), smooth=True)
        .curve_to((366, 268), (330, 290), (288, 318), smooth=True)
        .curve_to((246, 346), (210, 366), (172, 366), smooth=True)
        .curve_to((116, 366), (74, 328), (54, 256), smooth=False)
        .line_to(116, 228)
        .curve_to((134, 278), (156, 296), (188, 296), smooth=True)
        .curve_to((222, 296), (258, 274), (300, 246), smooth=True)
        .curve_to((342, 218), (376, 198), (408, 198), smooth=True)
    )
    return [c]


# ---------------------------------------------------------------------------
# Compact 600u Redrawings for Multi-Bowl Extended Glyphs (AE, OE, ae, oe)
# ---------------------------------------------------------------------------

def build_mono_at(p: SansWeightParams) -> List[ContourBuilder]:
    # Native 600u '@' (x: 34..566, y: -112..700) with crisp round inner 'a' — zero squeezing!
    outer = (
        ContourBuilder((306, -112))
        .curve_to((382, -112), (446, -94), (502, -58), smooth=False)
        .line_to(474, 2)
        .curve_to((426, -28), (370, -44), (310, -44), smooth=True)
        .hv_to(98, 298, 0.585, 0.59)
        .vh_to(308, 634, 0.59, 0.585)
        .hv_to(504, 344, 0.585, 0.585)
        .curve_to((504, 232), (474, 168), (434, 168), smooth=True)
        .curve_to((408, 168), (396, 192), (396, 238), smooth=False)
        .line_to(396, 468)
        .line_to(334, 468)
        .line_to(332, 424)
        .curve_to((310, 458), (278, 478), (238, 478), smooth=False)
        .hv_to(144, 290, 0.585, 0.585)
        .vh_to(236, 102, 0.585, 0.585)
        .curve_to((280, 102), (316, 124), (340, 166), smooth=False)
        .curve_to((352, 120), (386, 96), (432, 96), smooth=False)
        .curve_to((512, 96), (566, 186), (566, 348), smooth=True)
        .vh_to(306, 700, 0.585, 0.585)
        .hv_to(34, 298, 0.59, 0.59)
        .vh_to(306, -112, 0.59, 0.59)
    )
    inner = (
        ContourBuilder((254, 164))
        .hv_to(204, 290, 0.59, 0.59)
        .vh_to(256, 416, 0.59, 0.59)
        .hv_to(332, 326, 0.56, 0.56)
        .line_to(332, 254)
        .vh_to(254, 164, 0.56, 0.56)
    )
    return [outer, inner]


def build_mono_percent(p: SansWeightParams) -> List[ContourBuilder]:
    # Native 600u '%' with balanced round bowls (x: 42..558) + crisp diagonal slash
    top_o = humanist_oval_contour(162, 530, 116, 166, 0.59, 0.59, clockwise=False)
    top_i = humanist_oval_contour(162, 530, 56, 108, 0.60, 0.60, clockwise=True)
    bot_o = humanist_oval_contour(438, 160, 116, 166, 0.59, 0.59, clockwise=False)
    bot_i = humanist_oval_contour(438, 160, 56, 108, 0.60, 0.60, clockwise=True)
    slash = ContourBuilder((128, -8)).line_to(192, -8).line_to(472, 698).line_to(408, 698)
    return [top_o, top_i, bot_o, bot_i, slash]


def build_mono_AE(p: SansWeightParams) -> List[ContourBuilder]:
    # Native 600u AE with 78-80u stems (zero horizontal squeezing!)
    cap = METRICS.cap_height
    yb0, yb1 = 198, 268
    xl_b0 = lerp_x(112, 0, 276, 560, yb0)
    xl_b1 = lerp_x(112, 0, 276, 560, yb1)
    outer = (
        ContourBuilder((32, 0))
        .line_to(112, 0)
        .line_to(xl_b0, yb0)
        .line_to(276, yb0)
        .line_to(276, 0)
        .line_to(562, 0)
        .line_to(562, 72)
        .line_to(356, 72)
        .line_to(356, 324)
        .line_to(532, 324)
        .line_to(532, 396)
        .line_to(356, 396)
        .line_to(356, cap - 72)
        .line_to(556, cap - 72)
        .line_to(556, cap)
        .line_to(256, cap)
    )
    inner = (
        ContourBuilder((xl_b1, yb1))
        .line_to(272, 576)
        .line_to(276, 576)
        .line_to(276, yb1)
    )
    return [outer, inner]


def build_mono_OE(p: SansWeightParams) -> List[ContourBuilder]:
    # Native 600u OE (34..564) with 80-82u stems & open counters
    cap = METRICS.cap_height
    top = cap + METRICS.cap_overshoot
    bot = -METRICS.cap_overshoot
    o_out = (
        ContourBuilder((224, bot))
        .curve_to((266, bot), (288, -6), (288, 0), smooth=False)
        .line_to(564, 0)
        .line_to(564, 72)
        .line_to(366, 72)
        .line_to(366, 324)
        .line_to(534, 324)
        .line_to(534, 396)
        .line_to(366, 396)
        .line_to(366, cap - 72)
        .line_to(558, cap - 72)
        .line_to(558, cap)
        .line_to(288, cap)
        .curve_to((288, cap + 6), (266, top), (224, top), smooth=False)
        .hv_to(34, 350, 0.585, 0.59)
        .vh_to(224, bot, 0.59, 0.585)
    )
    o_in = (
        ContourBuilder((226, 60))
        .hv_to(116, 350, 0.59, 0.60)
        .vh_to(226, 640, 0.60, 0.59)
        .hv_to(286, 540, 0.56, 0.56)
        .line_to(286, 160)
        .vh_to(226, 60, 0.56, 0.56)
    )
    return [o_out, o_in]


def build_mono_ae(p: SansWeightParams) -> List[ContourBuilder]:
    # Review 3: one outline with two counters, built like the Mono Bold ae. The old version was a
    # union of four pieces and left a flat notch at the bottom and a pinched e counter.
    top = METRICS.x_height + METRICS.lc_overshoot
    bot = -METRICS.lc_overshoot
    outer = (
        ContourBuilder((162, bot))
        .curve_to((204, bot), (236, 6), (260, 40), smooth=False)
        .line_to(272, 40)
        .curve_to((302, 6), (352, bot), (428, bot), smooth=True)
        .curve_to((494, bot), (538, 24), (564, 78), smooth=False)
        .line_to(512, 118)
        .curve_to((490, 78), (462, 58), (430, 58), smooth=True)
        .curve_to((372, 58), (334, 112), (330, 226), smooth=False)
        .line_to(566, 226)
        .line_to(566, 276)
        .vh_to(424, top, 0.58, 0.58)
        .curve_to((364, top), (318, 500), (286, 444), smooth=False)
        .line_to(276, 444)
        .curve_to((246, 500), (204, top), (160, top), smooth=True)
        .curve_to((118, top), (84, 506), (62, 480), smooth=False)
        .line_to(104, 426)
        .curve_to((126, 448), (148, 460), (172, 460), smooth=False)
        .hv_to(252, 352, 0.56, 0.56)
        .line_to(252, 312)
        .curve_to((180, 304), (36, 268), (36, 136), smooth=True)
        .vh_to(162, bot, 0.585, 0.585)
    )
    in_a = (
        ContourBuilder((172, 56))
        .hv_to(110, 138, 0.58, 0.58)
        .curve_to((110, 206), (186, 244), (252, 248), smooth=False)
        .line_to(252, 134)
        .vh_to(172, 56, 0.56, 0.58)
    )
    in_e = (
        ContourBuilder((334, 292))
        .line_to(334, 340)
        .vh_to(424, 460, 0.56, 0.58)
        .curve_to((464, 460), (490, 400), (494, 292), smooth=False)
    )
    return [outer, in_a, in_e]


def build_mono_oe(p: SansWeightParams) -> List[ContourBuilder]:
    # Native 600u oe (34..568): balanced round bowls fused along 74u shared wall
    top = METRICS.x_height + METRICS.lc_overshoot
    bot = -METRICS.lc_overshoot
    o_out = (
        ContourBuilder((176, bot))
        .curve_to((222, bot), (258, 8), (284, 44), smooth=False)
        .line_to(284, 476)
        .curve_to((258, 512), (222, top), (176, top), smooth=False)
        .hv_to(34, 260, 0.585, 0.59)
        .vh_to(176, bot, 0.59, 0.585)
    )
    o_in = (
        ContourBuilder((180, 56))
        .hv_to(108, 260, 0.59, 0.60)
        .vh_to(180, 464, 0.60, 0.59)
        .hv_to(254, 344, 0.56, 0.56)
        .line_to(254, 176)
        .vh_to(180, 56, 0.56, 0.56)
    )
    e_out = (
        ContourBuilder((432, bot))
        .curve_to((490, bot), (534, 24), (558, 78), smooth=False)
        .line_to(500, 118)
        .curve_to((482, 76), (458, 56), (428, 56), smooth=True)
        .curve_to((372, 56), (336, 116), (332, 232), smooth=False)
        .line_to(566, 232)
        .line_to(566, 276)
        .vh_to(422, top, 0.58, 0.58)
        .hv_to(254, 260, 0.585, 0.59)
        .vh_to(432, bot, 0.59, 0.585)
    )
    e_in = (
        ContourBuilder((332, 296))
        .line_to(332, 344)
        .hv_to(422, 464, 0.56, 0.58)
        .curve_to((464, 464), (492, 404), (496, 296), smooth=False)
    )
    return union_contours([o_out, o_in, e_out, e_in])


def build_mono_Thorn(p: SansWeightParams) -> List[ContourBuilder]:
    cap = METRICS.cap_height
    outer = (
        ContourBuilder((78, 0))
        .line_to(162, 0)
        .line_to(162, 166)
        .line_to(312, 166)
        .hv_to(530, 376, 0.58, 0.58)
        .vh_to(312, 586, 0.58, 0.58)
        .line_to(162, 586)
        .line_to(162, cap)
        .line_to(78, cap)
    )
    inner = (
        ContourBuilder((162, 240))
        .line_to(162, 512)
        .line_to(304, 512)
        .hv_to(442, 376, 0.59, 0.59)
        .vh_to(304, 240, 0.59, 0.59)
    )
    return [outer, inner]


def build_mono_Germandbls(p: SansWeightParams) -> List[ContourBuilder]:
    cap = METRICS.cap_height
    c = (
        ContourBuilder((78, 0))
        .line_to(162, 0)
        .line_to(162, cap - 74)
        .line_to(326, cap - 74)
        .hv_to(412, 536, 0.58, 0.58)
        .curve_to((412, 468), (362, 424), (258, 392), smooth=False)
        .line_to(258, 326)
        .curve_to((400, 306), (470, 252), (470, 174), smooth=False)
        .vh_to(350, 74, 0.58, 0.58)
        .curve_to((300, 74), (250, 82), (204, 96), smooth=False)
        .line_to(188, 24)
        .curve_to((242, 6), (300, -10), (360, -10), smooth=True)
        .hv_to(554, 176, 0.58, 0.58)
        .curve_to((554, 274), (494, 338), (388, 366), smooth=False)
        .curve_to((452, 404), (492, 464), (492, 540), smooth=False)
        .curve_to((492, 624), (426, cap), (330, cap), smooth=False)
        .line_to(78, cap)
    )
    return [c]


def build_mono_germandbls(p: SansWeightParams) -> List[ContourBuilder]:
    c = (
        ContourBuilder((76, 0))
        .line_to(162, 0)
        .line_to(162, 578)
        .vh_to(284, 672, 0.58, 0.58)
        .hv_to(388, 572, 0.58, 0.58)
        .curve_to((388, 496), (336, 444), (238, 412), smooth=False)
        .line_to(238, 344)
        .curve_to((382, 324), (456, 266), (456, 178), smooth=False)
        .vh_to(344, 62, 0.58, 0.58)
        .curve_to((292, 62), (244, 72), (198, 86), smooth=False)
        .line_to(184, 16)
        .curve_to((236, 0), (294, -10), (356, -10), smooth=True)
        .hv_to(544, 178, 0.58, 0.58)
        .curve_to((544, 280), (484, 348), (376, 376), smooth=False)
        .curve_to((438, 418), (474, 484), (474, 572), smooth=False)
        .vh_to(286, 744, 0.58, 0.58)
        .hv_to(76, 580, 0.58, 0.58)
    )
    return [c]


def build_mono_Eng(p: SansWeightParams) -> List[ContourBuilder]:
    cap = METRICS.cap_height
    sL = rect_contour(64, 0, 148, cap)
    diag = ContourBuilder((440, 0)).line_to(536, 0).line_to(160, cap).line_to(64, cap)
    r_hook = (
        ContourBuilder((406, -224))
        .hv_to(536, -62, 0.58, 0.58)
        .line_to(536, cap)
        .line_to(452, cap)
        .line_to(452, -64)
        .vh_to(398, -152, 0.58, 0.58)
        .curve_to((364, -152), (336, -142), (312, -124), smooth=False)
        .line_to(282, -190)
        .curve_to((316, -214), (360, -224), (406, -224), smooth=True)
    )
    return union_contours([sL, diag, r_hook])


def build_mono_IJ(p: SansWeightParams) -> List[ContourBuilder]:
    cap = METRICS.cap_height
    bh = 74
    i_part = (
        ContourBuilder((52, 0))
        .line_to(242, 0)
        .line_to(242, bh)
        .line_to(189, bh)
        .line_to(189, cap - bh)
        .line_to(242, cap - bh)
        .line_to(242, cap)
        .line_to(52, cap)
        .line_to(52, cap - bh)
        .line_to(105, cap - bh)
        .line_to(105, bh)
        .line_to(52, bh)
    )
    j_part = (
        ContourBuilder((384, -12))
        .hv_to(524, 186, 0.58, 0.58)
        .line_to(524, cap)
        .line_to(338, cap)
        .line_to(338, cap - bh)
        .line_to(440, cap - bh)
        .line_to(440, 186)
        .vh_to(378, 64, 0.58, 0.58)
        .curve_to((344, 64), (316, 84), (294, 122), smooth=False)
        .line_to(238, 74)
        .curve_to((272, 16), (320, -12), (384, -12), smooth=True)
    )
    return [i_part, j_part]


def build_mono_ij(p: SansWeightParams) -> List[ContourBuilder]:
    xh = METRICS.x_height
    i_stem = (
        ContourBuilder((68, 0))
        .line_to(246, 0)
        .line_to(246, 72)
        .line_to(200, 72)
        .line_to(200, xh)
        .line_to(68, xh)
        .line_to(68, xh - 72)
        .line_to(114, xh - 72)
        .line_to(114, 72)
        .line_to(68, 72)
    )
    i_dot = humanist_oval_contour(157, 658, 50, 50, 0.60, 0.60, clockwise=False)
    j_stem = (
        ContourBuilder((342, -224))
        .hv_to(486, -62, 0.58, 0.58)
        .line_to(486, xh)
        .line_to(316, xh)
        .line_to(316, xh - 72)
        .line_to(400, xh - 72)
        .line_to(400, -64)
        .vh_to(336, -152, 0.58, 0.58)
        .curve_to((304, -152), (276, -142), (254, -126), smooth=False)
        .line_to(228, -190)
        .curve_to((262, -214), (300, -224), (342, -224), smooth=True)
    )
    j_dot = humanist_oval_contour(443, 658, 50, 50, 0.60, 0.60, clockwise=False)
    return [i_stem, i_dot, j_stem, j_dot]


def build_mono_napostrophe(p: SansWeightParams) -> List[ContourBuilder]:
    xh = METRICS.x_height
    top = xh + METRICS.lc_overshoot
    q = [c.translated(-42, 0) for c in build_quoteright(p)]
    n_c = (
        ContourBuilder((178, 0))
        .line_to(264, 0)
        .line_to(264, 316)
        .vh_to(372, 456, 0.56, 0.58)
        .hv_to(466, 336, 0.56, 0.58)
        .line_to(466, 0)
        .line_to(552, 0)
        .line_to(552, 344)
        .vh_to(384, top, 0.58, 0.58)
        .curve_to((326, top), (282, 496), (254, 444), smooth=False)
        .line_to(252, xh)
        .line_to(178, xh)
    )
    return q + [n_c]


def build_mono_ldot(p: SansWeightParams) -> List[ContourBuilder]:
    # Mono 'l' shifted slightly left + crisp raised middot inside 600u cell
    l_base = [c.translated(-42, 0) for c in build_mono_l(p)]
    dot = humanist_oval_contour(424, 286, 46, 46, 0.62, 0.62, clockwise=False)
    return l_base + [dot]


def build_mono_tbar(p: SansWeightParams) -> List[ContourBuilder]:
    return union_contours(build_mono_t(p) + [rect_contour(118, 240, 386, 300)])


def build_mono_Tbar(p: SansWeightParams) -> List[ContourBuilder]:
    t_base = _fit_to_mono(CAP_GLYPH_BUILDERS["T"](p), DUPLEX_ADVANCE_WIDTHS["T"])
    return union_contours(t_base + [rect_contour(124, 336, 476, 400)])


def build_mono_longs(p: SansWeightParams) -> List[ContourBuilder]:
    # Mono long s (86u stem 209..295 + curved arch + foot serif, no right crossbar)
    xh = METRICS.x_height
    c = (
        ContourBuilder((128, 0))
        .line_to(396, 0)
        .line_to(396, 72)
        .line_to(295, 72)
        .line_to(295, 608)
        .vh_to(390, 680, 0.58, 0.58)
        .curve_to((422, 680), (452, 674), (476, 662), smooth=False)
        .line_to(494, 732)
        .curve_to((460, 746), (422, 752), (380, 752), smooth=True)
        .hv_to(209, 604, 0.58, 0.58)
        .line_to(209, xh)
        .line_to(108, xh)
        .line_to(108, 448)
        .line_to(209, 448)
        .line_to(209, 72)
        .line_to(128, 72)
    )
    return [c]


def build_mono_won(p: SansWeightParams) -> List[ContourBuilder]:
    b1 = rect_contour(28, 224, 572, 288)
    b2 = rect_contour(28, 384, 572, 448)
    return union_contours(build_mono_W(p) + [b1, b2])


# ---------------------------------------------------------------------------
# Off-by-Default Code Ligature Cell Glyphs (ss01, every glyph = 600u!)
# ---------------------------------------------------------------------------
# Operator vertical axis: y_mid = 276 (bar y: 242..310, 68u thick)

def _lig_hyphen_r(p: SansWeightParams) -> List[ContourBuilder]:
    # Left cell of '->': bar from x=76 right to cell boundary x=600
    return [rect_contour(76, 242, 600, 310)]


def _lig_greater_arrow(p: SansWeightParams) -> List[ContourBuilder]:
    # Right cell of '->': bar from x=0 into crisp arrow nose at x=524
    c = (
        ContourBuilder((0, 242))
        .line_to(388, 242)
        .line_to(238, 92)
        .line_to(288, 42)
        .line_to(514, 268)
        .line_to(514, 284)
        .line_to(288, 510)
        .line_to(238, 460)
        .line_to(388, 310)
        .line_to(0, 310)
    )
    return [c]


def _lig_less_arrow(p: SansWeightParams) -> List[ContourBuilder]:
    return _rotate_180(_lig_greater_arrow(p), 300, 276)


def _lig_hyphen_l(p: SansWeightParams) -> List[ContourBuilder]:
    return [rect_contour(0, 242, 524, 310)]


def _lig_equal_r(p: SansWeightParams) -> List[ContourBuilder]:
    # Left cell of '==' or '=>'
    return [rect_contour(76, 156, 600, 220), rect_contour(76, 332, 600, 396)]


def _lig_equal_l(p: SansWeightParams) -> List[ContourBuilder]:
    # Right cell of '=='
    return [rect_contour(0, 156, 524, 220), rect_contour(0, 332, 524, 396)]


def _lig_greater_fatarrow(p: SansWeightParams) -> List[ContourBuilder]:
    # Right cell of '=>': double bars (156..220, 332..396) meeting angled chevron head!
    bars = [rect_contour(0, 156, 376, 220), rect_contour(0, 332, 376, 396)]
    head = (
        ContourBuilder((232, 92))
        .line_to(282, 42)
        .line_to(514, 268)
        .line_to(514, 284)
        .line_to(282, 510)
        .line_to(232, 460)
        .line_to(416, 276)
    )
    return union_contours(bars + [head])


def _lig_exclam_neq(p: SansWeightParams) -> List[ContourBuilder]:
    # Left cell of '!=': double bar starting at x=96 + bold diagonal slash!
    bars = [rect_contour(96, 156, 600, 220), rect_contour(96, 332, 600, 396)]
    slash = bar_segment_contour((356, 36), (546, 516), 66)
    return union_contours(bars + [slash])


def _lig_less_le(p: SansWeightParams) -> List[ContourBuilder]:
    # Left cell (0..600) of wide 2-cell '<=' chevron-over-bar (total span x: 96..1104):
    # Nose at (96, 336..384), upper/lower arms crossing x=600 cleanly into right cell!
    # Upper arm outer: (96, 384)->(1080, 588) => at x=600, y=488.5; inner: (236, 360)->(1104, 522) => at x=600, y=428
    # Lower arm outer: (96, 336)->(1080, 132) => at x=600, y=231.5; inner: (236, 360)->(1104, 198) => at x=600, y=292
    lt_left = (
        ContourBuilder((96, 336))
        .line_to(600, 232)
        .line_to(600, 298)
        .line_to(252, 360)
        .line_to(600, 422)
        .line_to(600, 488)
        .line_to(96, 384)
    )
    bar_left = rect_contour(96, 48, 600, 114)
    return [lt_left, bar_left]


def _lig_equal_le(p: SansWeightParams) -> List[ContourBuilder]:
    # Right cell (0..600, global 600..1200) of wide 2-cell '<=' continuing seamlessly from x=0 to x=504!
    arms_right = [
        ContourBuilder((0, 232)).line_to(480, 132).line_to(496, 198).line_to(0, 298),
        ContourBuilder((0, 422)).line_to(496, 522).line_to(480, 588).line_to(0, 488),
        rect_contour(0, 48, 504, 114),
    ]
    return arms_right


def _lig_greater_ge(p: SansWeightParams) -> List[ContourBuilder]:
    # Left cell of wide 2-cell '>=' (mirror of _lig_equal_le around x=600)
    return [
        ContourBuilder((120, 132)).line_to(600, 232).line_to(600, 298).line_to(104, 198),
        ContourBuilder((104, 522)).line_to(600, 422).line_to(600, 488).line_to(120, 588),
        rect_contour(96, 48, 600, 114),
    ]


def _lig_equal_ge(p: SansWeightParams) -> List[ContourBuilder]:
    # Right cell of wide 2-cell '>=' (mirror of _lig_less_le)
    gt_right = (
        ContourBuilder((0, 232))
        .line_to(504, 336)
        .line_to(504, 384)
        .line_to(0, 488)
        .line_to(0, 422)
        .line_to(348, 360)
        .line_to(0, 298)
    )
    bar_right = rect_contour(0, 48, 504, 114)
    return [gt_right, bar_right]


def _shifted_case_mono(fn: Callable[[SansWeightParams], List[ContourBuilder]]):
    dy = METRICS.case_shift_y
    def _b(p: SansWeightParams) -> List[ContourBuilder]:
        return [c.translated(0, dy) for c in fn(p)]
    return _b


MONO_CUSTOM_OVERRIDES: Dict[str, Callable[[SansWeightParams], List[ContourBuilder]]] = {
    "A": build_mono_A,
    "B": build_mono_B,
    "C": build_mono_C,
    "D": build_mono_D,
    "G": build_mono_G,
    "H": build_mono_H,
    "I": build_mono_I,
    "J": build_mono_J,
    "K": build_mono_K,
    "M": build_mono_M,
    "N": build_mono_N,
    "O": build_mono_O,
    "P": build_mono_P,
    "Q": build_mono_Q,
    "R": build_mono_R,
    "U": build_mono_U,
    "V": build_mono_V,
    "W": build_mono_W,
    "X": build_mono_X,
    "i": build_mono_i,
    "dotlessi": build_mono_dotlessi,
    "l": build_mono_l,
    "j": build_mono_j,
    "dotlessj": build_mono_dotlessj,
    "r": build_mono_r,
    "f": build_mono_f,
    "t": build_mono_t,
    "m": build_mono_m,
    "w": build_mono_w,
    "zero": build_mono_zero,
    "zero.tnum": build_mono_zero,
    "zero.slash": build_mono_zero_slash,
    "zero.tnum.slash": build_mono_zero_slash,
    "one": build_mono_one,
    "one.tnum": build_mono_one,
    "period": build_mono_period,
    "comma": build_mono_comma,
    "colon": build_mono_colon,
    "semicolon": build_mono_semicolon,
    "quotesingle": build_mono_quotesingle,
    "quotedbl": build_mono_quotedbl,
    "grave": build_mono_grave,
    "parenleft": build_mono_parenleft,
    "parenright": build_mono_parenright,
    "bracketleft": build_mono_bracketleft,
    "bracketright": build_mono_bracketright,
    "braceleft": build_mono_braceleft,
    "braceright": build_mono_braceright,
    "slash": build_mono_slash,
    "backslash": build_mono_backslash,
    "bar": build_mono_bar,
    "brokenbar": build_mono_brokenbar,
    "underscore": build_mono_underscore,
    "hyphen": build_mono_hyphen,
    "hyphentwo": build_mono_hyphen,
    "nonbreakinghyphen": build_mono_hyphen,
    "endash": build_mono_endash,
    "emdash": build_mono_emdash,
    "ellipsis": build_mono_ellipsis,
    "asterisk": build_mono_asterisk,
    "asciicircum": build_mono_asciicircum,
    "asciitilde": build_mono_asciitilde,
    "at": build_mono_at,
    "percent": build_mono_percent,
    "AE": build_mono_AE,
    "OE": build_mono_OE,
    "ae": build_mono_ae,
    "oe": build_mono_oe,
    "Thorn": build_mono_Thorn,
    "Germandbls": build_mono_Germandbls,
    "germandbls": build_mono_germandbls,
    "Eng": build_mono_Eng,
    "IJ": build_mono_IJ,
    "ij": build_mono_ij,
    "ldot": build_mono_ldot,
    "Tbar": build_mono_Tbar,
    "tbar": build_mono_tbar,
    "longs": build_mono_longs,
    "napostrophe": build_mono_napostrophe,
    "won": build_mono_won,
    "lslash": lambda p: union_contours(build_mono_l(p) + [bar_segment_contour((168, 310), (416, 468), 60)]),
    # Case-shifted variants matching Mono's custom brackets & dashes
    "hyphen.case": _shifted_case_mono(build_mono_hyphen),
    "hyphentwo.case": _shifted_case_mono(build_mono_hyphen),
    "nonbreakinghyphen.case": _shifted_case_mono(build_mono_hyphen),
    "endash.case": _shifted_case_mono(build_mono_endash),
    "emdash.case": _shifted_case_mono(build_mono_emdash),
    "parenleft.case": _shifted_case_mono(build_mono_parenleft),
    "parenright.case": _shifted_case_mono(build_mono_parenright),
    "bracketleft.case": _shifted_case_mono(build_mono_bracketleft),
    "bracketright.case": _shifted_case_mono(build_mono_bracketright),
    "braceleft.case": _shifted_case_mono(build_mono_braceleft),
    "braceright.case": _shifted_case_mono(build_mono_braceright),
    "colon.case": _shifted_case_mono(build_mono_colon),
}

MONO_SS01_LIG_GLYPHS: Dict[str, Callable[[SansWeightParams], List[ContourBuilder]]] = {
    "hyphen.lig_r": _lig_hyphen_r,
    "greater.lig_arrow": _lig_greater_arrow,
    "less.lig_arrow": _lig_less_arrow,
    "hyphen.lig_l": _lig_hyphen_l,
    "equal.lig_r": _lig_equal_r,
    "equal.lig_l": _lig_equal_l,
    "greater.lig_fatarrow": _lig_greater_fatarrow,
    "exclam.lig_neq": _lig_exclam_neq,
    "less.lig_le": _lig_less_le,
    "equal.lig_le": _lig_equal_le,
    "greater.lig_ge": _lig_greater_ge,
    "equal.lig_ge": _lig_equal_ge,
}


def build_all_mono_glyphs(
    params: SansWeightParams = MONO_REGULAR,
) -> Dict[str, Tuple[int, int | None, List[ContourBuilder]]]:
    """
    Build all Admiralty Mono Regular contour glyphs:
      - Every spacing glyph has advance width == 600u (zero exceptions!)
      - Combining marks (width == 0) remain zero-width MarkGlyphs for GDEF/mark/mkmk
    """
    sans_core: Dict[str, Callable] = {
        **CAP_GLYPH_BUILDERS,
        **LC_GLYPH_BUILDERS,
        **FIG_PUNCT_GLYPH_BUILDERS,
    }

    result: Dict[str, Tuple[int, int | None, List[ContourBuilder]]] = {}

    for gname, orig_w in DUPLEX_ADVANCE_WIDTHS.items():
        uni = UNICODE_MAP.get(gname)
        if gname in MONO_CUSTOM_OVERRIDES:
            contours = MONO_CUSTOM_OVERRIDES[gname](params)
        else:
            raw = sans_core[gname](params)
            # Gently proportion-fit any non-letter glyph wider than 600u into the 600u cell
            sx = min(1.0, 548.0 / orig_w) if orig_w > 600 else 1.0
            contours = _fit_to_mono(raw, orig_w, sx=sx)
        result[gname] = (MONO_WIDTH, uni, contours)

    for gname, (orig_w, uni, sans_builder) in EXT_CONTOUR_BUILDERS.items():
        if orig_w == 0:
            # Combining mark (zero-width!)
            result[gname] = (0, uni, sans_builder(params))
        elif gname in MONO_CUSTOM_OVERRIDES:
            result[gname] = (MONO_WIDTH, uni, MONO_CUSTOM_OVERRIDES[gname](params))
        elif gname in ("Oslash", "Eth", "Dcroat", "Hbar"):
            # Rebuild on Mono's nicely proportioned base caps!
            base_map = {
                "Oslash": ("O", bar_segment_contour((108, -32), (492, 732), 62)),
                "Eth": ("D", rect_contour(28, 322, 290, 388)),
                "Dcroat": ("D", rect_contour(28, 322, 290, 388)),
                "Hbar": ("H", rect_contour(32, 502, 568, 562)),
            }
            bname, overlay = base_map[gname]
            result[gname] = (MONO_WIDTH, uni, union_contours(result[bname][2] + [overlay]))
        else:
            raw = sans_builder(params)
            sx = min(1.0, 544.0 / orig_w) if orig_w > 600 else 1.0
            result[gname] = (MONO_WIDTH, uni, _fit_to_mono(raw, orig_w, sx=sx))

    # Append 600u contextual ligature cells for off-by-default ss01
    for gname, fn in MONO_SS01_LIG_GLYPHS.items():
        result[gname] = (MONO_WIDTH, None, fn(params))

    return result


from glyphs_sans import OPEN_TYPE_FEATURES_FEA as _SANS_FEA

MONO_FEATURES_FEA = _SANS_FEA + """

# Optional Code Ligatures (OFF by default per Section 9!)
# Every substituted glyph remains 600u wide so fixed-pitch cell alignment never breaks!
feature ss01 {
  featureNames {
    name "Code Ligatures";
  };
  # ->
  sub hyphen' greater by hyphen.lig_r;
  sub hyphen.lig_r greater' by greater.lig_arrow;
  # <-
  sub less' hyphen by less.lig_arrow;
  sub less.lig_arrow hyphen' by hyphen.lig_l;
  # =>
  sub equal' greater by equal.lig_r;
  sub equal.lig_r greater' by greater.lig_fatarrow;
  # ==
  sub equal' equal by equal.lig_r;
  sub equal.lig_r equal' by equal.lig_l;
  # !=
  sub exclam' equal by exclam.lig_neq;
  sub exclam.lig_neq equal' by equal.lig_l;
  # <=
  sub less' equal by less.lig_le;
  sub less.lig_le equal' by equal.lig_le;
  # >=
  sub greater' equal by greater.lig_ge;
  sub greater.lig_ge equal' by equal.lig_ge;
} ss01;
"""


def attach_mono_anchors_and_composites(ufo) -> None:
    """
    Attach centered 600u-aware base & mark anchors and construct all Pan-European
    composite glyphs with advance width == 600u (including IJ = I+J redrawn or fitted!).
    """
    from fontTools.pens.boundsPen import BoundsPen
    import ufoLib2
    from spacing_kerning import BASE_ANCHORS, MARK_ANCHORS

    for mname, adict in MARK_ANCHORS.items():
        if mname in ufo:
            ufo[mname].anchors = [
                ufoLib2.objects.Anchor(x=ax, y=ay, name=aname)
                for aname, (ax, ay) in adict.items()
            ]

    # Compute exact horizontal ink center for each 600u Mono base glyph!
    special_top_x = {
        "L": 124.0,
        "b": 129.0,
        "d": 471.0,
        "h": 127.0,
        "k": 155.0,
        "l": 295.0,
        "t": 244.0,
        "i": 300.0,
        "dotlessi": 300.0,
        "j": 338.0,
        "dotlessj": 338.0,
    }
    special_ogonek = {
        "A": (516.0, 0.0),
        "E": (468.0, 0.0),
        "I": (312.0, 0.0),
        "U": (494.0, 4.0),
        "a": (462.0, 0.0),
        "e": (416.0, 12.0),
        "i": (343.0, 0.0),
        "dotlessi": (343.0, 0.0),
        "u": (469.0, 0.0),
    }

    for bname, orig_anchors in BASE_ANCHORS.items():
        if bname not in ufo:
            continue
        g = ufo[bname]
        bpen = BoundsPen(ufo)
        g.draw(bpen)
        cx = 300.0
        if bpen.bounds is not None:
            cx = round((bpen.bounds[0] + bpen.bounds[2]) / 2.0)

        new_anchors = []
        for aname, (_, ay) in orig_anchors.items():
            if aname == "top":
                ax = special_top_x.get(bname, cx)
                new_anchors.append(ufoLib2.objects.Anchor(x=ax, y=ay, name="top"))
            elif aname == "bottom":
                ax = 295.0 if bname == "l" else cx
                new_anchors.append(ufoLib2.objects.Anchor(x=ax, y=ay, name="bottom"))
            elif aname == "ogonek":
                ox, oy = special_ogonek.get(bname, (cx + 80.0, ay))
                new_anchors.append(ufoLib2.objects.Anchor(x=ox, y=oy, name="ogonek"))
        g.anchors = new_anchors

    glyph_order = list(ufo.lib.get("public.glyphOrder", []))
    for comp_name, uni, base_name, mark_name, anchor_name in COMPOSITE_RECIPES:
        base_g = ufo[base_name]
        mark_g = ufo[mark_name]

        if comp_name in ("dcaron", "lcaron", "tcaron", "Lcaron"):
            dx_map = {"dcaron": 546, "lcaron": 404, "tcaron": 374, "Lcaron": 276}
            dy_map = {"dcaron": 20, "lcaron": 18, "tcaron": 22, "Lcaron": 0}
            dx, dy = dx_map[comp_name], dy_map[comp_name]
        else:
            b_anc = next(a for a in base_g.anchors if a.name == anchor_name)
            m_anc = next(a for a in mark_g.anchors if a.name == f"_{anchor_name}")
            dx = round(b_anc.x - m_anc.x)
            dy = round(b_anc.y - m_anc.y)

        g = ufo.newGlyph(comp_name)
        g.width = MONO_WIDTH
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
