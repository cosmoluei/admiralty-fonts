"""
Milestone 7 Medium (Weight 500) Glyph Builders for:
  - Admiralty Sans Medium (1:1 duplexed with Serif Medium, t=0.38 width progression)
  - Admiralty Serif Medium (literary book-serif contrast ~2.3:1, 112-128u stems / 44-50u hairlines)
  - Admiralty Mono Medium (strict 600u fixed pitch, 96-102u stems, 76u ss01 ligatures)
"""

from __future__ import annotations
from typing import Callable, Dict, List, Tuple

import ufoLib2

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
from glyphs_bold import (
    _LOCKED_WIDTH_GLYPHS,
    bolden_contours_smooth,
    compute_duplex_bold_width,
)
from glyphs_mono import (
    MONO_REGULAR,
    MONO_WIDTH,
    build_all_mono_glyphs,
)
from glyphs_sans import build_all_sans_glyphs
from glyphs_sans_latin_ext import (
    COMPOSITE_RECIPES,
    EXT_CONTOUR_BUILDERS,
    _rotate_180,
    _scale_contours,
)
from glyphs_serif_figs_ext import SERIF_REGULAR, build_all_serif_glyphs
from serif_primitives import SerifWeightParams, diag_foot_serif, vstem_serifed
from spacing_kerning import BASE_ANCHORS, MARK_ANCHORS, apply_class_kerning


SANS_MED_RX = 8.0
SANS_MED_RY = 5.0
SERIF_MED_RX = 8.0
SERIF_MED_RY = 2.2
MONO_MED_RX = 5.8
MONO_MED_RY = 3.5

SERIF_MEDIUM = SerifWeightParams(
    name="Medium",
    weight_value=500,
    lc_stem_v=112.0,
    lc_stem_h=46.0,
    lc_bowl_v=116.0,
    lc_join_thin=44.0,
    cap_stem_v=122.0,
    cap_stem_h=50.0,
    cap_bowl_v=128.0,
    fig_stem_v=114.0,
    fig_stem_h=48.0,
    fig_bowl_v=122.0,
    outer_tension=0.58,
    inner_tension=0.60,
    lc_serif_h=30.0,
    lc_serif_ext=46.0,
    lc_bracket=32.0,
    cap_serif_h=32.0,
    cap_serif_ext=50.0,
    cap_bracket=36.0,
)


def compute_duplex_medium_width(gname: str, reg_w: int) -> int:
    """
    Smooth optical t=0.38 width interpolation between Regular (400) and Bold (700),
    keeping locked spaces/tabular numerals/operators/0u combining marks unchanged.
    """
    if reg_w == 0:
        return 0
    if gname in _LOCKED_WIDTH_GLYPHS:
        return reg_w
    base = gname[:-5] if gname.endswith(".case") else gname
    if base in _LOCKED_WIDTH_GLYPHS:
        return reg_w
    bold_w = compute_duplex_bold_width(gname, reg_w)
    if bold_w == reg_w:
        return reg_w
    return int(round((reg_w + 0.38 * (bold_w - reg_w)) / 2.0) * 2)


DUPLEX_MEDIUM_ADVANCE_WIDTHS: Dict[str, int] = {
    gname: compute_duplex_medium_width(gname, w)
    for gname, w in DUPLEX_ADVANCE_WIDTHS.items()
}

EXT_MEDIUM_ADVANCE_WIDTHS: Dict[str, int] = {
    gname: compute_duplex_medium_width(gname, w)
    for gname, (w, _, _) in EXT_CONTOUR_BUILDERS.items()
}


def _mono_medium_ss01_ligatures() -> Dict[str, List[ContourBuilder]]:
    """600u fixed-pitch ss01 ligatures tuned for Medium (76u single bar / 76u double bars)."""
    # Single arrow axis y_mid=276 -> bar y: 238..314 (76u)
    # Double bars: lower 148..224 (76u), upper 328..404 (76u)
    return {
        "hyphen.lig_r": [rect_contour(70, 238, 600, 314)],
        "greater.lig_arrow": union_contours([
            rect_contour(0, 238, 464, 314),
            ContourBuilder((234, 82)).line_to(290, 26).line_to(524, 266).line_to(524, 286).line_to(290, 526).line_to(234, 470).line_to(434, 276),
        ]),
        "less.lig_arrow": union_contours([
            rect_contour(136, 238, 600, 314),
            ContourBuilder((76, 266)).line_to(310, 26).line_to(366, 82).line_to(166, 276).line_to(366, 470).line_to(310, 526).line_to(76, 286),
        ]),
        "hyphen.lig_l": [rect_contour(0, 238, 530, 314)],
        "equal.lig_r": [rect_contour(70, 148, 600, 224), rect_contour(70, 328, 600, 404)],
        "equal.lig_l": [rect_contour(0, 148, 530, 224), rect_contour(0, 328, 530, 404)],
        "greater.lig_fatarrow": union_contours([
            rect_contour(0, 148, 386, 224),
            rect_contour(0, 328, 386, 404),
            ContourBuilder((228, 86)).line_to(286, 28).line_to(522, 266).line_to(522, 286).line_to(286, 524).line_to(228, 466).line_to(418, 276),
        ]),
        "exclam.lig_neq": union_contours([
            rect_contour(86, 148, 600, 224),
            rect_contour(86, 328, 600, 404),
            bar_segment_contour((354, 30), (546, 522), 78),
        ]),
        "less.lig_le": [
            ContourBuilder((86, 334)).line_to(600, 230).line_to(600, 306).line_to(262, 360).line_to(600, 414).line_to(600, 490).line_to(86, 386),
            rect_contour(86, 44, 600, 120),
        ],
        "equal.lig_le": [
            ContourBuilder((0, 230)).line_to(478, 132).line_to(494, 208).line_to(0, 306),
            ContourBuilder((0, 414)).line_to(494, 512).line_to(478, 588).line_to(0, 490),
            rect_contour(0, 44, 514, 120),
        ],
        "greater.lig_ge": [
            ContourBuilder((122, 132)).line_to(600, 230).line_to(600, 306).line_to(106, 208),
            ContourBuilder((106, 512)).line_to(600, 414).line_to(600, 490).line_to(122, 588),
            rect_contour(86, 44, 600, 120),
        ],
        "equal.lig_ge": [
            ContourBuilder((0, 230)).line_to(514, 334).line_to(514, 386).line_to(0, 490).line_to(0, 414).line_to(338, 360).line_to(0, 306),
            rect_contour(0, 44, 514, 120),
        ],
    }


def _med_four(shift_x: float = 0.0, is_serif: bool = False) -> List[ContourBuilder]:
    sw = 104.0 if not is_serif else 114.0
    bh = 82.0 if not is_serif else 66.0
    xr = 472.0 + shift_x
    xl = xr - sw
    outer = (
        ContourBuilder((xl, 0))
        .line_to(xr, 0)
        .line_to(xr, 174)
        .line_to(xr + 76, 174)
        .line_to(xr + 76, 174 + bh)
        .line_to(xr, 174 + bh)
        .line_to(xr, 692)
        .line_to(332.0 + shift_x, 692)
        .line_to(40.0 + shift_x, 174 + bh)
        .line_to(40.0 + shift_x, 174)
        .line_to(xl, 174)
    )
    in_xl = lerp_x(40.0 + shift_x, 174 + bh, 332.0 + shift_x, 692, 174 + bh) + (78.0 if not is_serif else 58.0)
    inner = (
        ContourBuilder((in_xl, 174 + bh))
        .line_to(xl, 566)
        .line_to(xl, 174 + bh)
    )
    # Use upper diag intersection for triangle inner top
    y_top_in = 562.0
    return [outer, ContourBuilder((128.0 + shift_x, 174 + bh)).line_to(xl, y_top_in).line_to(xl, 174 + bh)]


def _med_perthousand(w: int = 1010) -> List[ContourBuilder]:
    sx = w / 980.0
    top_o = humanist_oval_contour(200 * sx, 526, 132, 170, 0.585, 0.59, clockwise=False)
    top_i = humanist_oval_contour(200 * sx, 526, 56, 102, 0.60, 0.60, clockwise=True)
    b1_o = humanist_oval_contour(556 * sx, 164, 128, 170, 0.585, 0.59, clockwise=False)
    b1_i = humanist_oval_contour(556 * sx, 164, 52, 102, 0.60, 0.60, clockwise=True)
    b2_o = humanist_oval_contour(840 * sx, 164, 128, 170, 0.585, 0.59, clockwise=False)
    b2_i = humanist_oval_contour(840 * sx, 164, 52, 102, 0.60, 0.60, clockwise=True)
    slash = ContourBuilder((156, -12)).line_to(230, -12).line_to(558, 700).line_to(484, 700)
    return [top_o, top_i, b1_o, b1_i, b2_o, b2_i, slash]


def _med_Delta(w: int = 628, is_serif: bool = False) -> List[ContourBuilder]:
    cap = METRICS.cap_height
    cx = w / 2.0
    bh = 62.0 if is_serif else 82.0
    xl0 = 32.0
    xr0 = w - 32.0
    outer = (
        ContourBuilder((xl0, 0))
        .line_to(xr0, 0)
        .line_to(cx + 42.0, cap)
        .line_to(cx - 42.0, cap)
    )
    lx_i = lerp_x(xl0, 0, cx - 42.0, cap, bh) + (58.0 if is_serif else 82.0)
    rx_i = lerp_x(xr0, 0, cx + 42.0, cap, bh) - (108.0 if is_serif else 86.0)
    in_y_top = cap - (124.0 if is_serif else 138.0)
    inner = ContourBuilder((lx_i, bh)).line_to(cx, in_y_top).line_to(rx_i, bh)
    return [outer, inner]


def _sans_med_germandbls() -> List[ContourBuilder]:
    c = (
        ContourBuilder((74, 0))
        .line_to(180, 0)
        .line_to(180, 560)
        .vh_to(296, 654, 0.58, 0.58)
        .hv_to(404, 554, 0.58, 0.58)
        .curve_to((404, 488), (360, 444), (274, 412), smooth=False)
        .line_to(274, 330)
        .curve_to((404, 310), (474, 256), (474, 174), smooth=False)
        .vh_to(372, 74, 0.58, 0.58)
        .curve_to((328, 74), (288, 82), (248, 94), smooth=False)
        .line_to(228, 12)
        .curve_to((280, -4), (332, -10), (388, -10), smooth=True)
        .hv_to(588, 174, 0.58, 0.58)
        .curve_to((588, 276), (526, 342), (424, 370), smooth=False)
        .curve_to((484, 412), (514, 476), (514, 556), smooth=False)
        .vh_to(296, 742, 0.58, 0.58)
        .hv_to(74, 562, 0.58, 0.58)
    )
    return [c]


def _serif_med_germandbls() -> List[ContourBuilder]:
    c = (
        ContourBuilder((74, 0))
        .line_to(184, 0)
        .line_to(184, 564)
        .vh_to(298, 666, 0.58, 0.58)
        .hv_to(404, 560, 0.58, 0.58)
        .curve_to((404, 492), (362, 448), (280, 416), smooth=False)
        .line_to(280, 340)
        .curve_to((402, 320), (472, 266), (472, 180), smooth=False)
        .vh_to(370, 60, 0.58, 0.58)
        .curve_to((326, 60), (288, 70), (250, 86), smooth=False)
        .line_to(232, 16)
        .curve_to((282, 0), (334, -10), (390, -10), smooth=True)
        .hv_to(590, 180, 0.58, 0.58)
        .curve_to((590, 280), (528, 346), (426, 374), smooth=False)
        .curve_to((484, 416), (514, 480), (514, 562), smooth=False)
        .vh_to(298, 746, 0.58, 0.58)
        .hv_to(74, 566, 0.58, 0.58)
    )
    foot = diag_foot_serif(74, 184, 0, 74, 184, 120, ext_l=42, ext_r=0, sh=30, brk=30)
    return union_contours([c, foot])


def _sans_med_AE() -> List[ContourBuilder]:
    cap = METRICS.cap_height
    yb0, yb1 = 192, 274
    xl_b0 = lerp_x(146, 0, 442, 558, yb0)
    xl_b1 = lerp_x(146, 0, 442, 558, yb1)
    outer = (
        ContourBuilder((22, 0))
        .line_to(146, 0)
        .line_to(xl_b0, yb0)
        .line_to(442, yb0)
        .line_to(442, 0)
        .line_to(894, 0)
        .line_to(894, 86)
        .line_to(564, 86)
        .line_to(564, 322)
        .line_to(856, 322)
        .line_to(856, 404)
        .line_to(564, 404)
        .line_to(564, cap - 86)
        .line_to(880, cap - 86)
        .line_to(880, cap)
        .line_to(388, cap)
    )
    inner = ContourBuilder((xl_b1, yb1)).line_to(436, 558).line_to(442, 558).line_to(442, yb1)
    return [outer, inner]


def _serif_med_A() -> List[ContourBuilder]:
    cap = METRICS.cap_height
    yb0, yb1 = 200, 252
    xl_b0 = lerp_x(112, 0, 318, 574, yb0)
    xr_b0 = lerp_x(490, 0, 326, 574, yb0)
    xl_b1 = lerp_x(112, 0, 318, 574, yb1)
    xr_b1 = lerp_x(490, 0, 326, 574, yb1)
    outer = (
        ContourBuilder((36, 0))
        .line_to(112, 0)
        .line_to(xl_b0, yb0)
        .line_to(xr_b0, yb0)
        .line_to(490, 0)
        .line_to(622, 0)
        .line_to(378, cap)
        .line_to(278, cap)
    )
    inner = ContourBuilder((xl_b1, yb1)).line_to(318, 574).line_to(326, 574).line_to(xr_b1, yb1)
    f_l = diag_foot_serif(36, 112, 0, lerp_x(36, 0, 278, cap, yb0), xl_b0, yb0, ext_l=24, ext_r=26, sh=32, brk=32)
    f_r = diag_foot_serif(490, 622, 0, xr_b0, lerp_x(622, 0, 378, cap, yb0), yb0, ext_l=26, ext_r=24, sh=32, brk=32)
    return union_contours([outer, inner, f_l, f_r])


def _serif_med_AE() -> List[ContourBuilder]:
    cap = METRICS.cap_height
    yb0, yb1 = 200, 252
    xl_b0 = lerp_x(118, 0, 446, 570, yb0)
    xl_b1 = lerp_x(118, 0, 446, 570, yb1)
    outer = (
        ContourBuilder((36, 0))
        .line_to(118, 0)
        .line_to(xl_b0, yb0)
        .line_to(446, yb0)
        .line_to(446, 0)
        .line_to(894, 0)
        .line_to(904, 152)
        .line_to(870, 152)
        .curve_to((860, 74), (826, 52), (764, 52), smooth=False)
        .line_to(564, 52)
        .line_to(564, 326)
        .line_to(814, 326)
        .line_to(814, 378)
        .line_to(564, 378)
        .line_to(564, cap - 52)
        .line_to(756, cap - 52)
        .curve_to((816, cap - 52), (848, cap - 74), (858, cap - 144), smooth=False)
        .line_to(892, cap - 144)
        .line_to(882, cap)
        .line_to(388, cap)
    )
    inner = ContourBuilder((xl_b1, yb1)).line_to(440, 570).line_to(446, 570).line_to(446, yb1)
    f_l = diag_foot_serif(36, 118, 0, lerp_x(36, 0, 388, cap, yb0), xl_b0, yb0, ext_l=24, ext_r=26, sh=32, brk=32)
    return union_contours([outer, inner, f_l])


def _mono_med_AE() -> List[ContourBuilder]:
    cap = METRICS.cap_height
    yb0, yb1 = 192, 266
    xl_b0 = lerp_x(112, 0, 290, 558, yb0)
    xl_b1 = lerp_x(112, 0, 290, 558, yb1)
    outer = (
        ContourBuilder((22, 0))
        .line_to(112, 0)
        .line_to(xl_b0, yb0)
        .line_to(290, yb0)
        .line_to(290, 0)
        .line_to(566, 0)
        .line_to(566, 78)
        .line_to(382, 78)
        .line_to(382, 320)
        .line_to(536, 320)
        .line_to(536, 396)
        .line_to(382, 396)
        .line_to(382, cap - 78)
        .line_to(556, cap - 78)
        .line_to(556, cap)
        .line_to(244, cap)
    )
    inner = ContourBuilder((xl_b1, yb1)).line_to(284, 558).line_to(290, 558).line_to(290, yb1)
    return [outer, inner]


def _mono_med_IJ() -> List[ContourBuilder]:
    cap = METRICS.cap_height
    bh = 76
    i_part = (
        ContourBuilder((36, 0))
        .line_to(236, 0)
        .line_to(236, bh)
        .line_to(184, bh)
        .line_to(184, cap - bh)
        .line_to(236, cap - bh)
        .line_to(236, cap)
        .line_to(36, cap)
        .line_to(36, cap - bh)
        .line_to(88, cap - bh)
        .line_to(88, bh)
        .line_to(36, bh)
    )
    j_part = (
        ContourBuilder((392, -12))
        .hv_to(540, 186, 0.58, 0.58)
        .line_to(540, cap)
        .line_to(336, cap)
        .line_to(336, cap - bh)
        .line_to(442, cap - bh)
        .line_to(442, 186)
        .vh_to(388, 66, 0.58, 0.58)
        .curve_to((360, 66), (336, 84), (316, 118), smooth=False)
        .line_to(262, 66)
        .curve_to((294, 14), (334, -12), (392, -12), smooth=True)
    )
    return [i_part, j_part]


def _med_superscript(digit_c: List[ContourBuilder], dx: float, dy: float) -> List[ContourBuilder]:
    return _scale_contours(digit_c, 0.58, 0.56, dx, dy)


def _med_fraction(num_c: List[ContourBuilder], den_c: List[ContourBuilder], dx_den: float) -> List[ContourBuilder]:
    num = _scale_contours(num_c, 0.56, 0.56, 42, 312)
    den = _scale_contours(den_c, 0.56, 0.56, dx_den, 0)
    slash = ContourBuilder((238, -14)).line_to(312, -14).line_to(574, 712).line_to(500, 712)
    return num + [slash] + den


def _med_lessequal(less_c: List[ContourBuilder], dx: float = 0.0, bar_t: float = 68.0) -> List[ContourBuilder]:
    raised = [c.translated(dx, 92) for c in less_c]
    return raised + [rect_contour(60 + dx, 24, 520 + dx, 24 + bar_t)]


def _med_greaterequal(gr_c: List[ContourBuilder], dx: float = 0.0, bar_t: float = 68.0) -> List[ContourBuilder]:
    raised = [c.translated(dx, 92) for c in gr_c]
    return raised + [rect_contour(60 + dx, 24, 520 + dx, 24 + bar_t)]


def _rebuild_derived_medium(
    result: Dict[str, Tuple[int, int | None, List[ContourBuilder]]],
    is_serif: bool,
    is_mono: bool,
) -> None:
    bar_t = 54.0 if is_serif else (72.0 if is_mono else 78.0)
    thin_t = 50.0 if is_serif else (64.0 if is_mono else 68.0)

    def _set(name: str, contours: List[ContourBuilder]) -> None:
        w, uni, _ = result[name]
        result[name] = (w, uni, contours)

    slash_box = (
        bar_segment_contour((156, 86), (444, 604), thin_t)
        if is_mono
        else bar_segment_contour((142, 84), (450, 606), thin_t)
    )
    z_rings = result["zero"][2][:2]
    _set("zero.slash", union_contours(z_rings + [slash_box]))
    if is_mono:
        for d in ("zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine"):
            _set(f"{d}.tnum", result[d][2])
        _set("zero.tnum.slash", result["zero.slash"][2])
    else:
        for d in ("zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine"):
            w_prop = result[d][0]
            dx = (TABULAR_FIG_WIDTH - w_prop) / 2.0
            _set(f"{d}.tnum", [c.translated(dx, 0) for c in result[d][2]])
        dx0 = (TABULAR_FIG_WIDTH - result["zero.slash"][0]) / 2.0
        _set("zero.tnum.slash", [c.translated(dx0, 0) for c in result["zero.slash"][2]])

    # Clean overlay glyphs from Medium bases
    wO = result["O"][0]
    _set("Oslash", union_contours(result["O"][2] + [bar_segment_contour((92, -34), (wO - 92, 734), thin_t)]))
    wo = result["o"][0]
    _set("oslash", union_contours(result["o"][2] + [bar_segment_contour((80, -30), (wo - 80, 550), thin_t)]))
    _set("Eth", union_contours(result["D"][2] + [rect_contour(16, 326, 300, 326 + bar_t)]))
    _set("Dcroat", result["Eth"][2])
    _set("dcroat", union_contours(result["d"][2] + [rect_contour(result["d"][0] - 300, 564, result["d"][0] - 20, 564 + bar_t)]))
    _set("Hbar", union_contours(result["H"][2] + [rect_contour(24, 506, result["H"][0] - 24, 506 + bar_t)]))
    _set("hbar", union_contours(result["h"][2] + [rect_contour(20, 570, 320, 570 + bar_t)]))
    _set("Tbar", union_contours(result["T"][2] + [rect_contour(result["T"][0] * 0.21, 336, result["T"][0] * 0.79, 336 + bar_t)]))
    _set("tbar", union_contours(result["t"][2] + [rect_contour(36, 240, result["t"][0] - 58, 240 + bar_t)]))
    _set("Lslash", union_contours(result["L"][2] + [bar_segment_contour((18, 250), (288, 450), bar_t)]))
    if is_mono:
        _set("lslash", union_contours(result["l"][2] + [bar_segment_contour((162, 306), (420, 470), 64.0)]))
    else:
        l_sh = [c.translated(12, 0) for c in result["l"][2]]
        _set("lslash", union_contours(l_sh + [bar_segment_contour((18, 306), (266, 472), bar_t)]))

    _set("dotlessi", result["i"][2][:1])
    _set("dotlessj", result["j"][2][:1])
    if is_mono:
        _set("ldot", [c.translated(-40, 0) for c in result["l"][2]] + [humanist_oval_contour(420, 286, 48, 48, 0.62, 0.62, clockwise=False)])
        _set("Ldot", result["L"][2] + [humanist_oval_contour(360, 368, 50, 50, 0.62, 0.62, clockwise=False)])
    else:
        _set("IJ", result["I"][2] + [c.translated(294, 0) for c in result["J"][2]])
        _set("ij", result["i"][2] + [c.translated(252, 0) for c in result["j"][2]])
        _set("Ldot", result["L"][2] + [humanist_oval_contour(370, 368, 52, 52, 0.62, 0.62, clockwise=False)])
        _set("ldot", result["l"][2] + [humanist_oval_contour(316, 286, 48, 48, 0.62, 0.62, clockwise=False)])
        _set("napostrophe", [c.translated(-22, 0) for c in result["quoteright"][2]] + [c.translated(174, 0) for c in result["n"][2]])

    if not is_mono:
        s_sh = _scale_contours(result["S"][2], 580.0 / result["S"][0], 1.0, 0.0, 0.0) if not is_serif else [c.translated(6, 0) for c in result["S"][2]]
        _set("dollar", union_contours(s_sh + [rect_contour(258, -90, 322 if not is_serif else 314, 782)]))
    else:
        _set("dollar", union_contours(result["S"][2] + [rect_contour(268, -90, 332, 782)]))

    c_sh = _scale_contours(result["c"][2], result["cent"][0] / result["c"][0], 1.0, 0.0, 0.0)
    cx_cent = result["cent"][0] / 2.0
    cb_w = 27.0 if is_serif else 33.0
    _set("cent", union_contours(c_sh + [rect_contour(cx_cent - cb_w, -94, cx_cent + cb_w, 614)]))

    won_base = result["W"][2] if is_mono else _scale_contours(result["W"][2], 880.0 / result["W"][0], 1.0, 22.0, 0.0)
    won_x0, won_x1 = (24, 576) if is_mono else (28, result["won"][0] - 28)
    _set("won", union_contours(won_base + [rect_contour(won_x0, 240, won_x1, 240 + thin_t), rect_contour(won_x0, 396, won_x1, 396 + thin_t)]))

    if is_mono:
        _set("notequal", union_contours(result["equal"][2] + [bar_segment_contour((160, 44), (420, 508), 72)]))
    else:
        _set("notequal", union_contours(result["equal"][2] + [bar_segment_contour((160, 44), (420, 508), thin_t)]))
    _set("approxequal", [c.translated(0, -148) for c in result["asciitilde"][2]] + [c.translated(0, 32) for c in result["asciitilde"][2]])
    _set("lessequal", _med_lessequal(result["less"][2], dx=10.0 if is_mono else 0.0, bar_t=thin_t))
    _set("greaterequal", _med_greaterequal(result["greater"][2], dx=10.0 if is_mono else 0.0, bar_t=thin_t))

    _set("exclamdown", _rotate_180(result["exclam"][2], result["exclam"][0] / 2.0, 260))
    _set("questiondown", _rotate_180(result["question"][2], result["question"][0] / 2.0, 260))
    _set("onesuperior", _med_superscript(result["one"][2], 24, 296))
    _set("twosuperior", _med_superscript(result["two"][2], 20, 304))
    _set("threesuperior", _med_superscript(result["three"][2], 20, 304))

    dx_den = 292.0 if is_mono else 420.0
    if not is_mono:
        _set("onequarter", _med_fraction(result["one"][2], result["four"][2], dx_den))
        _set("onehalf", _med_fraction(result["one"][2], result["two"][2], dx_den))
        _set("threequarters", _med_fraction(result["three"][2], result["four"][2], dx_den))
    else:
        for fn, a, b in (("onequarter", "one", "four"), ("onehalf", "one", "two"), ("threequarters", "three", "four")):
            num = _scale_contours(result[a][2], 0.50, 0.50, 24, 338)
            den = _scale_contours(result[b][2], 0.50, 0.50, 286, 0)
            slash = ContourBuilder((168, -12)).line_to(236, -12).line_to(472, 704).line_to(404, 704)
            _set(fn, num + [slash] + den)

    for sp_name, comb_name, dx_c in (
        ("acute", "acutecomb", 160), ("dieresis", "dieresiscomb", 180), ("macron", "macroncomb", 180),
        ("cedilla", "cedillacomb", 160), ("breve", "brevecomb", 180), ("dotaccent", "dotaccentcomb", 150),
        ("ring", "ringabovecomb", 160), ("ogonek", "ogonekcomb", 160), ("tilde", "tildecomb", 210),
        ("hungarumlaut", "hungarumlautcomb", 190), ("circumflex", "circumflexcomb", 180), ("caron", "caroncomb", 180),
    ):
        dx_val = 300 if is_mono else (result[sp_name][0] / 2.0 if sp_name in result else dx_c)
        _set(sp_name, [c.translated(dx_val, 0) for c in result[comb_name][2]])

    for name in list(result.keys()):
        if name.endswith(".case"):
            base_n = name[:-5]
            if base_n in result:
                _set(name, [c.translated(0, METRICS.case_shift_y) for c in result[base_n][2]])
    for alias, src_n in (
        ("hyphentwo", "hyphen"),
        ("nonbreakinghyphen", "hyphen"),
        ("softhyphen", "hyphen"),
        ("hyphentwo.case", "hyphen.case"),
        ("nonbreakinghyphen.case", "hyphen.case"),
    ):
        if alias in result and src_n in result:
            _set(alias, result[src_n][2])
    if not is_mono:
        # Review 3: a prime is a straight tapered stroke (it was a copy of the curly quote here)
        _set("minute", [ContourBuilder((74, 446)).line_to(140, 446).line_to(197, 708).line_to(105, 708)])
        _set("second", [c.translated(-16, 0) for c in result["minute"][2]] + [c.translated(144, 0) for c in result["minute"][2]])


def build_all_sans_medium_glyphs() -> Dict[str, Tuple[int, int | None, List[ContourBuilder]]]:
    reg = build_all_sans_glyphs()
    result: Dict[str, Tuple[int, int | None, List[ContourBuilder]]] = {}
    explicit: Dict[str, Callable[[], List[ContourBuilder]]] = {
        "four": lambda: _med_four(0.0, False),
        "AE": _sans_med_AE,
        "germandbls": _sans_med_germandbls,
        "perthousand": lambda: _med_perthousand(1010),
        "Delta": lambda: _med_Delta(628, False),
        "increment": lambda: _med_Delta(628, False),
    }
    for gname, (orig_w, uni, contours) in reg.items():
        nw = compute_duplex_medium_width(gname, orig_w)
        if gname in explicit:
            result[gname] = (nw, uni, explicit[gname]())
        elif gname == ".notdef":
            result[gname] = (nw, uni, [rect_contour(64, 0, 536, 700, False), rect_contour(150, 86, 450, 614, True)])
        elif orig_w == 0:
            result[gname] = (0, uni, bolden_contours_smooth(contours, 0, 0, 5.0, 3.5, is_mark=True))
        else:
            result[gname] = (nw, uni, bolden_contours_smooth(contours, orig_w, nw, SANS_MED_RX, SANS_MED_RY))
    _rebuild_derived_medium(result, is_serif=False, is_mono=False)
    return result


def build_all_serif_medium_glyphs() -> Dict[str, Tuple[int, int | None, List[ContourBuilder]]]:
    reg = build_all_serif_glyphs(SERIF_REGULAR)
    result: Dict[str, Tuple[int, int | None, List[ContourBuilder]]] = {}
    explicit: Dict[str, Callable[[], List[ContourBuilder]]] = {
        "A": _serif_med_A,
        "four": lambda: _med_four(0.0, True),
        "AE": _serif_med_AE,
        "germandbls": _serif_med_germandbls,
        "perthousand": lambda: _med_perthousand(1010),
        "Delta": lambda: _med_Delta(628, True),
        "increment": lambda: _med_Delta(628, True),
    }
    for gname, (orig_w, uni, contours) in reg.items():
        nw = compute_duplex_medium_width(gname, orig_w)
        if gname in explicit:
            result[gname] = (nw, uni, explicit[gname]())
        elif gname == ".notdef":
            result[gname] = (nw, uni, [rect_contour(64, 0, 536, 700, False), rect_contour(150, 86, 450, 614, True)])
        elif orig_w == 0:
            result[gname] = (0, uni, bolden_contours_smooth(contours, 0, 0, 5.0, 3.5, is_mark=True))
        else:
            result[gname] = (nw, uni, bolden_contours_smooth(contours, orig_w, nw, SERIF_MED_RX, SERIF_MED_RY))
    _rebuild_derived_medium(result, is_serif=True, is_mono=False)
    return result


def build_all_mono_medium_glyphs() -> Dict[str, Tuple[int, int | None, List[ContourBuilder]]]:
    reg = build_all_mono_glyphs(MONO_REGULAR)
    result: Dict[str, Tuple[int, int | None, List[ContourBuilder]]] = {}
    ss01_map = _mono_medium_ss01_ligatures()
    explicit: Dict[str, Callable[[], List[ContourBuilder]]] = {
        "AE": _mono_med_AE,
        "IJ": _mono_med_IJ,
        "perthousand": lambda: _scale_contours(_med_perthousand(1010), 0.56, 1.0, 14, 0),
    }
    for gname, (orig_w, uni, contours) in reg.items():
        if gname in ss01_map:
            result[gname] = (MONO_WIDTH, None, ss01_map[gname])
        elif gname in explicit:
            result[gname] = (MONO_WIDTH, uni, explicit[gname]())
        elif gname == ".notdef":
            result[gname] = (MONO_WIDTH, uni, [rect_contour(64, 0, 536, 700, False), rect_contour(150, 86, 450, 614, True)])
        elif orig_w == 0:
            result[gname] = (0, uni, bolden_contours_smooth(contours, 0, 0, 5.0, 3.5, is_mark=True))
        else:
            result[gname] = (MONO_WIDTH, uni, bolden_contours_smooth(contours, MONO_WIDTH, MONO_WIDTH, MONO_MED_RX, MONO_MED_RY))
    _rebuild_derived_medium(result, is_serif=False, is_mono=True)
    return result


def attach_medium_anchors_and_composites(ufo: ufoLib2.Font, *, is_monospace: bool = False) -> None:
    """Attach centered/scaled anchors and depth-1 composites with propagated anchors."""
    from fontTools.pens.boundsPen import BoundsPen

    mark_anchors_med = dict(MARK_ANCHORS)
    mark_anchors_med["dieresiscomb.cap"] = {"_top": (0, 700), "top": (0, 814)}
    mark_anchors_med["macroncomb.cap"] = {"_top": (0, 700), "top": (0, 814)}
    mark_anchors_med["acutecomb.cap"] = {"_top": (0, 700), "top": (0, 864)}
    mark_anchors_med["gravecomb.cap"] = {"_top": (0, 700), "top": (0, 864)}
    mark_anchors_med["caroncomb.cap"] = {"_top": (0, 700), "top": (0, 864)}

    for mname, adict in mark_anchors_med.items():
        if mname in ufo:
            ufo[mname].anchors = [
                ufoLib2.objects.Anchor(x=ax, y=ay, name=aname)
                for aname, (ax, ay) in adict.items()
            ]

    reg_widths_all = dict(DUPLEX_ADVANCE_WIDTHS)
    for gn, (rw, _, _) in EXT_CONTOUR_BUILDERS.items():
        reg_widths_all[gn] = rw

    special_top_x_mono = {
        "L": 120.0, "b": 124.0, "d": 476.0, "h": 122.0, "k": 148.0,
        "l": 298.0, "t": 244.0, "i": 300.0, "dotlessi": 300.0, "j": 340.0, "dotlessj": 340.0,
    }
    special_ogonek_mono = {
        "A": (514.0, 0.0), "E": (466.0, 0.0), "I": (312.0, 0.0), "U": (494.0, 4.0),
        "a": (460.0, 0.0), "e": (414.0, 12.0), "i": (342.0, 0.0), "dotlessi": (342.0, 0.0), "u": (468.0, 0.0),
    }

    for bname, orig_anchors in BASE_ANCHORS.items():
        if bname not in ufo:
            continue
        g = ufo[bname]
        if is_monospace:
            bpen = BoundsPen(ufo)
            g.draw(bpen)
            cx = round((bpen.bounds[0] + bpen.bounds[2]) / 2.0) if bpen.bounds else 300.0
            new_a = []
            for aname, (_, ay) in orig_anchors.items():
                if aname == "top":
                    new_a.append(ufoLib2.objects.Anchor(x=special_top_x_mono.get(bname, cx), y=ay, name="top"))
                elif aname == "bottom":
                    new_a.append(ufoLib2.objects.Anchor(x=298.0 if bname == "l" else cx, y=ay, name="bottom"))
                elif aname == "ogonek":
                    ox, oy = special_ogonek_mono.get(bname, (cx + 80.0, ay))
                    new_a.append(ufoLib2.objects.Anchor(x=ox, y=oy, name="ogonek"))
            g.anchors = new_a
        else:
            rw = reg_widths_all.get(bname, g.width)
            sx = g.width / rw if rw > 0 else 1.0
            g.anchors = [
                ufoLib2.objects.Anchor(x=round(ax * sx), y=ay, name=aname)
                for aname, (ax, ay) in orig_anchors.items()
            ]

    glyph_order = list(ufo.lib.get("public.glyphOrder", []))
    for comp_name, uni, base_name, mark_name, anchor_name in COMPOSITE_RECIPES:
        base_g = ufo[base_name]
        mark_g = ufo[mark_name]

        if comp_name in ("dcaron", "lcaron", "tcaron", "Lcaron"):
            if is_monospace:
                dx_map = {"dcaron": 546, "lcaron": 404, "tcaron": 374, "Lcaron": 276}
                dy_map = {"dcaron": 20, "lcaron": 18, "tcaron": 22, "Lcaron": 0}
                w_override = {}
            else:
                dx_map = {"dcaron": 592, "lcaron": 236, "tcaron": 280, "Lcaron": 274}
                dy_map = {"dcaron": 16, "lcaron": 16, "tcaron": -16, "Lcaron": 0}
                w_override = {"dcaron": 692, "lcaron": 334, "tcaron": 368, "Lcaron": 566}
            dx, dy = dx_map[comp_name], dy_map[comp_name]
        else:
            w_override = {}
            b_anc = next(a for a in base_g.anchors if a.name == anchor_name)
            m_anc = next(a for a in mark_g.anchors if a.name == f"_{anchor_name}")
            dx = round(b_anc.x - m_anc.x)
            dy = round(b_anc.y - m_anc.y)

        g = ufo.newGlyph(comp_name)
        g.width = MONO_WIDTH if is_monospace else w_override.get(comp_name, base_g.width)
        if uni is not None:
            g.unicodes = [uni]

        if base_g.components:
            for sub_c in base_g.components:
                g.components.append(
                    ufoLib2.objects.Component(baseGlyph=sub_c.baseGlyph, transformation=sub_c.transformation)
                )
        else:
            g.components.append(ufoLib2.objects.Component(baseGlyph=base_name, transformation=(1, 0, 0, 1, 0, 0)))
        g.components.append(ufoLib2.objects.Component(baseGlyph=mark_name, transformation=(1, 0, 0, 1, dx, dy)))

        mark_out = {a.name: a for a in mark_g.anchors if not a.name.startswith("_")}
        prop_anchors = []
        for a in base_g.anchors:
            if comp_name not in ("dcaron", "lcaron", "tcaron", "Lcaron") and a.name == anchor_name and anchor_name in mark_out:
                m_out = mark_out[anchor_name]
                prop_anchors.append(ufoLib2.objects.Anchor(x=round(dx + m_out.x), y=round(dy + m_out.y), name=a.name))
            else:
                prop_anchors.append(ufoLib2.objects.Anchor(x=a.x, y=a.y, name=a.name))
        g.anchors = prop_anchors
        glyph_order.append(comp_name)

    ufo.lib["public.glyphOrder"] = glyph_order


def apply_medium_class_kerning(ufo: ufoLib2.Font) -> None:
    """Apply shared class-based kerning onto Sans Medium & Serif Medium (0px reflow)."""
    apply_class_kerning(ufo)
