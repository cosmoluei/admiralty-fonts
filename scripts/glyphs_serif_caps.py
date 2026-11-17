"""
Uppercase A-Z glyph builders for Admiralty Serif Regular (1000 UPM).
Built on the 1:1 duplex advance-width table shared with Admiralty Sans,
featuring classic literary contrast (102u stems / 50u hairlines,
104u/58u calligraphic diagonals) and crisp 30u bracketed serifs.
"""

from __future__ import annotations
from typing import Callable, Dict, List

from design_system import (
    ContourBuilder,
    METRICS,
    humanist_oval_contour,
    lerp_x,
    rect_contour,
    union_contours,
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


def build_notdef(p: SerifWeightParams) -> List[ContourBuilder]:
    return [
        rect_contour(80, 0, 520, 700, clockwise=False),
        rect_contour(144, 64, 456, 636, clockwise=True),
    ]


def build_space(p: SerifWeightParams) -> List[ContourBuilder]:
    return []


def build_A(p: SerifWeightParams) -> List[ContourBuilder]:
    cap = METRICS.cap_height
    # Literary calligraphic contrast: sturdy 58u left upstroke, firm 104u right downstroke, 50u crossbar
    yb0, yb1 = 212, 262
    xl_b0 = lerp_x(98, 0, 304, 590, yb0)
    xr_b0 = lerp_x(498, 0, 312, 590, yb0)
    xl_b1 = lerp_x(98, 0, 304, 590, yb1)
    xr_b1 = lerp_x(498, 0, 312, 590, yb1)

    outer = (
        ContourBuilder((36, 0))
        .line_to(98, 0)
        .line_to(xl_b0, yb0)
        .line_to(xr_b0, yb0)
        .line_to(498, 0)
        .line_to(604, 0)
        .line_to(360, cap)
        .line_to(280, cap)
    )
    inner = (
        ContourBuilder((xl_b1, yb1))
        .line_to(304, 590)
        .line_to(312, 590)
        .line_to(xr_b1, yb1)
    )
    f_left = diag_foot_serif(
        36, 98, 0, lerp_x(36, 0, 280, cap, yb0), xl_b0, yb0,
        ext_l=24, ext_r=28, sh=30, brk=34,
    )
    f_right = diag_foot_serif(
        498, 604, 0, xr_b0, lerp_x(604, 0, 360, cap, yb0), yb0,
        ext_l=28, ext_r=24, sh=30, brk=34,
    )
    return union_contours([outer, inner, f_left, f_right])


def build_B(p: SerifWeightParams) -> List[ContourBuilder]:
    cap = METRICS.cap_height
    xl0, xl1 = 82, 184  # 102u stem
    bh = p.cap_stem_h   # 50u hairline
    stem = vstem_serifed(xl0, xl1, 0, cap, bl=48, tl=48, sh=30, brk=34)
    bowls_out = (
        ContourBuilder((140, 0))
        .line_to(336, 0)
        .hv_to(560, 192, 0.58, 0.58)
        .curve_to((560, 290), (496, 352), (404, 368), smooth=False)
        .curve_to((482, 386), (532, 444), (532, 530), smooth=False)
        .vh_to(318, cap, 0.58, 0.58)
        .line_to(140, cap)
    )
    in_top = (
        ContourBuilder((xl1, 392))
        .line_to(xl1, cap - bh)
        .line_to(304, cap - bh)
        .hv_to(426, 523, 0.58, 0.58)
        .vh_to(306, 392, 0.58, 0.58)
    )
    in_bot = (
        ContourBuilder((xl1, bh))
        .line_to(xl1, 342)
        .line_to(320, 342)
        .hv_to(452, 195, 0.58, 0.58)
        .vh_to(322, bh, 0.58, 0.58)
    )
    return union_contours([bowls_out, in_top, in_bot, stem])


def build_C(p: SerifWeightParams) -> List[ContourBuilder]:
    top = METRICS.cap_height + METRICS.cap_overshoot  # 712
    bot = -METRICS.cap_overshoot                      # -12
    # 110u left belly, 50u top/bottom strokes, crisp editorial upper beak + upturned lower terminal
    body = (
        ContourBuilder((360, bot))
        .curve_to((462, bot), (544, 24), (594, 96), smooth=False)
        .line_to(560, 128)
        .curve_to((510, 66), (442, 38), (364, 38), smooth=True)
        .hv_to(166, 350, 0.59, 0.605)
        .vh_to(364, 662, 0.605, 0.59)
        .curve_to((442, 662), (502, 628), (542, 548), smooth=False)
        .line_to(582, 548)
        .line_to(590, 704)
        .line_to(554, 704)
        .line_to(544, 672)
        .curve_to((494, 698), (432, top), (360, top), smooth=False)
        .hv_to(54, 350, 0.58, 0.595)
        .vh_to(360, bot, 0.595, 0.58)
    )
    return [body]


def build_D(p: SerifWeightParams) -> List[ContourBuilder]:
    cap = METRICS.cap_height
    xl0, xl1 = 82, 184
    bh = p.cap_stem_h  # 50
    stem = vstem_serifed(xl0, xl1, 0, cap, bl=48, tl=48, sh=30, brk=34)
    bowl_out = (
        ContourBuilder((140, 0))
        .line_to(312, 0)
        .hv_to(614, 350, 0.58, 0.59)
        .vh_to(312, cap, 0.59, 0.58)
        .line_to(140, cap)
    )
    bowl_in = (
        ContourBuilder((xl1, bh))
        .line_to(xl1, cap - bh)
        .line_to(304, cap - bh)
        .hv_to(504, 350, 0.59, 0.605)
        .vh_to(304, bh, 0.605, 0.59)
    )
    return union_contours([bowl_out, bowl_in, stem])


def build_E(p: SerifWeightParams) -> List[ContourBuilder]:
    cap = METRICS.cap_height
    xl0, xl1 = 82, 184
    bh = p.cap_stem_h  # 50
    stem = vstem_serifed(xl0, xl1, 0, cap, bl=48, tl=48, sh=30, brk=34)
    arms = (
        ContourBuilder((140, 0))
        .line_to(530, 0)
        .line_to(540, 162)
        .line_to(504, 162)
        .curve_to((496, 86), (474, bh), (416, bh), smooth=False)
        .line_to(xl1, bh)
        .line_to(xl1, 335)
        .line_to(390, 335)
        .curve_to((426, 335), (440, 318), (446, 272), smooth=False)
        .line_to(480, 272)
        .line_to(480, 448)
        .line_to(446, 448)
        .curve_to((440, 402), (426, 385), (390, 385), smooth=False)
        .line_to(xl1, 385)
        .line_to(xl1, cap - bh)
        .line_to(404, cap - bh)
        .curve_to((460, cap - bh), (482, cap - 86), (488, cap - 158), smooth=False)
        .line_to(524, cap - 158)
        .line_to(516, cap)
        .line_to(140, cap)
    )
    return union_contours([stem, arms])


def build_F(p: SerifWeightParams) -> List[ContourBuilder]:
    cap = METRICS.cap_height
    xl0, xl1 = 82, 184
    bh = p.cap_stem_h  # 50
    stem = vstem_serifed(xl0, xl1, 0, cap, bl=48, br=56, tl=48, sh=30, brk=34)
    arms = (
        ContourBuilder((140, 325))
        .line_to(384, 325)
        .curve_to((420, 325), (434, 308), (440, 262), smooth=False)
        .line_to(474, 262)
        .line_to(474, 438)
        .line_to(440, 438)
        .curve_to((434, 392), (420, 375), (384, 375), smooth=False)
        .line_to(140, 375)
    )
    top_arm = (
        ContourBuilder((140, cap - bh))
        .line_to(400, cap - bh)
        .curve_to((456, cap - bh), (478, cap - 86), (484, cap - 158), smooth=False)
        .line_to(520, cap - 158)
        .line_to(512, cap)
        .line_to(140, cap)
    )
    return union_contours([stem, arms, top_arm])


def build_G(p: SerifWeightParams) -> List[ContourBuilder]:
    top = METRICS.cap_height + METRICS.cap_overshoot
    bot = -METRICS.cap_overshoot
    body = (
        ContourBuilder((360, bot))
        .curve_to((462, bot), (546, 14), (606, 62), smooth=False)
        .line_to(606, 338)
        .line_to(508, 338)
        .line_to(508, 96)
        .curve_to((466, 56), (414, 38), (364, 38), smooth=False)
        .hv_to(166, 350, 0.59, 0.605)
        .vh_to(364, 662, 0.605, 0.59)
        .curve_to((442, 662), (502, 628), (542, 548), smooth=False)
        .line_to(582, 548)
        .line_to(590, 704)
        .line_to(554, 704)
        .line_to(544, 672)
        .curve_to((494, 698), (432, top), (360, top), smooth=False)
        .hv_to(54, 350, 0.58, 0.595)
        .vh_to(360, bot, 0.595, 0.58)
    )
    throat_cap = head_pad_ccw(508, 606, 356, ext_l=78, ext_r=40, sh=30, brk=32)
    return union_contours([body, throat_cap])


def build_H(p: SerifWeightParams) -> List[ContourBuilder]:
    cap = METRICS.cap_height
    sL = vstem_serifed(80, 182, 0, cap, bl=44, br=42, tl=44, tr=42, sh=30, brk=34)
    sR = vstem_serifed(498, 600, 0, cap, bl=42, br=44, tl=42, tr=44, sh=30, brk=34)
    bar = rect_contour(150, 331, 530, 381)  # 50u crisp crossbar
    return union_contours([sL, sR, bar])


def build_I(p: SerifWeightParams) -> List[ContourBuilder]:
    cap = METRICS.cap_height
    return [vstem_serifed(103, 205, 0, cap, bl=64, br=64, tl=64, tr=64, sh=30, brk=34)]


def build_J(p: SerifWeightParams) -> List[ContourBuilder]:
    cap = METRICS.cap_height
    bot = -METRICS.cap_overshoot
    # Firm 102u stem curving into a 50u bottom with a rounded pear lobe
    body = (
        ContourBuilder((220, bot))
        .hv_to(422, 214, 0.58, 0.58)
        .line_to(422, cap)
        .line_to(320, cap)
        .line_to(320, 210)
        .vh_to(212, 38, 0.58, 0.58)
        .curve_to((168, 38), (138, 56), (138, 88), smooth=False)   # Review 3: upright tangent at the join
        .curve_to((138, 126), (112, 150), (80, 150), smooth=False)
        .curve_to((46, 150), (24, 124), (24, 88), smooth=True)
        .curve_to((24, 30), (104, bot), (220, bot), smooth=True)
    )
    top_s = head_pad_ccw(320, 422, cap, ext_l=50, ext_r=46, sh=30, brk=34)
    return union_contours([body, top_s])


def build_K(p: SerifWeightParams) -> List[ContourBuilder]:
    cap = METRICS.cap_height
    stem = vstem_serifed(80, 182, 0, cap, bl=44, br=42, tl=44, tr=42, sh=30, brk=34)
    # 58u upper-right arm + firm 104u lower-right leg
    arm_leg = (
        ContourBuilder((162, 336))
        .line_to(236, 398)
        .line_to(470, 0)
        .line_to(580, 0)
        .line_to(296, 456)
        .line_to(550, cap)
        .line_to(476, cap)
        .line_to(162, 388)
    )
    h_arm = diag_head_serif(
        476, 550, cap, lerp_x(476, cap, 162, 388, 456), 296, 456,
        ext_l=24, ext_r=26, sh=30, brk=32,
    )
    f_leg = diag_foot_serif(
        470, 580, 0, 236, lerp_x(580, 0, 296, 456, 398), 398,
        ext_l=22, ext_r=24, sh=30, brk=32,
    )
    return union_contours([stem, arm_leg, h_arm, f_leg])


def build_L(p: SerifWeightParams) -> List[ContourBuilder]:
    cap = METRICS.cap_height
    bh = p.cap_stem_h  # 50
    stem = vstem_serifed(82, 184, 0, cap, bl=48, tl=48, tr=50, sh=30, brk=34)
    base = (
        ContourBuilder((140, 0))
        .line_to(506, 0)
        .line_to(518, 166)
        .line_to(482, 166)
        .curve_to((474, 88), (450, bh), (388, bh), smooth=False)
        .line_to(140, bh)
    )
    return union_contours([stem, base])


def build_M(p: SerifWeightParams) -> List[ContourBuilder]:
    cap = METRICS.cap_height
    # Fortified calligraphic M: 60u thin left stem, 104u down-right V, 58u up-right V, 102u right stem
    sL = vstem_serifed(82, 142, 0, cap, bl=44, br=44, tl=44, sh=30, brk=34)
    sR = vstem_serifed(636, 738, 0, cap, bl=42, br=42, tr=42, sh=30, brk=34)
    v_mid = (
        ContourBuilder((372, 0))
        .line_to(428, 0)
        .line_to(668, cap)
        .line_to(608, cap)
        .line_to(422, 148)
        .line_to(414, 148)
        .line_to(202, cap)
        .line_to(98, cap)
    )
    return union_contours([sL, sR, v_mid])


def build_N(p: SerifWeightParams) -> List[ContourBuilder]:
    cap = METRICS.cap_height
    # 60u vertical thin stems (robust on Windows 100%) + 106u diagonal down-stroke
    sL = vstem_serifed(86, 146, 0, cap, bl=44, br=46, tl=44, sh=30, brk=34)
    sR = vstem_serifed(546, 606, 0, cap, tl=46, tr=44, sh=30, brk=34)
    diag = (
        ContourBuilder((516, 0))
        .line_to(606, 0)
        .line_to(606, 102)
        .line_to(192, cap)
        .line_to(98, cap)
    )
    return union_contours([sL, sR, diag])


def build_O(p: SerifWeightParams) -> List[ContourBuilder]:
    cx, cy = 342, 350
    rx_out = 288
    ry_out = 350 + METRICS.cap_overshoot  # 362
    rx_in = rx_out - p.cap_bowl_v         # 178 (110u vertical bellies)
    ry_in = ry_out - p.cap_stem_h         # 312 (50u top/bottom hairlines!)
    return [
        humanist_oval_contour(cx, cy, rx_out, ry_out, 0.575, 0.595, clockwise=False),
        humanist_oval_contour(cx, cy, rx_in, ry_in, 0.605, 0.61, clockwise=True),
    ]


def build_P(p: SerifWeightParams) -> List[ContourBuilder]:
    cap = METRICS.cap_height
    xl0, xl1 = 82, 184
    bh = p.cap_stem_h  # 50
    stem = vstem_serifed(xl0, xl1, 0, cap, bl=48, br=56, tl=48, sh=30, brk=34)
    bowl_out = (
        ContourBuilder((140, 286))
        .line_to(318, 286)
        .hv_to(546, 493, 0.58, 0.58)
        .vh_to(318, cap, 0.58, 0.58)
        .line_to(140, cap)
    )
    bowl_in = (
        ContourBuilder((xl1, 286 + bh))
        .line_to(xl1, cap - bh)
        .line_to(306, cap - bh)
        .hv_to(438, 493, 0.59, 0.59)
        .vh_to(306, 286 + bh, 0.59, 0.59)
    )
    return union_contours([bowl_out, bowl_in, stem])


def build_Q(p: SerifWeightParams) -> List[ContourBuilder]:
    o_parts = build_O(p)
    tail = (
        ContourBuilder((356, 36))
        .curve_to((414, -56), (496, -116), (602, -116), smooth=True)
        .curve_to((622, -116), (640, -112), (654, -104), smooth=False)
        .line_to(644, -64)
        .curve_to((564, -64), (504, -12), (452, 66), smooth=False)
    )
    return union_contours([o_parts[0], o_parts[1], tail])


def build_R(p: SerifWeightParams) -> List[ContourBuilder]:
    cap = METRICS.cap_height
    xl0, xl1 = 82, 184
    bh = p.cap_stem_h  # 50
    stem = vstem_serifed(xl0, xl1, 0, cap, bl=48, br=46, tl=48, sh=30, brk=34)
    bowl_leg = (
        ContourBuilder((140, 328))
        .line_to(262, 328)
        .line_to(458, 0)
        .line_to(564, 0)
        .line_to(362, 344)
        .curve_to((460, 358), (534, 418), (534, 514), smooth=True)
        .vh_to(314, cap, 0.58, 0.58)
        .line_to(140, cap)
    )
    bowl_in = (
        ContourBuilder((xl1, 328 + bh))
        .line_to(xl1, cap - bh)
        .line_to(304, cap - bh)
        .hv_to(428, 514, 0.59, 0.59)
        .vh_to(304, 328 + bh, 0.59, 0.59)
    )
    leg_foot = diag_foot_serif(
        458, 564, 0, 262, lerp_x(564, 0, 362, 344, 328), 328,
        ext_l=0, ext_r=34, sh=30, brk=30,
    )
    return union_contours([bowl_leg, bowl_in, stem, leg_foot])


def build_S(p: SerifWeightParams) -> List[ContourBuilder]:
    top = METRICS.cap_height + METRICS.cap_overshoot  # 712
    bot = -METRICS.cap_overshoot                      # -12
    # 102u spine, 50u top/bottom strokes, dramatic vertical serif beaks
    c = (
        ContourBuilder((282, bot))
        .hv_to(522, 188, 0.58, 0.56)
        .curve_to((522, 330), (418, 374), (294, 412), smooth=True)
        .curve_to((198, 442), (160, 478), (160, 538), smooth=True)
        .vh_to(296, 662, 0.58, 0.58)
        .curve_to((372, 662), (430, 632), (466, 562), smooth=False)
        .line_to(502, 562)
        .line_to(510, 704)
        .line_to(474, 704)
        .line_to(464, 676)
        .curve_to((418, 700), (360, top), (296, top), smooth=False)
        .hv_to(66, 526, 0.58, 0.56)
        .curve_to((66, 384), (172, 340), (294, 302), smooth=True)
        .curve_to((392, 272), (422, 236), (422, 178), smooth=True)
        .vh_to(282, 38, 0.58, 0.58)
        .curve_to((198, 38), (136, 72), (98, 148), smooth=False)
        .line_to(62, 148)
        .line_to(54, -2)
        .line_to(90, -2)
        .line_to(100, 26)
        .curve_to((150, -2), (212, bot), (282, bot), smooth=False)
    )
    return [c]


def build_T(p: SerifWeightParams) -> List[ContourBuilder]:
    cap = METRICS.cap_height
    bh = p.cap_stem_h  # 50
    stem = vstem_serifed(241, 343, 0, cap - 16, bl=58, br=58, sh=30, brk=34)
    bar = (
        ContourBuilder((32, cap - 162))
        .line_to(68, cap - 162)
        .curve_to((76, cap - 84), (100, cap - bh), (158, cap - bh), smooth=False)
        .line_to(426, cap - bh)
        .curve_to((484, cap - bh), (508, cap - 84), (516, cap - 162), smooth=False)
        .line_to(552, cap - 162)
        .line_to(544, cap)
        .line_to(40, cap)
    )
    return union_contours([stem, bar])


def build_U(p: SerifWeightParams) -> List[ContourBuilder]:
    cap = METRICS.cap_height
    bot = -METRICS.cap_overshoot
    # 102u left stem (82..184), 60u right stem (528..588), 50u bottom
    body = (
        ContourBuilder((340, bot))
        .hv_to(588, 256, 0.58, 0.59)
        .line_to(588, cap)
        .line_to(528, cap)
        .line_to(528, 254)
        .vh_to(350, 38, 0.59, 0.58)
        .hv_to(184, 254, 0.58, 0.59)
        .line_to(184, cap)
        .line_to(82, cap)
        .line_to(82, 256)
        .vh_to(340, bot, 0.59, 0.58)
    )
    hL = head_pad_ccw(82, 184, cap, ext_l=44, ext_r=42, sh=30, brk=34)
    hR = head_pad_ccw(528, 588, cap, ext_l=44, ext_r=44, sh=30, brk=34)
    return union_contours([body, hL, hR])


def build_V(p: SerifWeightParams) -> List[ContourBuilder]:
    cap = METRICS.cap_height
    # 104u left down-stroke, 58u right up-stroke
    v = (
        ContourBuilder((268, 0))
        .line_to(344, 0)
        .line_to(574, cap)
        .line_to(514, cap)
        .line_to(326, 126)
        .line_to(318, 126)
        .line_to(138, cap)
        .line_to(30, cap)
    )
    hL = diag_head_serif(
        30, 138, cap, lerp_x(30, cap, 268, 0, 126), 318, 126,
        ext_l=24, ext_r=26, sh=30, brk=32,
    )
    hR = diag_head_serif(
        514, 574, cap, 326, lerp_x(574, cap, 344, 0, 126), 126,
        ext_l=26, ext_r=24, sh=30, brk=32,
    )
    return union_contours([v, hL, hR])


def build_W(p: SerifWeightParams) -> List[ContourBuilder]:
    cap = METRICS.cap_height
    # Alternating 102u / 58u / 100u / 58u calligraphic strokes
    w_body = (
        ContourBuilder((198, 0))
        .line_to(274, 0)
        .line_to(434, 540)
        .line_to(442, 540)
        .line_to(606, 0)
        .line_to(682, 0)
        .line_to(848, cap)
        .line_to(788, cap)
        .line_to(658, 138)
        .line_to(650, 138)
        .line_to(480, 686)
        .line_to(412, 686)
        .line_to(252, 138)
        .line_to(244, 138)
        .line_to(130, cap)
        .line_to(28, cap)
    )
    hL = diag_head_serif(
        28, 130, cap, lerp_x(28, cap, 198, 0, 138), 244, 138,
        ext_l=22, ext_r=24, sh=30, brk=32,
    )
    hR = diag_head_serif(
        788, 848, cap, 658, lerp_x(848, cap, 682, 0, 138), 138,
        ext_l=24, ext_r=22, sh=30, brk=32,
    )
    return union_contours([w_body, hL, hR])


def build_X(p: SerifWeightParams) -> List[ContourBuilder]:
    cap = METRICS.cap_height
    # 106u thick down-right diagonal + 58u up-right diagonal + crisp 30u serifs
    d1 = ContourBuilder((452, 0)).line_to(562, 0).line_to(150, cap).line_to(40, cap)
    d2 = ContourBuilder((46, 0)).line_to(108, 0).line_to(554, cap).line_to(492, cap)
    hTL = diag_head_serif(40, 150, cap, 452, 562, 0, ext_l=22, ext_r=22, sh=30, brk=32)
    fBR = diag_foot_serif(452, 562, 0, 40, 150, cap, ext_l=22, ext_r=22, sh=30, brk=32)
    fBL = diag_foot_serif(46, 108, 0, 492, 554, cap, ext_l=24, ext_r=24, sh=30, brk=32)
    hTR = diag_head_serif(492, 554, cap, 46, 108, 0, ext_l=24, ext_r=24, sh=30, brk=32)
    return union_contours([d1, d2, hTL, hTR, fBL, fBR])


def build_Y(p: SerifWeightParams) -> List[ContourBuilder]:
    cap = METRICS.cap_height
    stem = vstem_serifed(241, 343, 0, 304, bl=56, br=56, sh=30, brk=34)
    arms = (
        ContourBuilder((241, 282))
        .line_to(343, 282)
        .line_to(552, cap)
        .line_to(492, cap)
        .line_to(308, 362)
        .line_to(300, 362)
        .line_to(136, cap)
        .line_to(28, cap)
    )
    hL = diag_head_serif(
        28, 136, cap, lerp_x(28, cap, 241, 282, 362), 300, 362,
        ext_l=22, ext_r=24, sh=30, brk=30,
    )
    hR = diag_head_serif(
        492, 552, cap, 308, lerp_x(552, cap, 343, 282, 362), 362,
        ext_l=24, ext_r=22, sh=30, brk=30,
    )
    return union_contours([stem, arms, hL, hR])


def build_Z(p: SerifWeightParams) -> List[ContourBuilder]:
    cap = METRICS.cap_height
    bh = p.cap_stem_h  # 50
    c = (
        ContourBuilder((40, 0))
        .line_to(536, 0)
        .line_to(546, 164)
        .line_to(510, 164)
        .curve_to((502, 86), (476, bh), (416, bh), smooth=False)
        .line_to(156, bh)
        .line_to(532, cap - 48)
        .line_to(532, cap)
        .line_to(50, cap)
        .line_to(40, cap - 160)
        .line_to(76, cap - 160)
        .curve_to((84, cap - 84), (110, cap - bh), (170, cap - bh), smooth=False)
        .line_to(420, cap - bh)
        .line_to(40, 48)
    )
    return [c]


SERIF_CAP_BUILDERS: Dict[str, Callable[[SerifWeightParams], List[ContourBuilder]]] = {
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
