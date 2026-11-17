"""
Lowercase a-z glyph builders for Admiralty Serif Regular (1000 UPM).
Engineered for strong visual differentiation from Admiralty Sans while preserving
1:1 duplex advance widths (zero text reflow):
  - ~2.3:1 literary book-serif contrast (92u stems / 40u hairlines)
  - Double-story binocular 'g' with crisp ear & open lower loop
  - Curved upturned tail & pear-droplet arch on 'a'
  - Pear / teardrop terminals on 'c', 'f', 'r', 'j', 'y'
  - Slender 26u horizontal serifs & expressive sloped head flags
"""

from __future__ import annotations
from typing import Callable, Dict, List

from design_system import (
    ContourBuilder,
    METRICS,
    humanist_oval_contour,
    lerp_x,
    union_contours,
)
from serif_primitives import (
    SERIF_REGULAR,
    SerifWeightParams,
    diag_foot_serif,
    diag_head_serif,
    foot_pad_ccw,
    vstem_serifed,
)


def build_a(p: SerifWeightParams) -> List[ContourBuilder]:
    top = METRICS.x_height + METRICS.lc_overshoot  # 530
    bot = -METRICS.lc_overshoot                    # -10
    # Literary double-story 'a': pear-droplet top-left terminal, 40u hairline arch/waist,
    # 90u stem curving into an upturned humanist tail on the right baseline.
    outer = (
        ContourBuilder((204, bot))
        .curve_to((284, bot), (354, 18), (390, 66), smooth=False)
        .curve_to((398, 16), (424, bot), (464, bot), smooth=False)
        .curve_to((492, bot), (516, -2), (532, 14), smooth=False)
        .line_to(526, 44)
        # Review 3: one wide concave curve from the tail into the stem. The old join was a
        # tight 22-unit corner, which folded into a spike when the Bold was made from it.
        .curve_to((510, 34), (478, 50), (478, 118), smooth=False)
        .line_to(478, 356)
        .vh_to(268, top, 0.58, 0.58)
        .hv_to(70, 418, 0.58, 0.56)
        .vh_to(114, 376, 0.58, 0.58)
        .hv_to(156, 418, 0.58, 0.58)
        .vh_to(260, 482, 0.48, 0.58)
        .hv_to(388, 360, 0.56, 0.56)
        .line_to(388, 310)
        .curve_to((268, 306), (48, 266), (48, 132), smooth=True)
        .vh_to(204, bot, 0.58, 0.58)
    )
    inner = (
        ContourBuilder((220, 38))
        .hv_to(140, 134, 0.58, 0.58)
        .curve_to((140, 214), (262, 258), (388, 262), smooth=False)
        .line_to(388, 136)
        .vh_to(220, 38, 0.56, 0.58)
    )
    return [outer, inner]


def build_b(p: SerifWeightParams) -> List[ContourBuilder]:
    asc = METRICS.ascender
    top = METRICS.x_height + METRICS.lc_overshoot
    bot = -METRICS.lc_overshoot
    stem = vstem_serifed(72, 164, 0, asc, tl=46, tl_flag=True, sh=28, brk=32)
    bowl_out = (
        ContourBuilder((130, 68))
        .curve_to((176, 18), (244, bot), (326, bot), smooth=False)
        .hv_to(528, 260, 0.58, 0.585)
        .vh_to(326, top, 0.585, 0.58)
        .curve_to((248, top), (188, 500), (158, 448), smooth=False)
        .line_to(130, 448)
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


def build_c(p: SerifWeightParams) -> List[ContourBuilder]:
    top = METRICS.x_height + METRICS.lc_overshoot
    bot = -METRICS.lc_overshoot
    # 98u left belly, 48u crowns, warm literary pear lobe at upper-right
    c = (
        ContourBuilder((286, bot))
        .curve_to((372, bot), (438, 24), (476, 90), smooth=False)
        .line_to(444, 118)
        .curve_to((408, 62), (354, 38), (292, 38), smooth=True)
        .hv_to(150, 260, 0.59, 0.605)
        .vh_to(294, 482, 0.605, 0.59)
        .curve_to((338, 482), (374, 470), (396, 448), smooth=False)
        .curve_to((384, 438), (378, 424), (378, 406), smooth=False)
        .vh_to(424, 362, 0.58, 0.58)
        .hv_to(472, 412, 0.58, 0.58)
        .curve_to((472, 480), (396, top), (286, top), smooth=True)
        .hv_to(50, 260, 0.58, 0.59)
        .vh_to(286, bot, 0.59, 0.58)
    )
    return [c]


def build_d(p: SerifWeightParams) -> List[ContourBuilder]:
    asc = METRICS.ascender
    top = METRICS.x_height + METRICS.lc_overshoot
    bot = -METRICS.lc_overshoot
    stem = vstem_serifed(412, 504, 0, asc, br=44, tl=46, tl_flag=True, sh=28, brk=32)
    bowl_out = (
        ContourBuilder((248, bot))
        .curve_to((332, bot), (398, 20), (440, 72), smooth=False)
        .line_to(440, 448)
        .curve_to((396, 500), (330, top), (250, top), smooth=False)
        .hv_to(48, 260, 0.58, 0.585)
        .vh_to(248, bot, 0.585, 0.58)
    )
    bowl_in = (
        ContourBuilder((270, 38))
        .hv_to(146, 260, 0.59, 0.605)
        .vh_to(270, 482, 0.605, 0.59)
        .hv_to(412, 340, 0.56, 0.56)
        .line_to(412, 180)
        .vh_to(270, 38, 0.56, 0.56)
    )
    return union_contours([bowl_out, bowl_in, stem])


def build_e(p: SerifWeightParams) -> List[ContourBuilder]:
    top = METRICS.x_height + METRICS.lc_overshoot
    bot = -METRICS.lc_overshoot
    # 98u left belly, 48u crisp horizontal crossbar & 48u crowns
    outer = (
        ContourBuilder((288, bot))
        .curve_to((380, bot), (450, 26), (492, 94), smooth=False)
        .line_to(460, 124)
        .curve_to((420, 64), (362, 38), (296, 38), smooth=True)
        .curve_to((208, 38), (152, 118), (148, 240), smooth=False)
        .line_to(500, 240)
        .line_to(500, 276)
        .vh_to(282, top, 0.58, 0.58)
        .hv_to(48, 260, 0.58, 0.59)
        .vh_to(288, bot, 0.59, 0.58)
    )
    inner = (
        ContourBuilder((150, 288))
        .curve_to((158, 408), (212, 482), (284, 482), smooth=True)
        .curve_to((356, 482), (406, 410), (412, 288), smooth=False)
    )
    return [outer, inner]


def build_f(p: SerifWeightParams) -> List[ContourBuilder]:
    xh = METRICS.x_height
    # Tall sweeping arch + rounded teardrop lobe + crisp 48u crossbar + wide foot serif
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
    bar = ContourBuilder((36, 472)).line_to(312, 472).line_to(312, xh).line_to(36, xh)
    foot = foot_pad_ccw(104, 196, 0, ext_l=46, ext_r=58, sh=28, brk=32)
    return union_contours([stem_arch, bar, foot])


def build_g(p: SerifWeightParams) -> List[ContourBuilder]:
    """
    Authentic double-story literary binocular 'g' inside w=572:
      - Upper oval bowl (x: 76..452, y: 196..530) with 90u walls & 48u crowns
      - Rounded book-serif ear at top-right (x: 344..528, y: 468..526)
      - Calligraphic S-link on left into closed lower loop (x: 58..518, y: -224..92)
    """
    bowl_out = humanist_oval_contour(264, 363, 188, 167, 0.58, 0.58, clockwise=False)
    bowl_in = humanist_oval_contour(264, 363, 98, 119, 0.60, 0.60, clockwise=True)

    loop_out = humanist_oval_contour(288, -66, 230, 158, 0.57, 0.59, clockwise=False)
    loop_in = humanist_oval_contour(290, -76, 148, 100, 0.60, 0.60, clockwise=True)

    # S-link connecting solid bottom-left of upper bowl (y~216) to solid top bar of lower loop (y~56)
    s_link = (
        ContourBuilder((168, 46))
        # Review 3: the link now ends exactly on the top of the lower loop (288, 92) with a
        # level tangent, so the two shapes join without the small step that was there.
        .line_to(288, 46)
        .line_to(288, 92)
        .curve_to((218, 92), (160, 110), (160, 142), smooth=False)
        .curve_to((160, 168), (182, 190), (218, 210), smooth=False)
        .line_to(168, 236)
        .curve_to((118, 204), (88, 168), (88, 128), smooth=False)
        .curve_to((88, 82), (120, 50), (168, 46), smooth=False)
    )

    # Smooth horizontal-flowing ear emerging seamlessly from crown of bowl
    ear = (
        ContourBuilder((286, 488))   # Review 3: starts inside the bowl wall, not on the counter edge
        .line_to(356, 468)
        .curve_to((394, 476), (430, 480), (464, 480), smooth=False)
        .vh_to(500, 460, 0.55, 0.58)
        .hv_to(536, 494, 0.58, 0.58)
        .vh_to(498, 530, 0.58, 0.58)
        .line_to(264, 530)          # Review 3: top of the ear is level with the top of the bowl
    )

    return union_contours([bowl_out, bowl_in, loop_out, loop_in, s_link, ear])


def build_h(p: SerifWeightParams) -> List[ContourBuilder]:
    asc = METRICS.ascender
    top = METRICS.x_height + METRICS.lc_overshoot
    sL = vstem_serifed(74, 166, 0, asc, bl=42, br=34, tl=44, tl_flag=True, sh=28, brk=32)
    arch = (
        ContourBuilder((148, 344))
        .line_to(166, 344)
        .curve_to((166, 420), (226, 482), (306, 482), smooth=False)
        .hv_to(418, 330, 0.56, 0.58)
        .line_to(418, 0)
        .line_to(510, 0)
        .line_to(510, 338)
        .vh_to(328, top, 0.58, 0.58)
        .curve_to((246, top), (184, 498), (148, 438), smooth=False)
    )
    fR = foot_pad_ccw(418, 510, 0, ext_l=34, ext_r=42, sh=28, brk=32)
    return union_contours([sL, arch, fR])


def build_i(p: SerifWeightParams) -> List[ContourBuilder]:
    xh = METRICS.x_height
    stem = vstem_serifed(78, 170, 0, xh, bl=42, br=42, tl=44, tl_flag=True, sh=28, brk=32)
    dot = humanist_oval_contour(124, 662, 52, 52, 0.60, 0.60, clockwise=False)
    return [stem, dot]


def build_j(p: SerifWeightParams) -> List[ContourBuilder]:
    xh = METRICS.x_height
    desc_bot = METRICS.descender - 6
    flag_stem = vstem_serifed(94, 186, 120, xh, tl=44, tl_flag=True, sh=28, brk=32)
    # Descender hook with rounded pear lobe
    hook = (
        ContourBuilder((44, desc_bot))
        .hv_to(186, -62, 0.58, 0.58)
        .line_to(186, 200)
        .line_to(94, 200)
        .line_to(94, -68)
        .vh_to(30, -178, 0.58, 0.58)
        .hv_to(18, -146, 0.55, 0.55)
        .vh_to(-16, -110, 0.58, 0.58)
        .hv_to(-50, -150, 0.58, 0.58)
        .vh_to(44, desc_bot, 0.58, 0.58)
    )
    dot = humanist_oval_contour(140, 662, 52, 52, 0.60, 0.60, clockwise=False)
    return union_contours([flag_stem, hook]) + [dot]


def build_k(p: SerifWeightParams) -> List[ContourBuilder]:
    asc = METRICS.ascender
    xh = METRICS.x_height
    sL = vstem_serifed(74, 166, 0, asc, bl=42, br=34, tl=44, tl_flag=True, sh=28, brk=32)
    # Fortified 54u upper arm + firm 94u lower leg
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


def build_l(p: SerifWeightParams) -> List[ContourBuilder]:
    asc = METRICS.ascender
    return [vstem_serifed(82, 174, 0, asc, bl=44, br=44, tl=46, tl_flag=True, sh=28, brk=32)]


def build_m(p: SerifWeightParams) -> List[ContourBuilder]:
    xh = METRICS.x_height
    top = xh + METRICS.lc_overshoot
    s1 = vstem_serifed(72, 160, 0, xh, bl=40, br=28, tl=42, tl_flag=True, sh=28, brk=30)
    arches = (
        ContourBuilder((146, 344))
        .line_to(160, 344)
        .curve_to((160, 420), (216, 482), (292, 482), smooth=False)
        .hv_to(396, 330, 0.56, 0.58)
        .line_to(396, 0)
        .line_to(484, 0)
        .line_to(484, 344)
        .curve_to((484, 420), (540, 482), (616, 482), smooth=False)
        .hv_to(720, 330, 0.56, 0.58)
        .line_to(720, 0)
        .line_to(808, 0)
        .line_to(808, 340)
        .vh_to(638, top, 0.58, 0.58)
        .curve_to((560, top), (504, 498), (474, 434), smooth=False)
        .curve_to((454, 496), (398, top), (316, top), smooth=False)
        .curve_to((238, top), (180, 498), (146, 438), smooth=False)
    )
    f2 = foot_pad_ccw(396, 484, 0, ext_l=28, ext_r=28, sh=28, brk=30)
    f3 = foot_pad_ccw(720, 808, 0, ext_l=28, ext_r=40, sh=28, brk=30)
    return union_contours([s1, arches, f2, f3])


def build_n(p: SerifWeightParams) -> List[ContourBuilder]:
    xh = METRICS.x_height
    top = xh + METRICS.lc_overshoot
    sL = vstem_serifed(74, 166, 0, xh, bl=42, br=34, tl=44, tl_flag=True, sh=28, brk=32)
    arch = (
        ContourBuilder((148, 344))
        .line_to(166, 344)
        .curve_to((166, 420), (226, 482), (306, 482), smooth=False)
        .hv_to(418, 330, 0.56, 0.58)
        .line_to(418, 0)
        .line_to(510, 0)
        .line_to(510, 338)
        .vh_to(328, top, 0.58, 0.58)
        .curve_to((246, top), (184, 498), (148, 438), smooth=False)
    )
    fR = foot_pad_ccw(418, 510, 0, ext_l=34, ext_r=42, sh=28, brk=32)
    return union_contours([sL, arch, fR])


def build_o(p: SerifWeightParams) -> List[ContourBuilder]:
    cx, cy = 290, 260
    rx_out = 240
    ry_out = 260 + METRICS.lc_overshoot  # 270
    rx_in = rx_out - p.lc_bowl_v         # 142 (98u vertical bellies)
    ry_in = ry_out - p.lc_stem_h         # 222 (48u top/bottom hairlines!)
    return [
        humanist_oval_contour(cx, cy, rx_out, ry_out, p.outer_tension, p.outer_tension, clockwise=False),
        humanist_oval_contour(cx, cy, rx_in, ry_in, p.inner_tension, p.inner_tension, clockwise=True),
    ]


def build_p(p: SerifWeightParams) -> List[ContourBuilder]:
    xh = METRICS.x_height
    desc = METRICS.descender
    top = xh + METRICS.lc_overshoot
    bot = -METRICS.lc_overshoot
    stem = vstem_serifed(72, 164, desc, xh, bl=42, br=48, tl=44, tl_flag=True, sh=28, brk=32)
    bowl_out = (
        ContourBuilder((140, 68))
        .curve_to((182, 18), (246, bot), (326, bot), smooth=False)
        .hv_to(528, 260, 0.58, 0.585)
        .vh_to(328, top, 0.585, 0.58)
        .curve_to((248, top), (186, 498), (154, 444), smooth=False)
        .line_to(140, 444)
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


def build_q(p: SerifWeightParams) -> List[ContourBuilder]:
    xh = METRICS.x_height
    desc = METRICS.descender
    top = xh + METRICS.lc_overshoot
    bot = -METRICS.lc_overshoot
    stem = vstem_serifed(412, 504, desc, xh, bl=48, br=42, tr=36, sh=28, brk=32)
    bowl_out = (
        ContourBuilder((250, bot))
        .curve_to((328, bot), (388, 18), (430, 68), smooth=False)
        .line_to(430, 444)
        .curve_to((392, 498), (328, top), (248, top), smooth=False)
        .hv_to(48, 260, 0.58, 0.585)
        .vh_to(250, bot, 0.585, 0.58)
    )
    bowl_in = (
        ContourBuilder((270, 38))
        .hv_to(146, 260, 0.59, 0.605)
        .vh_to(270, 482, 0.605, 0.59)
        .hv_to(412, 340, 0.56, 0.56)
        .line_to(412, 180)
        .vh_to(270, 38, 0.56, 0.56)
    )
    return union_contours([bowl_out, bowl_in, stem])


def build_r(p: SerifWeightParams) -> List[ContourBuilder]:
    xh = METRICS.x_height
    top = xh + METRICS.lc_overshoot
    # Wide asymmetric foot serif + expressive pear lobe at upper-right
    sL = vstem_serifed(74, 166, 0, xh, bl=42, br=58, tl=44, tl_flag=True, sh=28, brk=32)
    arm = (
        ContourBuilder((148, 316))
        .line_to(166, 316)
        .vh_to(256, 476, 0.58, 0.58)
        .hv_to(268, 436, 0.55, 0.55)
        .vh_to(308, 394, 0.58, 0.58)
        .hv_to(352, 442, 0.58, 0.58)
        .vh_to(268, top, 0.58, 0.58)
        .curve_to((216, top), (176, 492), (148, 426), smooth=False)
    )
    return union_contours([sL, arm])


def build_s(p: SerifWeightParams) -> List[ContourBuilder]:
    top = METRICS.x_height + METRICS.lc_overshoot
    bot = -METRICS.lc_overshoot
    # 92u spine, 48u top/bottom hairlines, crisp vertical beaks
    c = (
        ContourBuilder((228, bot))
        .hv_to(424, 142, 0.58, 0.56)
        .curve_to((424, 248), (340, 282), (242, 310), smooth=True)
        .curve_to((164, 332), (134, 358), (134, 400), smooth=True)
        .vh_to(244, 482, 0.58, 0.58)
        .curve_to((306, 482), (352, 458), (380, 402), smooth=False)
        .line_to(412, 402)
        .line_to(420, 522)
        .line_to(388, 522)
        .line_to(380, 498)
        .curve_to((342, 518), (294, top), (242, top), smooth=False)
        .hv_to(54, 392, 0.58, 0.56)
        .curve_to((54, 286), (140, 250), (242, 222), smooth=True)
        .curve_to((320, 200), (344, 174), (344, 132), smooth=True)
        .vh_to(228, 38, 0.58, 0.58)
        .curve_to((162, 38), (114, 62), (84, 122), smooth=False)
        .line_to(52, 122)
        .line_to(44, -2)
        .line_to(76, -2)
        .line_to(84, 22)
        .curve_to((126, -2), (176, bot), (228, bot), smooth=False)
    )
    return [c]


def build_t(p: SerifWeightParams) -> List[ContourBuilder]:
    xh = METRICS.x_height
    bot = -METRICS.lc_overshoot
    c = (
        ContourBuilder((236, bot))
        .curve_to((280, bot), (314, 0), (338, 18), smooth=False)
        .line_to(332, 54)
        .curve_to((308, 40), (282, 38), (254, 38), smooth=True)
        .hv_to(194, 142, 0.55, 0.58)
        .line_to(194, 472)
        .line_to(314, 472)
        .line_to(314, xh)
        .line_to(194, xh)
        .line_to(194, 654)
        .line_to(158, 654)
        .curve_to((140, 574), (104, 520), (36, 508), smooth=False)
        .line_to(36, 472)
        .line_to(102, 472)
        .line_to(102, 140)
        .vh_to(236, bot, 0.58, 0.58)
    )
    return [c]


def build_u(p: SerifWeightParams) -> List[ContourBuilder]:
    xh = METRICS.x_height
    bot = -METRICS.lc_overshoot
    sL = vstem_serifed(72, 164, 180, xh, tl=42, tl_flag=True, sh=28, brk=32)
    sR = vstem_serifed(412, 504, 0, xh, br=44, tl=42, tl_flag=True, sh=28, brk=32)
    arch = (
        ContourBuilder((250, bot))
        .curve_to((332, bot), (394, 22), (430, 78), smooth=False)
        .line_to(430, 184)
        .line_to(412, 184)
        .vh_to(270, 38, 0.56, 0.58)
        .hv_to(164, 190, 0.58, 0.56)
        .line_to(72, 190)
        .line_to(72, 180)
        .vh_to(250, bot, 0.58, 0.58)
    )
    return union_contours([sL, sR, arch])


def build_v(p: SerifWeightParams) -> List[ContourBuilder]:
    xh = METRICS.x_height
    # 94u left down-stroke, 54u right up-stroke
    v = (
        ContourBuilder((212, 0))
        .line_to(288, 0)
        .line_to(470, xh)
        .line_to(412, xh)
        .line_to(268, 92)
        .line_to(260, 92)
        .line_to(126, xh)
        .line_to(28, xh)
    )
    hL = diag_head_serif(
        28, 126, xh, lerp_x(28, xh, 212, 0, 92), 260, 92,
        ext_l=22, ext_r=22, sh=28, brk=28,
    )
    hR = diag_head_serif(
        412, 470, xh, 268, lerp_x(470, xh, 288, 0, 92), 92,
        ext_l=24, ext_r=22, sh=28, brk=28,
    )
    return union_contours([v, hL, hR])


def build_w(p: SerifWeightParams) -> List[ContourBuilder]:
    xh = METRICS.x_height
    # Alternating 92u / 54u / 90u / 54u calligraphic strokes
    w_body = (
        ContourBuilder((170, 0))
        .line_to(238, 0)
        .line_to(372, 408)
        .line_to(380, 408)
        .line_to(514, 0)
        .line_to(586, 0)
        .line_to(722, xh)
        .line_to(662, xh)
        .line_to(554, 100)
        .line_to(546, 100)
        .line_to(416, 510)
        .line_to(342, 510)
        .line_to(216, 100)
        .line_to(208, 100)
        .line_to(122, xh)
        .line_to(26, xh)
    )
    hL = diag_head_serif(
        26, 122, xh, lerp_x(26, xh, 170, 0, 100), 208, 100,
        ext_l=20, ext_r=22, sh=28, brk=28,
    )
    hR = diag_head_serif(
        662, 722, xh, 554, lerp_x(722, xh, 586, 0, 100), 100,
        ext_l=24, ext_r=20, sh=28, brk=28,
    )
    return union_contours([w_body, hL, hR])


def build_x(p: SerifWeightParams) -> List[ContourBuilder]:
    xh = METRICS.x_height
    # 96u thick down-right diagonal + 54u slender up-right diagonal
    d1 = ContourBuilder((360, 0)).line_to(462, 0).line_to(136, xh).line_to(34, xh)
    d2 = ContourBuilder((40, 0)).line_to(106, 0).line_to(456, xh).line_to(390, xh)
    hTL = diag_head_serif(34, 136, xh, 360, 462, 0, ext_l=20, ext_r=20, sh=28, brk=28)
    fBR = diag_foot_serif(360, 462, 0, 34, 136, xh, ext_l=20, ext_r=20, sh=28, brk=28)
    fBL = diag_foot_serif(40, 106, 0, 390, 456, xh, ext_l=22, ext_r=22, sh=28, brk=28)
    hTR = diag_head_serif(390, 456, xh, 40, 106, 0, ext_l=22, ext_r=22, sh=28, brk=28)
    return union_contours([d1, d2, hTL, hTR, fBL, fBR])


def build_y(p: SerifWeightParams) -> List[ContourBuilder]:
    xh = METRICS.x_height
    # 94u left down-stroke, 54u right up-stroke/descender ending in a pear lobe
    body = (
        ContourBuilder((106, -224))
        .curve_to((168, -224), (218, -162), (248, -76), smooth=True)
        .line_to(456, xh)
        .line_to(398, xh)
        .line_to(244, 88)
        .line_to(236, 88)
        .line_to(132, xh)
        .line_to(34, xh)
        .line_to(196, -54)
        .curve_to((174, -124), (140, -182), (98, -182), smooth=False)
        .hv_to(86, -148, 0.55, 0.55)
        .vh_to(54, -112, 0.58, 0.58)
        .hv_to(20, -152, 0.58, 0.58)
        .vh_to(106, -224, 0.58, 0.58)
    )
    hL = diag_head_serif(
        34, 132, xh, lerp_x(34, xh, 196, -54, 88), 236, 88,
        ext_l=22, ext_r=22, sh=28, brk=28,
    )
    hR = diag_head_serif(
        398, 456, xh, 244, lerp_x(456, xh, 248, -76, 88), 88,
        ext_l=24, ext_r=22, sh=28, brk=28,
    )
    return union_contours([body, hL, hR])


def build_z(p: SerifWeightParams) -> List[ContourBuilder]:
    xh = METRICS.x_height
    bh = p.lc_stem_h  # 48
    c = (
        ContourBuilder((38, 0))
        .line_to(436, 0)
        .line_to(446, 134)
        .line_to(412, 134)
        .curve_to((404, 72), (384, bh), (332, bh), smooth=False)
        .line_to(144, bh)
        .line_to(432, xh - bh)
        .line_to(432, xh)
        .line_to(46, xh)
        .line_to(36, xh - 130)
        .line_to(70, xh - 130)
        .curve_to((78, xh - 70), (98, xh - bh), (150, xh - bh), smooth=False)
        .line_to(326, xh - bh)
        .line_to(38, bh)
    )
    return [c]


SERIF_LC_BUILDERS: Dict[str, Callable[[SerifWeightParams], List[ContourBuilder]]] = {
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
