"""
Reusable bracketed literary-humanist serif primitives & stroke parameters for
Admiralty Serif Regular (1000 UPM), engineered to maximize visual distinction
from Admiralty Sans while sitting cleanly inside the exact 1:1 duplex width table.
"""

from __future__ import annotations
from dataclasses import dataclass

from design_system import ContourBuilder, Point, lerp_x


@dataclass(frozen=True)
class SerifWeightParams:
    name: str = "Regular"
    weight_value: int = 400

    # Authentic book-serif contrast (robust on Windows 100% & dark mode)
    lc_stem_v: float = 92.0
    lc_stem_h: float = 48.0
    lc_bowl_v: float = 98.0
    lc_join_thin: float = 46.0

    cap_stem_v: float = 102.0
    cap_stem_h: float = 50.0
    cap_bowl_v: float = 110.0

    fig_stem_v: float = 96.0
    fig_stem_h: float = 50.0
    fig_bowl_v: float = 104.0

    # Crisp, sturdy horizontal serifs with graceful brackets
    lc_serif_h: float = 28.0
    lc_serif_ext: float = 44.0
    lc_bracket: float = 32.0

    cap_serif_h: float = 30.0
    cap_serif_ext: float = 48.0
    cap_bracket: float = 36.0

    outer_tension: float = 0.575
    inner_tension: float = 0.605


SERIF_REGULAR = SerifWeightParams()


def vstem_serifed(
    x0: float,
    x1: float,
    y_bot: float,
    y_top: float,
    *,
    bl: float = 0.0,
    br: float = 0.0,
    tl: float = 0.0,
    tr: float = 0.0,
    tl_flag: bool = False,
    sh: float = 28.0,
    brk: float = 32.0,
) -> ContourBuilder:
    """
    Build a single, clean CCW vertical stem [x0..x1] from y_bot to y_top with
    slender horizontal serifs and graceful curved brackets:
      - bl, br: bottom-left / bottom-right serif outward extension (0 = flush)
      - tl, tr: top-left / top-right horizontal serif outward extension (0 = flush)
      - tl_flag: if True (and tl > 0, tr == 0), draws an expressive sloped
        literary head flag on the top-left (for lowercase b, d, h, i, j, k, l, m, n, p, r, u).
    """
    cb = ContourBuilder((x0 - bl, y_bot))
    cb.line_to(x1 + br, y_bot)
    if br > 0:
        cb.line_to(x1 + br, y_bot + sh)
        cb.curve_to(
            (x1 + br * 0.32, y_bot + sh),
            (x1, y_bot + sh + brk * 0.35),
            (x1, y_bot + sh + brk),
            smooth=False,
        )

    # Right stem wall up to top-right
    if tr > 0:
        cb.line_to(x1, y_top - sh - brk)
        cb.curve_to(
            (x1, y_top - sh - brk * 0.35),
            (x1 + tr * 0.32, y_top - sh),
            (x1 + tr, y_top - sh),
            smooth=False,
        )
        cb.line_to(x1 + tr, y_top)
        cb.line_to(x0 - tl, y_top)
    elif tl_flag and tl > 0:
        # Expressive literary sloped wedge flag: peak at (x1 - 12, y_top + 12)
        cb.line_to(x1, y_top)
        cb.line_to(x1 - 14, y_top + 12)
        cb.line_to(x0 - tl, y_top - 22)
        cb.line_to(x0 - tl, y_top - 46)
        cb.curve_to(
            (x0 - tl * 0.32, y_top - 46),
            (x0, y_top - 46 - brk * 0.35),
            (x0, y_top - 46 - brk),
            smooth=False,
        )
    else:
        cb.line_to(x1, y_top)
        cb.line_to(x0 - tl, y_top)

    # Top-left horizontal serif (when not tl_flag)
    if tl > 0 and not tl_flag:
        cb.line_to(x0 - tl, y_top - sh)
        cb.curve_to(
            (x0 - tl * 0.32, y_top - sh),
            (x0, y_top - sh - brk * 0.35),
            (x0, y_top - sh - brk),
            smooth=False,
        )

    # Left stem wall down to bottom-left
    if bl > 0:
        cb.line_to(x0, y_bot + sh + brk)
        cb.curve_to(
            (x0, y_bot + sh + brk * 0.35),
            (x0 - bl * 0.32, y_bot + sh),
            (x0 - bl, y_bot + sh),
            smooth=False,
        )

    cb.line_to(x0 - bl, y_bot)
    return cb


def foot_pad_ccw(
    x_stem0: float,
    x_stem1: float,
    y_base: float,
    ext_l: float,
    ext_r: float,
    sh: float = 28.0,
    brk: float = 32.0,
) -> ContourBuilder:
    """Standalone CCW foot serif pad to union cleanly onto vertical stems."""
    return vstem_serifed(
        x_stem0, x_stem1, y_base, y_base + sh + brk + 24,
        bl=ext_l, br=ext_r, sh=sh, brk=brk,
    )


def head_pad_ccw(
    x_stem0: float,
    x_stem1: float,
    y_top: float,
    ext_l: float,
    ext_r: float,
    sh: float = 28.0,
    brk: float = 32.0,
) -> ContourBuilder:
    """Standalone CCW head serif pad to union cleanly onto vertical stems."""
    return vstem_serifed(
        x_stem0, x_stem1, y_top - sh - brk - 24, y_top,
        tl=ext_l, tr=ext_r, sh=sh, brk=brk,
    )


def _fillet_to(cb: ContourBuilder, p0: Point, p_corner: Point, p2: Point) -> None:
    """
    Append a G1-tangent bracket curve from p0 through corner p_corner to p2.
    Automatically splits at exact vertical tangent via De Casteljau when x reverses
    direction (obtuse inner diagonal corners) so Bezier extrema error is 0.00u.
    """
    dx1 = p_corner[0] - p0[0]
    dy1 = p_corner[1] - p0[1]
    dx2 = p2[0] - p_corner[0]
    dy2 = p2[1] - p_corner[1]

    if dx1 * dx2 < -1e-6:
        t = abs(dx1) / (abs(dx1) + abs(dx2))
        q01 = (p0[0] + t * dx1, p0[1] + t * dy1)
        q12 = (p_corner[0] + t * dx2, p_corner[1] + t * dy2)
        m = (q01[0] + t * (q12[0] - q01[0]), q01[1] + t * (q12[1] - q01[1]))
        cb.curve_to(
            (p0[0] + (2.0 / 3.0) * (q01[0] - p0[0]), p0[1] + (2.0 / 3.0) * (q01[1] - p0[1])),
            (m[0] + (2.0 / 3.0) * (q01[0] - m[0]), m[1] + (2.0 / 3.0) * (q01[1] - m[1])),
            m,
            smooth=True,
        )
        cb.curve_to(
            (m[0] + (2.0 / 3.0) * (q12[0] - m[0]), m[1] + (2.0 / 3.0) * (q12[1] - m[1])),
            (p2[0] + (2.0 / 3.0) * (q12[0] - p2[0]), p2[1] + (2.0 / 3.0) * (q12[1] - p2[1])),
            p2,
            smooth=False,
        )
    else:
        cb.curve_to(
            (p0[0] + 0.58 * dx1, p0[1] + 0.58 * dy1),
            (p2[0] - 0.58 * dx2, p2[1] - 0.58 * dy2),
            p2,
            smooth=False,
        )


def diag_foot_serif(
    xL_bot: float,
    xR_bot: float,
    y_bot: float,
    xL_far: float,
    xR_far: float,
    y_far: float,
    *,
    ext_l: float = 0.0,
    ext_r: float = 0.0,
    sh: float = 28.0,
    brk: float = 32.0,
) -> ContourBuilder:
    """
    True diagonal-tangent CCW foot serif pad for a slanted stroke whose left wall
    runs (xL_bot, y_bot)->(xL_far, y_far) and right wall runs (xR_bot, y_bot)->(xR_far, y_far).
    """
    y_slab = y_bot + sh
    y_join = y_bot + sh + brk
    y_deep = y_bot + sh + brk + 22.0

    xL_slab = lerp_x(xL_bot, y_bot, xL_far, y_far, y_slab)
    xR_slab = lerp_x(xR_bot, y_bot, xR_far, y_far, y_slab)
    xL_join = lerp_x(xL_bot, y_bot, xL_far, y_far, y_join)
    xR_join = lerp_x(xR_bot, y_bot, xR_far, y_far, y_join)
    xL_deep = lerp_x(xL_bot, y_bot, xL_far, y_far, y_deep)
    xR_deep = lerp_x(xR_bot, y_bot, xR_far, y_far, y_deep)

    x_tip_L = min(xL_bot, xL_join) - ext_l if ext_l > 0 else xL_bot
    x_tip_R = max(xR_bot, xR_join) + ext_r if ext_r > 0 else xR_bot

    cb = ContourBuilder((x_tip_L, y_bot))
    cb.line_to(x_tip_R, y_bot)
    if ext_r > 0:
        cb.line_to(x_tip_R, y_slab)
        _fillet_to(cb, (x_tip_R, y_slab), (xR_slab, y_slab), (xR_join, y_join))
    cb.line_to(xR_deep, y_deep)
    cb.line_to(xL_deep, y_deep)
    if ext_l > 0:
        cb.line_to(xL_join, y_join)
        _fillet_to(cb, (xL_join, y_join), (xL_slab, y_slab), (x_tip_L, y_slab))
        cb.line_to(x_tip_L, y_bot)
    return cb


def diag_head_serif(
    xL_top: float,
    xR_top: float,
    y_top: float,
    xL_far: float,
    xR_far: float,
    y_far: float,
    *,
    ext_l: float = 0.0,
    ext_r: float = 0.0,
    sh: float = 28.0,
    brk: float = 32.0,
) -> ContourBuilder:
    """
    True diagonal-tangent CCW head serif pad for a slanted stroke whose left wall
    runs (xL_top, y_top)->(xL_far, y_far) and right wall runs (xR_top, y_top)->(xR_far, y_far).
    """
    y_slab = y_top - sh
    y_join = y_top - sh - brk
    y_deep = y_top - sh - brk - 22.0

    xL_slab = lerp_x(xL_top, y_top, xL_far, y_far, y_slab)
    xR_slab = lerp_x(xR_top, y_top, xR_far, y_far, y_slab)
    xL_join = lerp_x(xL_top, y_top, xL_far, y_far, y_join)
    xR_join = lerp_x(xR_top, y_top, xR_far, y_far, y_join)
    xL_deep = lerp_x(xL_top, y_top, xL_far, y_far, y_deep)
    xR_deep = lerp_x(xR_top, y_top, xR_far, y_far, y_deep)

    x_tip_L = min(xL_top, xL_join) - ext_l if ext_l > 0 else xL_top
    x_tip_R = max(xR_top, xR_join) + ext_r if ext_r > 0 else xR_top

    cb = ContourBuilder((xL_deep, y_deep))
    cb.line_to(xR_deep, y_deep)
    if ext_r > 0:
        cb.line_to(xR_join, y_join)
        _fillet_to(cb, (xR_join, y_join), (xR_slab, y_slab), (x_tip_R, y_slab))
        cb.line_to(x_tip_R, y_top)
    else:
        cb.line_to(xR_top, y_top)
    cb.line_to(x_tip_L, y_top)
    if ext_l > 0:
        cb.line_to(x_tip_L, y_slab)
        _fillet_to(cb, (x_tip_L, y_slab), (xL_slab, y_slab), (xL_join, y_join))
    return cb
