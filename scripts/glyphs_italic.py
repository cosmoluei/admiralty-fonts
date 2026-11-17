"""
Milestone 7 True Duplexed Italics (Regular Italic 400, Medium Italic 500, Bold Italic 700) for:
  - Admiralty Serif Italic (literary cursive italic: single-story a, full-descender f,
    looped diagonal-bar e, single-story cursive g, angled entry flags + upturned exit hooks)
  - Admiralty Sans Italic (humanist italic: single-story a, descended f tail, 1:1 duplex)
  - Admiralty Mono Italic (strict 600u fixed pitch, cursive a/f/i/l, seamlessly sheared ss01)

True 9.5-deg italic angle, pivoted at y = 260 (x-height/2), passed through pathops + Qu2Cu +
cubic extremum splitting so all 9 Italic fonts pass Google-Fonts outline audits cleanly.
"""

from __future__ import annotations
import math
from typing import Callable, Dict, List, Tuple

import pathops
import ufoLib2

from design_system import (
    ContourBuilder,
    DUPLEX_ADVANCE_WIDTHS,
    METRICS,
    TABULAR_FIG_WIDTH,
    bar_segment_contour,
    humanist_oval_contour,
    lerp_x,
    rect_contour,
    union_contours,
)
from glyphs_bold import (
    MONO_BOLD_RX,
    MONO_BOLD_RY,
    SANS_BOLD_RX,
    SANS_BOLD_RY,
    SERIF_BOLD_RX,
    SERIF_BOLD_RY,
    bolden_contours_smooth,
    compute_duplex_bold_width,
)
from glyphs_medium import (
    MONO_MED_RX,
    MONO_MED_RY,
    SANS_MED_RX,
    SANS_MED_RY,
    SERIF_MED_RX,
    SERIF_MED_RY,
    _rebuild_derived_medium,
    compute_duplex_medium_width,
)
from glyphs_mono import MONO_REGULAR, MONO_WIDTH, build_all_mono_glyphs
from glyphs_sans import build_all_sans_glyphs
from glyphs_sans_latin_ext import COMPOSITE_RECIPES, EXT_CONTOUR_BUILDERS, _rotate_180, _scale_contours
from glyphs_serif_figs_ext import SERIF_REGULAR, build_all_serif_glyphs
from serif_primitives import SerifWeightParams, diag_foot_serif, diag_head_serif, foot_pad_ccw, vstem_serifed
from spacing_kerning import BASE_ANCHORS, MARK_ANCHORS, apply_class_kerning
from symbols_engine import _path_to_clean_contours


# Review 3: extra reach of the exit hooks (units, upright frame). The heavier weights are made by
# thickening the Italic 400 shapes; the white wedge between a stem and its exit hook is only about
# 50 units wide, so it closed up into a sharp notch. The hooks of the base shapes are drawn a
# little longer before thickening (0 for 400, more for 500 and 700) so the wedge stays open.
_HOOK_EXTRA = 0.0


def _hx(f: float = 1.0) -> float:
    return _HOOK_EXTRA * f


ITALIC_ANGLE = -9.5
SLANT_K = math.tan(math.radians(-ITALIC_ANGLE))   # ~0.1673426
CARET_SLOPE_RUN = int(round(1000.0 * SLANT_K))   # 167
ITALIC_PIVOT_Y = 260.0


def slant_contours_clean(
    cbs: List[ContourBuilder],
    y_piv: float = ITALIC_PIVOT_Y,
    dx: float = 0.0,
) -> List[ContourBuilder]:
    """
    Shear contours cleanly by +9.5 deg around y_piv, then normalize winding, quadratics,
    and split any new cubic X/Y extrema introduced by the shear transform.
    """
    if not cbs:
        return []
    sk = pathops.Path()

    def _sx(pt: Tuple[float, float]) -> Tuple[float, float]:
        return (pt[0] + SLANT_K * (pt[1] - y_piv) + dx, pt[1])

    for cb in cbs:
        sk.moveTo(*_sx(cb.start))
        for op in cb.ops:
            if op[0] == "line":
                sk.lineTo(*_sx(op[1]))
            elif op[0] == "curve":
                sk.cubicTo(*_sx(op[1]), *_sx(op[2]), *_sx(op[3]))
        sk.close()
    return _path_to_clean_contours(sk)


# ---------------------------------------------------------------------------
# Reusable Cursive Italic Stroke Primitives (Upright Frame before Shear)
# ---------------------------------------------------------------------------

def _cursive_entry_stem(
    x0: float,
    x1: float,
    y_bot: float,
    y_top: float,
    *,
    entry_tl: float = 34.0,
    exit_hook_r: float = 0.0,
    exit_y_bot: float = -10.0,
    bl_serif: float = 0.0,
    br_serif: float = 0.0,
) -> ContourBuilder:
    """
    Build a cursive serif-italic stem with optional sloped calligraphic entry flag at y_top
    and optional upturned baseline calligraphic exit hook on the right.
    """
    if exit_hook_r > 0:
        # Stem ends in smooth curved upturned finial without flat serif slab
        cb = ContourBuilder((x1 + exit_hook_r, exit_y_bot))
        cb.curve_to((x1 + exit_hook_r + 36 + _hx(0.4), exit_y_bot), (x1 + exit_hook_r + 58 + _hx(0.8), 22), (x1 + exit_hook_r + 70 + _hx(), 56), smooth=False)
        cb.line_to(x1 + exit_hook_r + 48 + _hx(), 72)
        # Review 3: the top of the exit hook runs into the stem as one wide concave curve.
        # Before, it met the stem in a sharp notch at y = 32 (visible in a d h l m n r u).
        cb.curve_to((x1 + exit_hook_r + 28 + _hx(0.7), 28), (x1, 30), (x1, 128), smooth=False)
        cb.line_to(x1, y_top)
    else:
        return vstem_serifed(
            x0, x1, y_bot, y_top,
            bl=bl_serif, br=br_serif, tl=entry_tl, tl_flag=(entry_tl > 0), sh=26, brk=30,
        )

    if entry_tl > 0:
        cb.line_to(x1 - 14, y_top + 12)
        cb.line_to(x0 - entry_tl, y_top - 22)
        cb.line_to(x0 - entry_tl, y_top - 44)
        cb.curve_to(
            (x0 - entry_tl * 0.32, y_top - 44),
            (x0, y_top - 44 - 10),
            (x0, y_top - 72),
            smooth=False,
        )
    else:
        cb.line_to(x0, y_top)

    cb.line_to(x0, 108)
    cb.vh_to(x1 + exit_hook_r, exit_y_bot, 0.60, 0.60)
    return cb


# ---------------------------------------------------------------------------
# Admiralty Serif Italic — True Literary Cursive Base Glyphs (w=Regular)
# ---------------------------------------------------------------------------

def _serif_it_a() -> List[ContourBuilder]:
    """Single-story cursive italic 'a' (w=548): pear oval bowl + cursive exit hook."""
    top = METRICS.x_height + METRICS.lc_overshoot  # 530
    bot = -METRICS.lc_overshoot                    # -10
    bowl_out = (
        ContourBuilder((224, bot))
        .curve_to((296, bot), (350, 22), (382, 74), smooth=False)
        .line_to(382, 434)
        .curve_to((348, 496), (294, top), (228, top), smooth=False)
        .hv_to(48, 256, 0.58, 0.585)
        .vh_to(224, bot, 0.585, 0.58)
    )
    bowl_in = (
        ContourBuilder((242, 42))
        .hv_to(146, 258, 0.59, 0.60)
        .vh_to(242, 480, 0.60, 0.59)
        .hv_to(372, 338, 0.56, 0.56)
        .line_to(372, 178)
        .vh_to(242, 42, 0.56, 0.56)
    )
    stem_exit = (
        ContourBuilder((432, bot))
        .curve_to((472 + _hx(0.4), bot), (502 + _hx(0.8), 22), (522 + _hx(), 62), smooth=False)
        .line_to(496 + _hx(), 80)
        # Review 3: one wide concave curve from the hook into the stem (no notch)
        .curve_to((476 + _hx(0.7), 36), (446, 30), (446, 128), smooth=False)
        .line_to(446, 520)
        .line_to(362, 520)
        .line_to(362, 92)
        .vh_to(432, bot, 0.58, 0.58)
    )
    return union_contours([bowl_out, bowl_in, stem_exit])


def _serif_it_e() -> List[ContourBuilder]:
    """Cursive italic 'e' (w=552): swept rising calligraphic eye bar."""
    top = METRICS.x_height + METRICS.lc_overshoot
    bot = -METRICS.lc_overshoot
    outer = (
        ContourBuilder((286, bot))
        .curve_to((376, bot), (444, 24), (488, 92), smooth=False)
        .line_to(456, 124)
        .curve_to((416, 62), (360, 38), (294, 38), smooth=True)
        .curve_to((206, 38), (150, 114), (146, 212), smooth=False)
        .curve_to((262, 228), (390, 260), (498, 294), smooth=False)
        .line_to(498, 304)
        .vh_to(284, top, 0.58, 0.58)
        .hv_to(50, 260, 0.58, 0.59)
        .vh_to(286, bot, 0.59, 0.58)
    )
    inner = (
        ContourBuilder((152, 264))
        .curve_to((166, 404), (218, 482), (288, 482), smooth=True)
        .curve_to((356, 482), (402, 424), (408, 326), smooth=False)
        .curve_to((322, 298), (230, 276), (152, 264), smooth=False)
    )
    return [outer, inner]


def _serif_it_f() -> List[ContourBuilder]:
    """Full-descender literary cursive 'f' (w=348, top 752 to bottom -212)."""
    xh = METRICS.x_height
    stem = (
        ContourBuilder((50, -214))
        .curve_to((146, -214), (194, -138), (194, -4), smooth=False)
        .line_to(194, 616)
        .vh_to(258, 706, 0.58, 0.58)
        .hv_to(272, 672, 0.55, 0.55)
        .vh_to(308, 636, 0.58, 0.58)
        .hv_to(348, 680, 0.58, 0.58)
        .vh_to(260, 754, 0.58, 0.58)
        .hv_to(104, 604, 0.58, 0.58)
        .line_to(104, -18)
        .curve_to((104, -124), (82, -170), (50, -170), smooth=False)
        .hv_to(38, -138, 0.55, 0.55)
        .vh_to(2, -104, 0.58, 0.58)
        .hv_to(-32, -144, 0.58, 0.58)
        .vh_to(50, -214, 0.58, 0.58)
    )
    bar = ContourBuilder((28, 472)).line_to(312, 472).line_to(312, xh).line_to(28, xh)
    return union_contours([stem, bar])


def _serif_it_g() -> List[ContourBuilder]:
    """Single-story cursive italic 'g' (w=572): clean 2-contour open loop + pear finial."""
    top = METRICS.x_height + METRICS.lc_overshoot
    bot = -METRICS.lc_overshoot
    bowl_out = (
        ContourBuilder((224, bot))
        .curve_to((296, bot), (350, 22), (382, 74), smooth=False)
        .line_to(382, 434)
        .curve_to((348, 496), (294, top), (228, top), smooth=False)
        .hv_to(48, 256, 0.58, 0.585)
        .vh_to(224, bot, 0.585, 0.58)
    )
    bowl_in = (
        ContourBuilder((242, 42))
        .hv_to(146, 258, 0.59, 0.60)
        .vh_to(242, 480, 0.60, 0.59)
        .hv_to(372, 338, 0.56, 0.56)
        .line_to(372, 178)
        .vh_to(242, 42, 0.56, 0.56)
    )
    tail = (
        ContourBuilder((226, -222))
        .curve_to((360, -222), (452, -148), (452, 8), smooth=False)
        .line_to(452, 520)
        .line_to(362, 520)
        .line_to(362, 6)
        .curve_to((362, -118), (308, -172), (226, -172), smooth=True)
        .curve_to((182, -172), (146, -150), (124, -120), smooth=False)
        .line_to(84, -162)
        .curve_to((120, -202), (168, -222), (226, -222), smooth=False)
    )
    return union_contours([bowl_out, bowl_in, tail])


def _serif_it_i() -> List[ContourBuilder]:
    xh = METRICS.x_height
    stem = _cursive_entry_stem(66, 152, 0, xh, entry_tl=34, exit_hook_r=2, exit_y_bot=-10)
    dot = humanist_oval_contour(112, 662, 52, 52, 0.60, 0.60, clockwise=False)
    return [stem, dot]


def _serif_it_l() -> List[ContourBuilder]:
    return [_cursive_entry_stem(66, 154, 0, METRICS.ascender, entry_tl=34, exit_hook_r=2, exit_y_bot=-10)]


def _serif_it_h() -> List[ContourBuilder]:
    asc = METRICS.ascender
    top = METRICS.x_height + METRICS.lc_overshoot
    sL = vstem_serifed(64, 154, 0, asc, bl=36, br=30, tl=38, tl_flag=True, sh=26, brk=30)
    arch = (
        ContourBuilder((138, 344))
        .line_to(154, 344)
        .curve_to((154, 422), (218, 482), (296, 482), smooth=False)
        .hv_to(388, 330, 0.56, 0.58)
        .line_to(388, 96)
        .vh_to(452, -10, 0.60, 0.60)
        .curve_to((492 + _hx(0.4), -10), (522 + _hx(0.8), 22), (542 + _hx(), 60), smooth=False)
        .line_to(516 + _hx(), 78)
        # Review 3: one wide concave curve from the hook into the stem (no notch)
        .curve_to((496 + _hx(0.7), 34), (462, 30), (462, 128), smooth=False)
        .line_to(462, 338)
        .vh_to(314, top, 0.58, 0.58)
        .curve_to((236, top), (174, 498), (138, 438), smooth=False)
    )
    return union_contours([sL, arch])


def _serif_it_d() -> List[ContourBuilder]:
    asc = METRICS.ascender
    top = METRICS.x_height + METRICS.lc_overshoot
    bot = -METRICS.lc_overshoot
    bowl_out = (
        ContourBuilder((240, bot))
        .curve_to((322, bot), (386, 20), (424, 72), smooth=False)
        .line_to(424, 448)
        .curve_to((384, 500), (320, top), (242, top), smooth=False)
        .hv_to(46, 260, 0.58, 0.585)
        .vh_to(240, bot, 0.585, 0.58)
    )
    bowl_in = (
        ContourBuilder((262, 38))
        .hv_to(142, 260, 0.59, 0.605)
        .vh_to(262, 482, 0.605, 0.59)
        .hv_to(396, 340, 0.56, 0.56)
        .line_to(396, 180)
        .vh_to(262, 38, 0.56, 0.56)
    )
    stem = _cursive_entry_stem(396, 484, 0, asc, entry_tl=36, exit_hook_r=2, exit_y_bot=-10)
    return union_contours([bowl_out, bowl_in, stem])


def _serif_it_n() -> List[ContourBuilder]:
    xh = METRICS.x_height
    top = xh + METRICS.lc_overshoot
    sL = vstem_serifed(64, 154, 0, xh, bl=36, br=30, tl=38, tl_flag=True, sh=26, brk=30)
    arch = (
        ContourBuilder((138, 344))
        .line_to(154, 344)
        .curve_to((154, 422), (218, 482), (296, 482), smooth=False)
        .hv_to(388, 330, 0.56, 0.58)
        .line_to(388, 96)
        .vh_to(452, -10, 0.60, 0.60)
        .curve_to((492 + _hx(0.4), -10), (522 + _hx(0.8), 22), (542 + _hx(), 60), smooth=False)
        .line_to(516 + _hx(), 78)
        # Review 3: one wide concave curve from the hook into the stem (no notch)
        .curve_to((496 + _hx(0.7), 34), (462, 30), (462, 128), smooth=False)
        .line_to(462, 338)
        .vh_to(314, top, 0.58, 0.58)
        .curve_to((236, top), (174, 498), (138, 438), smooth=False)
    )
    return union_contours([sL, arch])


def _serif_it_m() -> List[ContourBuilder]:
    xh = METRICS.x_height
    top = xh + METRICS.lc_overshoot
    s1 = vstem_serifed(62, 148, 0, xh, bl=34, br=26, tl=36, tl_flag=True, sh=26, brk=28)
    arches = (
        ContourBuilder((136, 344))
        .line_to(148, 344)
        .curve_to((148, 420), (204, 482), (278, 482), smooth=False)
        .hv_to(378, 330, 0.56, 0.58)
        .line_to(378, 0)
        .line_to(462, 0)
        .line_to(462, 344)
        .curve_to((462, 420), (518, 482), (592, 482), smooth=False)
        .hv_to(690, 330, 0.56, 0.58)
        .line_to(690, 96)
        .vh_to(752, -10, 0.60, 0.60)
        .curve_to((792 + _hx(0.4), -10), (822 + _hx(0.8), 22), (840 + _hx(), 60), smooth=False)
        .line_to(814 + _hx(), 78)
        # Review 3: one wide concave curve from the hook into the stem (no notch)
        .curve_to((794 + _hx(0.7), 34), (760, 30), (760, 128), smooth=False)
        .line_to(760, 340)
        .vh_to(610, top, 0.58, 0.58)
        .curve_to((534, top), (480, 498), (452, 434), smooth=False)
        .curve_to((434, 496), (380, top), (298, top), smooth=False)
        .curve_to((222, top), (168, 498), (136, 438), smooth=False)
    )
    f2 = foot_pad_ccw(378, 462, 0, ext_l=24, ext_r=24, sh=26, brk=28)
    return union_contours([s1, arches, f2])


def _serif_it_r() -> List[ContourBuilder]:
    xh = METRICS.x_height
    top = xh + METRICS.lc_overshoot
    sL = _cursive_entry_stem(66, 152, 0, xh, entry_tl=34, exit_hook_r=2, exit_y_bot=-10)
    arm = (
        ContourBuilder((138, 316))
        .line_to(152, 316)
        .vh_to(244, 476, 0.58, 0.58)
        .hv_to(256, 436, 0.55, 0.55)
        .vh_to(296, 394, 0.58, 0.58)
        .hv_to(340, 442, 0.58, 0.58)
        .vh_to(256, top, 0.58, 0.58)
        .curve_to((206, top), (166, 492), (138, 426), smooth=False)
    )
    return union_contours([sL, arm])


def _serif_it_u() -> List[ContourBuilder]:
    xh = METRICS.x_height
    bot = -METRICS.lc_overshoot
    sL = vstem_serifed(66, 156, 180, xh, tl=34, tl_flag=True, sh=26, brk=30)
    sR = _cursive_entry_stem(384, 472, 0, xh, entry_tl=34, exit_hook_r=2, exit_y_bot=-10)
    arch = (
        ContourBuilder((238, bot))
        .curve_to((314, bot), (372, 22), (404, 78), smooth=False)
        .line_to(404, 184)
        .line_to(384, 184)
        .vh_to(256, 38, 0.56, 0.58)
        .hv_to(156, 190, 0.58, 0.56)
        .line_to(66, 190)
        .line_to(66, 180)
        .vh_to(238, bot, 0.58, 0.58)
    )
    return union_contours([sL, sR, arch])


def _serif_it_k() -> List[ContourBuilder]:
    asc = METRICS.ascender
    xh = METRICS.x_height
    sL = vstem_serifed(64, 154, 0, asc, bl=36, br=30, tl=38, tl_flag=True, sh=26, brk=30)
    arms = (
        ContourBuilder((140, 224))
        # Review 3: the leg keeps an even width down to the ankle and both sides run into the
        # tail without a corner (the old leg narrowed to 35 units and turned with two kinks).
        .line_to(208, 284)
        .line_to(310, 100)
        .curve_to((340, 46), (372, -10), (414, -10), smooth=False)
        .curve_to((454, -10), (484, 20), (502, 58), smooth=False)
        .line_to(474, 76)
        .curve_to((460, 44), (446, 36), (432, 36), smooth=False)
        .curve_to((414, 36), (396, 52), (380, 86), smooth=False)
        .line_to(262, 342)
        .line_to(458, xh)
        .line_to(382, xh)
        .line_to(140, 294)
    )
    h_arm = diag_head_serif(
        382, 458, xh, lerp_x(382, xh, 140, 294, 342), 262, 342,
        ext_l=20, ext_r=20, sh=26, brk=26,
    )
    return union_contours([sL, arms, h_arm])


def _serif_it_ae() -> List[ContourBuilder]:
    """Cursive italic 'ae' (w=848): single-story oval a + rising diagonal-bar e."""
    top, bot = 530, -10
    outer = (
        ContourBuilder((224, bot))
        .curve_to((296, bot), (350, 22), (382, 74), smooth=False)
        .line_to(410, 74)
        .curve_to((448, 22), (514, bot), (602, bot), smooth=True)
        .curve_to((692, bot), (760, 24), (804, 92), smooth=False)
        .line_to(772, 124)
        .curve_to((732, 62), (676, 38), (610, 38), smooth=True)
        .curve_to((522, 38), (466, 114), (462, 212), smooth=False)
        .curve_to((578, 228), (706, 260), (814, 294), smooth=False)
        .line_to(814, 304)
        .vh_to(600, top, 0.58, 0.58)
        # Review 3: own straight stem for the a, open notch before the e (it read as oe)
        .curve_to((520, top), (470, 470), (466, 372), smooth=False)
        .line_to(466, 520)
        .line_to(380, 520)
        .curve_to((336, 528), (284, top), (228, top), smooth=False)
        .hv_to(48, 256, 0.58, 0.585)
        .vh_to(224, bot, 0.585, 0.58)
    )
    in_a = (
        ContourBuilder((242, 42))
        .hv_to(146, 258, 0.59, 0.60)
        .vh_to(242, 480, 0.60, 0.59)
        .hv_to(362, 338, 0.56, 0.56)
        .line_to(362, 178)
        .vh_to(242, 42, 0.56, 0.56)
    )
    in_e = (
        ContourBuilder((520, 272))      # Review 3: counter moved right with the lower e join
        .curve_to((530, 400), (566, 476), (616, 476), smooth=True)
        .curve_to((678, 476), (718, 424), (724, 326), smooth=False)
        .curve_to((652, 302), (584, 284), (520, 272), smooth=False)
    )
    return [outer, in_a, in_e]


def _serif_it_oe() -> List[ContourBuilder]:
    """Cursive italic 'oe' (w=868): oval o fused smoothly into rising-bar e."""
    top, bot = 530, -10
    outer = (
        ContourBuilder((260, bot))
        .curve_to((336, bot), (394, 18), (426, 68), smooth=False)
        .line_to(442, 68)
        .curve_to((480, 18), (542, bot), (626, bot), smooth=True)
        .curve_to((714, bot), (782, 24), (826, 92), smooth=False)
        .line_to(794, 124)
        .curve_to((754, 62), (698, 38), (634, 38), smooth=True)
        .curve_to((546, 38), (492, 114), (488, 212), smooth=False)
        .curve_to((602, 228), (730, 260), (836, 294), smooth=False)
        .line_to(836, 304)
        .vh_to(624, top, 0.58, 0.58)
        .curve_to((548, top), (484, 496), (442, 434), smooth=False)
        .line_to(426, 434)
        .curve_to((388, 496), (332, top), (260, top), smooth=False)
        .hv_to(46, 260, 0.58, 0.59)
        .vh_to(260, bot, 0.59, 0.58)
    )
    in_o = (
        ContourBuilder((264, 38))
        .hv_to(146, 260, 0.59, 0.605)
        .vh_to(264, 482, 0.605, 0.59)
        .hv_to(388, 338, 0.56, 0.56)
        .line_to(388, 182)
        .vh_to(264, 38, 0.56, 0.56)
    )
    in_e = (
        ContourBuilder((494, 264))
        .curve_to((508, 404), (558, 482), (628, 482), smooth=True)
        .curve_to((696, 482), (742, 424), (748, 326), smooth=False)
        .curve_to((662, 298), (572, 276), (494, 264), smooth=False)
    )
    return [outer, in_o, in_e]


# ---------------------------------------------------------------------------
# Admiralty Sans Italic — Calm Humanist Italic Base Glyphs (w=Regular)
# ---------------------------------------------------------------------------

def _sans_it_a() -> List[ContourBuilder]:
    """Single-story humanist italic 'a' (w=548): open oval bowl + calm humanist exit tail."""
    top, bot = 530, -10
    bowl_out = (
        ContourBuilder((236, bot))
        .curve_to((312, bot), (368, 22), (398, 72), smooth=False)
        .line_to(398, 438)
        .curve_to((364, 498), (308, top), (236, top), smooth=False)
        .hv_to(48, 260, 0.58, 0.585)
        .vh_to(236, bot, 0.585, 0.58)
    )
    bowl_in = (
        ContourBuilder((250, 64))
        .hv_to(138, 260, 0.585, 0.59)
        .vh_to(250, 456, 0.59, 0.585)
        .hv_to(386, 336, 0.56, 0.56)
        .line_to(386, 184)
        .vh_to(250, 64, 0.56, 0.56)
    )
    stem_tail = (
        ContourBuilder((438, -8))
        .curve_to((468 + _hx(0.4), -8), (496 + _hx(0.8), 0), (518 + _hx(), 18), smooth=False)
        .line_to(508 + _hx(), 86)
        # Review 3: one wide concave curve from the tail into the stem (no notch)
        .curve_to((492 + _hx(0.7), 68), (462, 62), (462, 150), smooth=False)
        .line_to(462, 520)
        .line_to(378, 520)
        .line_to(378, 88)
        .vh_to(438, -8, 0.58, 0.58)
    )
    return union_contours([bowl_out, bowl_in, stem_tail])


def _sans_it_f() -> List[ContourBuilder]:
    """Tailed humanist italic 'f' (w=348, top 748 to bottom -188)."""
    stem = (
        ContourBuilder((46, -190))
        .curve_to((148, -190), (194, -124), (194, 0), smooth=False)
        .line_to(194, 608)
        .vh_to(252, 672, 0.58, 0.58)
        .curve_to((272, 672), (294, 666), (314, 656), smooth=False)
        .line_to(326, 728)
        .curve_to((298, 742), (270, 748), (244, 748), smooth=False)
        .hv_to(108, 598, 0.58, 0.58)
        .line_to(108, -10)
        .curve_to((108, -94), (82, -118), (46, -118), smooth=False)
        .curve_to((32, -118), (20, -114), (8, -108), smooth=False)
        .line_to(-4, -180)
        .curve_to((14, -186), (30, -190), (46, -190), smooth=False)
    )
    bar = rect_contour(26, 444, 304, 520)
    return union_contours([stem, bar])


def _sans_it_i() -> List[ContourBuilder]:
    stem = (
        ContourBuilder((138, -8))
        .curve_to((176 + _hx(0.4), -8), (204 + _hx(0.8), 12), (222 + _hx(), 40), smooth=False)
        .line_to(204 + _hx(), 96)
        # Review 3: one wide concave curve from the tail into the stem (no notch)
        .curve_to((188 + _hx(0.7), 78), (156, 62), (156, 150), smooth=False)
        .line_to(156, 520)
        .line_to(72, 520)
        .line_to(72, 96)
        .vh_to(138, -8, 0.58, 0.58)
    )
    dot = humanist_oval_contour(114, 660, 50, 50, 0.60, 0.60, clockwise=False)
    return [stem, dot]


def _sans_it_ae() -> List[ContourBuilder]:
    """Humanist single-story 'ae' matching Sans Italic 'a' + Sans 'e' (w=848)."""
    top, bot = 530, -10
    outer = (
        ContourBuilder((236, bot))
        .curve_to((312, bot), (368, 22), (398, 72), smooth=False)
        .line_to(428, 72)
        .curve_to((466, 22), (532, bot), (618, bot), smooth=True)
        .curve_to((714, bot), (782, 26), (820, 88), smooth=False)
        .line_to(760, 144)
        .curve_to((728, 92), (680, 68), (620, 68), smooth=True)
        .curve_to((532, 68), (476, 134), (472, 232), smooth=False)
        .line_to(826, 232)
        .line_to(826, 286)
        .vh_to(614, top, 0.58, 0.58)
        # Review 3: the a has its own straight stem up to the x-height, with an open notch
        # between it and the e. Before, a and e met in a round valley and the glyph read as oe.
        .curve_to((532, top), (476, 470), (472, 372), smooth=False)
        .line_to(472, 520)
        .line_to(396, 520)
        .curve_to((350, 528), (296, top), (236, top), smooth=False)
        .hv_to(48, 260, 0.58, 0.585)
        .vh_to(236, bot, 0.585, 0.58)
    )
    in_a = (
        ContourBuilder((250, 64))
        .hv_to(138, 260, 0.585, 0.59)
        .vh_to(250, 456, 0.59, 0.585)
        .hv_to(378, 336, 0.56, 0.56)
        .line_to(378, 184)
        .vh_to(250, 64, 0.56, 0.56)
    )
    in_e = (
        ContourBuilder((530, 300))      # Review 3: counter moved right with the lower e join
        .curve_to((538, 392), (572, 450), (628, 450), smooth=True)
        .curve_to((700, 450), (740, 392), (744, 300), smooth=False)
    )
    return [outer, in_a, in_e]


# ---------------------------------------------------------------------------
# Admiralty Mono Italic — Fixed 600u Cursive Coding Glyphs
# ---------------------------------------------------------------------------

def _mono_it_a() -> List[ContourBuilder]:
    top, bot = 530, -10
    bowl_out = (
        ContourBuilder((250, bot))
        .curve_to((328, bot), (384, 22), (416, 72), smooth=False)
        .line_to(416, 438)
        .curve_to((382, 498), (324, top), (250, top), smooth=False)
        .hv_to(72, 260, 0.58, 0.585)
        .vh_to(250, bot, 0.585, 0.58)
    )
    bowl_in = (
        ContourBuilder((264, 64))
        .hv_to(158, 260, 0.585, 0.59)
        .vh_to(264, 456, 0.59, 0.585)
        .hv_to(404, 336, 0.56, 0.56)
        .line_to(404, 184)
        .vh_to(264, 64, 0.56, 0.56)
    )
    stem_tail = (
        ContourBuilder((458, -8))
        .curve_to((490 + _hx(0.4), -8), (516 + _hx(0.8), 0), (538 + _hx(), 18), smooth=False)
        .line_to(528 + _hx(), 86)
        # Review 3: one wide concave curve from the tail into the stem (no notch)
        .curve_to((512 + _hx(0.7), 68), (482, 62), (482, 150), smooth=False)
        .line_to(482, 520)
        .line_to(400, 520)
        .line_to(400, 88)
        .vh_to(458, -8, 0.58, 0.58)
    )
    return union_contours([bowl_out, bowl_in, stem_tail])


def _mono_it_f() -> List[ContourBuilder]:
    stem = (
        ContourBuilder((172, -184))
        .curve_to((272, -184), (316, -120), (316, 0), smooth=False)
        .line_to(316, 608)
        .vh_to(378, 672, 0.58, 0.58)
        .curve_to((400, 672), (424, 666), (446, 656), smooth=False)
        .line_to(458, 728)
        .curve_to((428, 742), (398, 748), (368, 748), smooth=False)
        .hv_to(230, 598, 0.58, 0.58)
        .line_to(230, -8)
        .curve_to((230, -90), (206, -112), (172, -112), smooth=False)
        .curve_to((154, -112), (138, -108), (124, -102), smooth=False)
        .line_to(112, -174)
        .curve_to((134, -180), (154, -184), (172, -184), smooth=False)
    )
    bar = rect_contour(120, 444, 444, 520)
    return union_contours([stem, bar])


def _mono_it_ae() -> List[ContourBuilder]:
    """Centered 600u cursive coding 'ae' fitting inside 600u."""
    return _scale_contours(_sans_it_ae(), 0.65, 1.0, 22.0, 0.0)


def _rebuild_derived_italic_upright_frame(
    result: Dict[str, Tuple[int, int | None, List[ContourBuilder]]],
    *,
    weight_class: int,
    is_serif: bool,
    is_mono: bool,
) -> None:
    """Rebuild dotlessi, dotlessj, and cursive composites inside the upright frame before slanting."""
    result["dotlessi"] = (result["dotlessi"][0], result["dotlessi"][1], result["i"][2][:1])
    result["dotlessj"] = (result["dotlessj"][0], result["dotlessj"][1], result["j"][2][:1])
    if is_mono:
        i_c = [c.translated(-136, 0) for c in result["i"][2]]
        j_c = [c.translated(96, 0) for c in result["j"][2]]
        result["ij"] = (MONO_WIDTH, result["ij"][1], i_c + j_c)
    else:
        dx_ij = {400: 244, 500: 252, 700: 264}[weight_class]
        result["ij"] = (result["ij"][0], result["ij"][1], result["i"][2] + [c.translated(dx_ij, 0) for c in result["j"][2]])
    if not is_mono:
        result["napostrophe"] = (
            result["napostrophe"][0],
            result["napostrophe"][1],
            [c.translated(-22, 0) for c in result["quoteright"][2]] + [c.translated(174 if weight_class == 500 else (180 if weight_class >= 700 else 170), 0) for c in result["n"][2]],
        )


def _thick_and_slant_family(
    base_400_upright: Dict[str, Tuple[int, int | None, List[ContourBuilder]]],
    weight_class: int,
    *,
    is_serif: bool,
    is_mono: bool,
    ss01_builder: Callable[[], Dict[str, List[ContourBuilder]]] | None = None,
) -> Dict[str, Tuple[int, int | None, List[ContourBuilder]]]:
    """
    Generate Regular Italic (400), Medium Italic (500), or Bold Italic (700) from the
    400 upright cursive dictionary, preserving contour topology and 1:1 duplex widths.
    """
    if weight_class == 400:
        upright = {k: (w, u, list(cs)) for k, (w, u, cs) in base_400_upright.items()}
    else:
        if is_mono:
            rx, ry = (MONO_BOLD_RX, MONO_BOLD_RY) if weight_class >= 700 else (MONO_MED_RX, MONO_MED_RY)
        elif is_serif:
            rx, ry = (SERIF_BOLD_RX, SERIF_BOLD_RY) if weight_class >= 700 else (SERIF_MED_RX, SERIF_MED_RY)
        else:
            rx, ry = (SANS_BOLD_RX, SANS_BOLD_RY) if weight_class >= 700 else (SANS_MED_RX, SANS_MED_RY)

        # Thicken 400 upright cursive glyphs cleanly to target duplex weight widths
        # Notice cursive Bold rx capped slightly at 17.5 on Serif Italic curved hooks to prevent neck pinch
        eff_rx = min(rx, 17.5) if (is_serif and weight_class >= 700) else rx
        mark_rx, mark_ry = (13.0, 8.5) if weight_class >= 700 else (5.0, 3.5)

        upright: Dict[str, Tuple[int, int | None, List[ContourBuilder]]] = {}
        ss01_map = ss01_builder() if (is_mono and ss01_builder is not None) else {}

        for gn, (orig_w, uni, contours) in base_400_upright.items():
            if is_mono:
                nw = MONO_WIDTH if orig_w > 0 else 0
            elif weight_class >= 700:
                nw = compute_duplex_bold_width(gn, orig_w)
            else:
                nw = compute_duplex_medium_width(gn, orig_w)

            if is_mono and gn in ss01_map:
                upright[gn] = (MONO_WIDTH, None, ss01_map[gn])
            elif gn == ".notdef":
                in_off = 92 if weight_class >= 700 else 86
                upright[gn] = (nw, uni, [rect_contour(64, 0, 536, 700, False), rect_contour(64 + in_off, in_off, 536 - in_off, 700 - in_off, True)])
            elif orig_w == 0:
                upright[gn] = (0, uni, bolden_contours_smooth(contours, 0, 0, mark_rx, mark_ry, is_mark=True))
            elif gn == "euro":
                upright[gn] = (nw, uni, bolden_contours_smooth(contours, orig_w, nw, min(eff_rx, 16.5), ry))
            else:
                upright[gn] = (nw, uni, bolden_contours_smooth(contours, orig_w, nw, eff_rx, ry))

        if weight_class == 500:
            _rebuild_derived_medium(upright, is_serif=is_serif, is_mono=is_mono)
        else:
            from glyphs_bold import _rebuild_derived_bold
            reg_w_map = {k: v[0] for k, v in base_400_upright.items()}
            _rebuild_derived_bold(upright, reg_w_map, is_serif=is_serif, is_mono=is_mono)

    _rebuild_derived_italic_upright_frame(upright, weight_class=weight_class, is_serif=is_serif, is_mono=is_mono)

    # In Mono Italic, guarantee clean separation on multi-contour IJ and fractions under 9.5-deg shear
    if is_mono:
        from glyphs_medium import _mono_med_IJ
        if weight_class == 400:
            upright["IJ"] = (MONO_WIDTH, upright["IJ"][1], [c.translated(-8, 0) for c in upright["IJ"][2]] if False else _mono_med_IJ())
        elif weight_class >= 700:
            upright["IJ"] = (MONO_WIDTH, upright["IJ"][1], _mono_med_IJ())
        for fn, a, b in (("onequarter", "one", "four"), ("onehalf", "one", "two"), ("threequarters", "three", "four")):
            num = _scale_contours(upright[a][2], 0.48, 0.48, 22, 344)
            den = _scale_contours(upright[b][2], 0.48, 0.48, 314, 0)
            slash = ContourBuilder((168, -12)).line_to(242, -12).line_to(468, 704).line_to(394, 704)
            upright[fn] = (MONO_WIDTH, upright[fn][1], num + [slash] + den)

    # Slant every contour through pathops -> Qu2Cu -> cubic extrema split!
    slanted: Dict[str, Tuple[int, int | None, List[ContourBuilder]]] = {}
    for gn, (w, uni, contours) in upright.items():
        if not contours:
            slanted[gn] = (w, uni, [])
        else:
            slanted[gn] = (w, uni, slant_contours_clean(contours, y_piv=ITALIC_PIVOT_Y))
    return slanted


def _build_400_upright_serif_italic() -> Dict[str, Tuple[int, int | None, List[ContourBuilder]]]:
    base = build_all_serif_glyphs(SERIF_REGULAR)
    cur: Dict[str, Tuple[int, int | None, List[ContourBuilder]]] = {k: v for k, v in base.items()}
    overrides: Dict[str, Callable[[], List[ContourBuilder]]] = {
        "a": _serif_it_a,
        "d": _serif_it_d,
        "e": _serif_it_e,
        "f": _serif_it_f,
        "g": _serif_it_g,
        "h": _serif_it_h,
        "i": _serif_it_i,
        "k": _serif_it_k,
        "l": _serif_it_l,
        "m": _serif_it_m,
        "n": _serif_it_n,
        "r": _serif_it_r,
        "u": _serif_it_u,
        "ae": _serif_it_ae,
        "oe": _serif_it_oe,
    }
    for gn, fn in overrides.items():
        w, uni, _ = cur[gn]
        cur[gn] = (w, uni, fn())
    # Rebuild cursive-dependent lslash & dcroat cleanly
    cur["dcroat"] = (cur["dcroat"][0], cur["dcroat"][1], union_contours(cur["d"][2] + [rect_contour(cur["d"][0] - 294, 566, cur["d"][0] - 20, 614)]))
    cur["lslash"] = (cur["lslash"][0], cur["lslash"][1], union_contours([c.translated(12, 0) for c in cur["l"][2]] + [bar_segment_contour((18, 306), (266, 472), 48)]))
    cur["ldot"] = (cur["ldot"][0], cur["ldot"][1], cur["l"][2] + [humanist_oval_contour(308, 286, 46, 46, 0.62, 0.62, clockwise=False)])
    return cur


def _build_400_upright_sans_italic() -> Dict[str, Tuple[int, int | None, List[ContourBuilder]]]:
    base = build_all_sans_glyphs()
    cur: Dict[str, Tuple[int, int | None, List[ContourBuilder]]] = {k: v for k, v in base.items()}
    overrides: Dict[str, Callable[[], List[ContourBuilder]]] = {
        "a": _sans_it_a,
        "f": _sans_it_f,
        "i": _sans_it_i,
        "ae": _sans_it_ae,
    }
    for gn, fn in overrides.items():
        w, uni, _ = cur[gn]
        cur[gn] = (w, uni, fn())
    return cur


def _build_400_upright_mono_italic() -> Dict[str, Tuple[int, int | None, List[ContourBuilder]]]:
    base = build_all_mono_glyphs(MONO_REGULAR)
    cur: Dict[str, Tuple[int, int | None, List[ContourBuilder]]] = {k: v for k, v in base.items()}
    overrides: Dict[str, Callable[[], List[ContourBuilder]]] = {
        "a": _mono_it_a,
        "f": _mono_it_f,
        "ae": _mono_it_ae,
    }
    for gn, fn in overrides.items():
        w, uni, _ = cur[gn]
        cur[gn] = (w, uni, fn())
    return cur


def build_all_sans_italic_glyphs(weight_class: int = 400) -> Dict[str, Tuple[int, int | None, List[ContourBuilder]]]:
    global _HOOK_EXTRA
    _HOOK_EXTRA = dict(zip((400, 500, 700), (0.0, 6.0, 16.0))).get(weight_class, 0.0)
    try:
        base400 = _build_400_upright_sans_italic()
    finally:
        _HOOK_EXTRA = 0.0
    if weight_class == 400:
        return _thick_and_slant_family(base400, 400, is_serif=False, is_mono=False)
    if weight_class == 500:
        from glyphs_medium import build_all_sans_medium_glyphs
        med = build_all_sans_medium_glyphs()
        for gn in ("a", "f", "i", "dotlessi", "ae", "ij"):
            nw, uni, _ = med[gn]
            med[gn] = (nw, uni, bolden_contours_smooth(base400[gn][2], base400[gn][0], nw, SANS_MED_RX, SANS_MED_RY))
        _rebuild_derived_italic_upright_frame(med, weight_class=500, is_serif=False, is_mono=False)
        return {gn: (w, u, slant_contours_clean(cs) if cs else []) for gn, (w, u, cs) in med.items()}
    else:
        from glyphs_bold import build_all_sans_bold_glyphs
        bld = build_all_sans_bold_glyphs()
        for gn in ("a", "f", "i", "dotlessi", "ae", "ij"):
            nw, uni, _ = bld[gn]
            bld[gn] = (nw, uni, bolden_contours_smooth(base400[gn][2], base400[gn][0], nw, 18.0, 11.5))
        _rebuild_derived_italic_upright_frame(bld, weight_class=700, is_serif=False, is_mono=False)
        return {gn: (w, u, slant_contours_clean(cs) if cs else []) for gn, (w, u, cs) in bld.items()}


def build_all_serif_italic_glyphs(weight_class: int = 400) -> Dict[str, Tuple[int, int | None, List[ContourBuilder]]]:
    global _HOOK_EXTRA
    _HOOK_EXTRA = dict(zip((400, 500, 700), (0.0, 8.0, 18.0))).get(weight_class, 0.0)
    try:
        base400 = _build_400_upright_serif_italic()
    finally:
        _HOOK_EXTRA = 0.0
    if weight_class == 400:
        return _thick_and_slant_family(base400, 400, is_serif=True, is_mono=False)
    cursive_keys = ("a", "d", "dcroat", "e", "f", "g", "h", "i", "dotlessi", "k", "l", "lslash", "ldot", "m", "n", "r", "u", "ae", "oe", "ij")
    if weight_class == 500:
        from glyphs_medium import build_all_serif_medium_glyphs
        med = build_all_serif_medium_glyphs()
        for gn in cursive_keys:
            nw, uni, _ = med[gn]
            med[gn] = (nw, uni, bolden_contours_smooth(base400[gn][2], base400[gn][0], nw, SERIF_MED_RX, SERIF_MED_RY))
        med["dcroat"] = (med["dcroat"][0], med["dcroat"][1], union_contours(med["d"][2] + [rect_contour(med["d"][0] - 300, 564, med["d"][0] - 20, 618)]))
        med["lslash"] = (med["lslash"][0], med["lslash"][1], union_contours([c.translated(12, 0) for c in med["l"][2]] + [bar_segment_contour((18, 306), (266, 472), 54)]))
        med["ldot"] = (med["ldot"][0], med["ldot"][1], med["l"][2] + [humanist_oval_contour(316, 286, 48, 48, 0.62, 0.62, clockwise=False)])
        _rebuild_derived_italic_upright_frame(med, weight_class=500, is_serif=True, is_mono=False)
        return {gn: (w, u, slant_contours_clean(cs) if cs else []) for gn, (w, u, cs) in med.items()}
    else:
        from glyphs_bold import build_all_serif_bold_glyphs
        bld = build_all_serif_bold_glyphs()
        for gn in cursive_keys:
            nw, uni, _ = bld[gn]
            bld[gn] = (nw, uni, bolden_contours_smooth(base400[gn][2], base400[gn][0], nw, 17.5, 5.2))
        bld["dcroat"] = (bld["dcroat"][0], bld["dcroat"][1], union_contours(bld["d"][2] + [rect_contour(bld["d"][0] - 310, 560, bld["d"][0] - 20, 622)]))
        bld["lslash"] = (bld["lslash"][0], bld["lslash"][1], union_contours([c.translated(12, 0) for c in bld["l"][2]] + [bar_segment_contour((18, 304), (274, 474), 60)]))
        bld["ldot"] = (bld["ldot"][0], bld["ldot"][1], bld["l"][2] + [humanist_oval_contour(326, 286, 54, 54, 0.62, 0.62, clockwise=False)])
        _rebuild_derived_italic_upright_frame(bld, weight_class=700, is_serif=True, is_mono=False)
        return {gn: (w, u, slant_contours_clean(cs) if cs else []) for gn, (w, u, cs) in bld.items()}


def _prep_mono_it_fractions_and_ij(gmap: Dict[str, Tuple[int, int | None, List[ContourBuilder]]]) -> None:
    from glyphs_medium import _mono_med_IJ
    gmap["IJ"] = (MONO_WIDTH, gmap["IJ"][1], _mono_med_IJ())
    for fn, a, b in (("onequarter", "one", "four"), ("onehalf", "one", "two"), ("threequarters", "three", "four")):
        num = _scale_contours(gmap[a][2], 0.48, 0.48, 22, 344)
        den = _scale_contours(gmap[b][2], 0.48, 0.48, 314, 0)
        slash = ContourBuilder((168, -12)).line_to(242, -12).line_to(468, 704).line_to(394, 704)
        gmap[fn] = (MONO_WIDTH, gmap[fn][1], num + [slash] + den)


def build_all_mono_italic_glyphs(weight_class: int = 400) -> Dict[str, Tuple[int, int | None, List[ContourBuilder]]]:
    global _HOOK_EXTRA
    _HOOK_EXTRA = dict(zip((400, 500, 700), (0.0, 6.0, 14.0))).get(weight_class, 0.0)
    try:
        base400 = _build_400_upright_mono_italic()
    finally:
        _HOOK_EXTRA = 0.0
    if weight_class == 400:
        return _thick_and_slant_family(base400, 400, is_serif=False, is_mono=True)
    if weight_class == 500:
        from glyphs_medium import build_all_mono_medium_glyphs
        med = build_all_mono_medium_glyphs()
        for gn in ("a", "f", "ae"):
            med[gn] = (MONO_WIDTH, med[gn][1], bolden_contours_smooth(base400[gn][2], MONO_WIDTH, MONO_WIDTH, MONO_MED_RX, MONO_MED_RY))
        _prep_mono_it_fractions_and_ij(med)
        return {gn: (w, u, slant_contours_clean(cs) if cs else []) for gn, (w, u, cs) in med.items()}
    else:
        from glyphs_bold import build_all_mono_bold_glyphs
        bld = build_all_mono_bold_glyphs()
        for gn in ("a", "f", "ae"):
            bld[gn] = (MONO_WIDTH, bld[gn][1], bolden_contours_smooth(base400[gn][2], MONO_WIDTH, MONO_WIDTH, 13.5, 8.5))
        _prep_mono_it_fractions_and_ij(bld)
        return {gn: (w, u, slant_contours_clean(cs) if cs else []) for gn, (w, u, cs) in bld.items()}


# ---------------------------------------------------------------------------
# Italic Slanted Anchor Placement, Composites & Kerning
# ---------------------------------------------------------------------------

def _slant_x(ax: float, ay: float) -> int:
    return int(round(ax + SLANT_K * (ay - ITALIC_PIVOT_Y)))


def attach_italic_anchors_and_composites(
    ufo: ufoLib2.Font,
    weight_class: int = 400,
    *,
    is_monospace: bool = False,
) -> None:
    """Attach 9.5-deg slanted anchors and depth-1 flattened composites with propagated anchors."""
    from fontTools.pens.boundsPen import BoundsPen

    mark_anchors_upright = dict(MARK_ANCHORS)
    if weight_class >= 700:
        mark_anchors_upright["dieresiscomb.cap"] = {"_top": (0, 700), "top": (0, 810)}
        mark_anchors_upright["macroncomb.cap"] = {"_top": (0, 700), "top": (0, 814)}
        mark_anchors_upright["acutecomb.cap"] = {"_top": (0, 700), "top": (0, 864)}
        mark_anchors_upright["gravecomb.cap"] = {"_top": (0, 700), "top": (0, 864)}
        mark_anchors_upright["caroncomb.cap"] = {"_top": (0, 700), "top": (0, 864)}
    elif weight_class == 500:
        mark_anchors_upright["dieresiscomb.cap"] = {"_top": (0, 700), "top": (0, 814)}
        mark_anchors_upright["macroncomb.cap"] = {"_top": (0, 700), "top": (0, 814)}
        mark_anchors_upright["acutecomb.cap"] = {"_top": (0, 700), "top": (0, 864)}
        mark_anchors_upright["gravecomb.cap"] = {"_top": (0, 700), "top": (0, 864)}
        mark_anchors_upright["caroncomb.cap"] = {"_top": (0, 700), "top": (0, 864)}

    for mname, adict in mark_anchors_upright.items():
        if mname in ufo:
            ufo[mname].anchors = [
                ufoLib2.objects.Anchor(x=_slant_x(ax, ay), y=ay, name=aname)
                for aname, (ax, ay) in adict.items()
            ]

    reg_widths_all = dict(DUPLEX_ADVANCE_WIDTHS)
    for gn, (rw, _, _) in EXT_CONTOUR_BUILDERS.items():
        reg_widths_all[gn] = rw

    mono_reg_top_x = {
        "L": 116.0, "b": 116.0, "d": 484.0, "h": 116.0, "k": 140.0,
        "l": 300.0, "t": 244.0, "i": 300.0, "dotlessi": 300.0, "j": 342.0, "dotlessj": 342.0,
    }
    mono_reg_ogonek = {
        "A": (512.0, 0.0), "E": (464.0, 0.0), "I": (312.0, 0.0), "U": (494.0, 4.0),
        "a": (456.0, 0.0), "e": (412.0, 12.0), "i": (342.0, 0.0), "dotlessi": (342.0, 0.0), "u": (468.0, 0.0),
    }

    for bname, orig_anchors in BASE_ANCHORS.items():
        if bname not in ufo:
            continue
        g = ufo[bname]
        if is_monospace:
            # Compute upright horizontal center roughly from slanted glyph by un-shearing around y=260
            new_a = []
            for aname, (ox, ay) in orig_anchors.items():
                if aname == "top":
                    ux = mono_reg_top_x.get(bname, 300.0)
                    new_a.append(ufoLib2.objects.Anchor(x=_slant_x(ux, ay), y=ay, name="top"))
                elif aname == "bottom":
                    ux = 300.0 if bname in ("l", "i", "dotlessi") else 300.0
                    new_a.append(ufoLib2.objects.Anchor(x=_slant_x(ux, ay), y=ay, name="bottom"))
                elif aname == "ogonek":
                    ux, oy = mono_reg_ogonek.get(bname, (380.0, ay))
                    new_a.append(ufoLib2.objects.Anchor(x=_slant_x(ux, oy), y=oy, name="ogonek"))
            g.anchors = new_a
        else:
            rw = reg_widths_all.get(bname, g.width)
            sx = g.width / rw if rw > 0 else 1.0
            g.anchors = [
                ufoLib2.objects.Anchor(x=_slant_x(ax * sx, ay), y=ay, name=aname)
                for aname, (ax, ay) in orig_anchors.items()
            ]

    alt_slant_dx = int(round(SLANT_K * (640.0 - ITALIC_PIVOT_Y)))  # ~+64u at apostrophe-caron height
    glyph_order = list(ufo.lib.get("public.glyphOrder", []))
    for comp_name, uni, base_name, mark_name, anchor_name in COMPOSITE_RECIPES:
        base_g = ufo[base_name]
        mark_g = ufo[mark_name]

        if comp_name in ("dcaron", "lcaron", "tcaron", "Lcaron"):
            if is_monospace:
                dx_base = {"dcaron": 546, "lcaron": 404, "tcaron": 374, "Lcaron": 276}[comp_name]
                dy = {"dcaron": 20, "lcaron": 18, "tcaron": 22, "Lcaron": 0}[comp_name]
                w_override = {}
            elif weight_class >= 700:
                dx_base = {"dcaron": 608, "lcaron": 248, "tcaron": 292, "Lcaron": 284}[comp_name]
                dy = {"dcaron": 16, "lcaron": 16, "tcaron": -16, "Lcaron": 0}[comp_name]
                w_override = {"dcaron": 706, "lcaron": 348, "tcaron": 384, "Lcaron": 584}
            elif weight_class == 500:
                dx_base = {"dcaron": 592, "lcaron": 236, "tcaron": 280, "Lcaron": 274}[comp_name]
                dy = {"dcaron": 16, "lcaron": 16, "tcaron": -16, "Lcaron": 0}[comp_name]
                w_override = {"dcaron": 692, "lcaron": 334, "tcaron": 368, "Lcaron": 566}
            else:
                dx_base = {"dcaron": 582, "lcaron": 230, "tcaron": 270, "Lcaron": 266}[comp_name]
                dy = {"dcaron": 16, "lcaron": 16, "tcaron": -16, "Lcaron": 0}[comp_name]
                w_override = {"dcaron": 680, "lcaron": 324, "tcaron": 356, "Lcaron": 556}
            dx = dx_base + alt_slant_dx
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


def apply_italic_class_kerning(ufo: ufoLib2.Font) -> None:
    """Shared class kerning + positive left-paren / bracket clearance for descended italic f."""
    apply_class_kerning(ufo)
    # Review 2: the group is now defined once in spacing_kerning.py (public.kern1.paren_l)
    ufo.kerning[("public.kern1.paren_l", "f")] = 28
