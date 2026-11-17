"""
Shared design system, Google-Fonts-compliant vertical metrics, duplex advance-width
registry, Unicode mapping, and cubic Bezier / boolean-union helpers for the
Admiralty font family (Sans, Serif, Mono, Symbols).

All coordinates are on a 1000-UPM grid. Sans and Serif share identical advance
widths so switching between them in the Personal Agent UI causes zero text reflow.
"""

from __future__ import annotations
from dataclasses import dataclass
import math
from typing import Dict, List, Sequence, Tuple

from fontTools.misc.bezierTools import splitCubicAtT
import pathops
import ufoLib2

Point = Tuple[float, float]
CubicSeg = Tuple[Point, Point, Point]


@dataclass(frozen=True)
class FamilyMetrics:
    upm: int = 1000
    x_height: int = 520
    cap_height: int = 700
    ascender: int = 740
    descender: int = -220

    # Optical overshoots
    lc_overshoot: int = 10
    cap_overshoot: int = 12

    # Google Fonts Guide compliant vertical metrics:
    # hhea == OS/2 typo == OS/2 win == 130% UPM (980 - (-320) = 1300), LineGap = 0
    typo_ascender: int = 980
    typo_descender: int = -320
    typo_line_gap: int = 0
    win_ascent: int = 980
    win_descent: int = 320
    hhea_ascender: int = 980
    hhea_descender: int = -320
    hhea_line_gap: int = 0

    # Case-sensitive punctuation vertical shift:
    # Centers x-height-aligned punctuation (~260u center) onto Cap Height (~350u center) -> +82u
    case_shift_y: int = 82


@dataclass(frozen=True)
class SansWeightParams:
    """Stroke & tension parameters for an interpolatable Admiralty Sans master."""

    name: str = "Regular"
    weight_value: int = 400

    # Lowercase stroke weights
    lc_stem_v: float = 86.0
    lc_stem_h: float = 74.0
    lc_bowl_v: float = 90.0
    lc_join_thin: float = 58.0

    # Capital & Numeral stroke weights
    cap_stem_v: float = 92.0
    cap_stem_h: float = 78.0
    cap_bowl_v: float = 96.0
    fig_stem_v: float = 88.0
    fig_stem_h: float = 76.0
    fig_bowl_v: float = 92.0

    # Humanist curve tensions
    outer_tension: float = 0.585
    inner_tension: float = 0.605


METRICS = FamilyMetrics()
SANS_REGULAR = SansWeightParams()

TABULAR_FIG_WIDTH = 580

# Duplexed advance widths shared 1:1 between Admiralty Sans and Admiralty Serif.
DUPLEX_ADVANCE_WIDTHS: Dict[str, int] = {
    ".notdef": 600,
    "space": 260,
    # Uppercase A-Z
    "A": 636,
    "B": 618,
    "C": 632,
    "D": 668,
    "E": 576,
    "F": 546,
    "G": 668,
    "H": 680,
    "I": 308,
    "J": 496,
    "K": 628,
    "L": 544,
    "M": 816,
    "N": 692,
    "O": 684,
    "P": 596,
    "Q": 684,
    "R": 612,
    "S": 568,
    "T": 584,
    "U": 672,
    "V": 612,
    "W": 884,
    "X": 604,
    "Y": 584,
    "Z": 576,
    # Lowercase a-z
    "a": 548,
    "b": 576,
    "c": 502,
    "d": 576,
    "e": 552,
    "f": 348,
    "g": 572,
    "h": 584,
    "i": 246,
    "j": 256,
    "k": 528,
    "l": 256,
    "m": 880,
    "n": 584,
    "o": 580,
    "p": 576,
    "q": 576,
    "r": 368,
    "s": 468,
    "t": 354,
    "u": 576,
    "v": 504,
    "w": 756,
    "x": 500,
    "y": 496,
    "z": 472,
    # Proportional lining numerals (default)
    "zero": 564,
    "one": 436,
    "two": 548,
    "three": 548,
    "four": 568,
    "five": 548,
    "six": 560,
    "seven": 528,
    "eight": 564,
    "nine": 560,
    # Tabular lining numerals (.tnum) & slashed zero variants
    "zero.tnum": TABULAR_FIG_WIDTH,
    "one.tnum": TABULAR_FIG_WIDTH,
    "two.tnum": TABULAR_FIG_WIDTH,
    "three.tnum": TABULAR_FIG_WIDTH,
    "four.tnum": TABULAR_FIG_WIDTH,
    "five.tnum": TABULAR_FIG_WIDTH,
    "six.tnum": TABULAR_FIG_WIDTH,
    "seven.tnum": TABULAR_FIG_WIDTH,
    "eight.tnum": TABULAR_FIG_WIDTH,
    "nine.tnum": TABULAR_FIG_WIDTH,
    "zero.slash": 564,
    "zero.tnum.slash": TABULAR_FIG_WIDTH,
    # Basic Latin ASCII punctuation & symbols
    "period": 248,
    "comma": 248,
    "colon": 256,
    "semicolon": 256,
    "exclam": 276,
    "question": 476,
    "quotesingle": 228,
    "quotedbl": 384,
    "grave": 300,
    "asciicircum": 500,
    "asciitilde": 560,
    "hyphen": 360,
    "underscore": 520,
    "parenleft": 336,
    "parenright": 336,
    "bracketleft": 336,
    "bracketright": 336,
    "braceleft": 368,
    "braceright": 368,
    "slash": 388,
    "backslash": 388,
    "bar": 280,
    "asterisk": 420,
    "plus": 580,
    "equal": 580,
    "less": 580,
    "greater": 580,
    "numbersign": 580,
    "percent": 780,
    "ampersand": 664,
    "at": 840,
    "dollar": 580,
    # Extended typographic punctuation & currencies
    "endash": 560,
    "emdash": 920,
    "quoteleft": 244,
    "quoteright": 244,
    "quotedblleft": 424,
    "quotedblright": 424,
    "ellipsis": 720,
    "bullet": 360,
    "periodcentered": 260,
    "degree": 380,
    "euro": 580,
    "sterling": 580,
    "yen": 580,
    "cent": 520,
    # Case-sensitive punctuation variants (.case)
    "hyphen.case": 360,
    "endash.case": 560,
    "emdash.case": 920,
    "parenleft.case": 336,
    "parenright.case": 336,
    "bracketleft.case": 336,
    "bracketright.case": 336,
    "braceleft.case": 368,
    "braceright.case": 368,
    "colon.case": 256,
    "periodcentered.case": 260,
}

UNICODE_MAP: Dict[str, int] = {
    "space": 0x0020,
    "exclam": 0x0021,
    "quotedbl": 0x0022,
    "numbersign": 0x0023,
    "dollar": 0x0024,
    "percent": 0x0025,
    "ampersand": 0x0026,
    "quotesingle": 0x0027,
    "parenleft": 0x0028,
    "parenright": 0x0029,
    "asterisk": 0x002A,
    "plus": 0x002B,
    "comma": 0x002C,
    "hyphen": 0x002D,
    "period": 0x002E,
    "slash": 0x002F,
    "zero": 0x0030,
    "one": 0x0031,
    "two": 0x0032,
    "three": 0x0033,
    "four": 0x0034,
    "five": 0x0035,
    "six": 0x0036,
    "seven": 0x0037,
    "eight": 0x0038,
    "nine": 0x0039,
    "colon": 0x003A,
    "semicolon": 0x003B,
    "less": 0x003C,
    "equal": 0x003D,
    "greater": 0x003E,
    "question": 0x003F,
    "at": 0x0040,
    **{chr(c): c for c in range(0x0041, 0x005B)},  # A-Z
    "bracketleft": 0x005B,
    "backslash": 0x005C,
    "bracketright": 0x005D,
    "asciicircum": 0x005E,
    "underscore": 0x005F,
    "grave": 0x0060,
    **{chr(c): c for c in range(0x0061, 0x007B)},  # a-z
    "braceleft": 0x007B,
    "bar": 0x007C,
    "braceright": 0x007D,
    "asciitilde": 0x007E,
    # Extended punctuation & currencies
    "cent": 0x00A2,
    "sterling": 0x00A3,
    "yen": 0x00A5,
    "degree": 0x00B0,
    "periodcentered": 0x00B7,
    "endash": 0x2013,
    "emdash": 0x2014,
    "quoteleft": 0x2018,
    "quoteright": 0x2019,
    "quotedblleft": 0x201C,
    "quotedblright": 0x201D,
    "bullet": 0x2022,
    "ellipsis": 0x2026,
    "euro": 0x20AC,
}

# Initial Milestone 2 optical kerning pairs (Milestone 3 performs full class-based kerning pass)
DUPLEX_KERNING: Dict[Tuple[str, str], int] = {
    # A pairs
    ("A", "C"): -20, ("A", "G"): -20, ("A", "O"): -22, ("A", "Q"): -22,
    ("A", "T"): -56, ("A", "U"): -18, ("A", "V"): -52, ("A", "W"): -44, ("A", "Y"): -60,
    ("A", "d"): -18, ("A", "e"): -18, ("A", "g"): -16, ("A", "o"): -20,
    ("A", "t"): -24, ("A", "u"): -14, ("A", "v"): -36, ("A", "w"): -30, ("A", "y"): -38,
    ("A", "quoteright"): -54, ("A", "quotedblright"): -54,
    # F / P / T / V / W / Y pairs
    ("F", "A"): -46, ("F", "a"): -28, ("F", "e"): -28, ("F", "o"): -30,
    ("F", "period"): -64, ("F", "comma"): -64,
    ("L", "T"): -56, ("L", "V"): -52, ("L", "W"): -42, ("L", "Y"): -60,
    ("L", "quoteright"): -56, ("L", "quotedblright"): -56,
    ("P", "A"): -52, ("P", "a"): -20, ("P", "e"): -22, ("P", "o"): -24,
    ("P", "period"): -76, ("P", "comma"): -76,
    ("R", "a"): -12, ("R", "d"): -14, ("R", "e"): -16, ("R", "o"): -18, ("R", "y"): -22,
    ("T", "A"): -56, ("T", "O"): -18, ("T", "a"): -46, ("T", "c"): -46,
    ("T", "d"): -44, ("T", "e"): -46, ("T", "g"): -42, ("T", "o"): -48,
    ("T", "r"): -36, ("T", "s"): -42, ("T", "u"): -36, ("T", "w"): -36, ("T", "y"): -38,
    ("T", "period"): -56, ("T", "comma"): -56, ("T", "colon"): -36, ("T", "hyphen"): -42,
    ("V", "A"): -52, ("V", "O"): -18, ("V", "a"): -42, ("V", "e"): -42, ("V", "o"): -44,
    ("V", "period"): -64, ("V", "comma"): -64,
    ("W", "A"): -44, ("W", "a"): -32, ("W", "e"): -32, ("W", "o"): -34,
    ("W", "period"): -52, ("W", "comma"): -52,
    ("Y", "A"): -60, ("Y", "O"): -20, ("Y", "a"): -50, ("Y", "d"): -48,
    ("Y", "e"): -50, ("Y", "o"): -52, ("Y", "p"): -42, ("Y", "u"): -40,
    ("Y", "period"): -68, ("Y", "comma"): -68,
    ("O", "A"): -20, ("O", "T"): -18, ("O", "V"): -18, ("O", "Y"): -20,
    ("K", "O"): -24, ("K", "e"): -20, ("K", "o"): -22, ("K", "u"): -16,
    # Lowercase pairs
    ("f", "a"): -12, ("f", "e"): -12, ("f", "o"): -14, ("f", "period"): -24, ("f", "comma"): -24,
    ("f", "quoteright"): 24, ("f", "quotedblright"): 24, ("f", "parenright"): 20,
    ("r", "a"): -12, ("r", "c"): -14, ("r", "d"): -14, ("r", "e"): -14,
    ("r", "g"): -12, ("r", "o"): -16, ("r", "q"): -14,
    ("r", "period"): -44, ("r", "comma"): -44,
    ("t", "y"): -12,
    ("v", "a"): -16, ("v", "e"): -16, ("v", "o"): -18, ("v", "period"): -44, ("v", "comma"): -44,
    ("w", "a"): -14, ("w", "e"): -14, ("w", "o"): -16, ("w", "period"): -38, ("w", "comma"): -38,
    ("y", "a"): -14, ("y", "d"): -14, ("y", "e"): -16, ("y", "o"): -18,
    ("y", "period"): -48, ("y", "comma"): -48,
}


def rpt(x: float, y: float) -> Point:
    """Round coordinates cleanly to 0.5u precision."""
    rx = round(x * 2.0) / 2.0
    ry = round(y * 2.0) / 2.0
    return (int(rx) if rx.is_integer() else rx, int(ry) if ry.is_integer() else ry)


def lerp_x(x0: float, y0: float, x1: float, y1: float, y: float) -> float:
    return x0 + (x1 - x0) * ((y - y0) / (y1 - y0))


def hv_quadrant(p0: Point, p1: Point, t0: float = 0.585, t1: float = 0.585) -> CubicSeg:
    x0, y0 = p0
    x1, y1 = p1
    c1 = rpt(x0 + t0 * (x1 - x0), y0)
    c2 = rpt(x1, y1 - t1 * (y1 - y0))
    return (c1, c2, rpt(x1, y1))


def vh_quadrant(p0: Point, p1: Point, t0: float = 0.585, t1: float = 0.585) -> CubicSeg:
    x0, y0 = p0
    x1, y1 = p1
    c1 = rpt(x0, y0 + t0 * (y1 - y0))
    c2 = rpt(x1 - t1 * (x1 - x0), y1)
    return (c1, c2, rpt(x1, y1))


def _interior_cubic_extrema_ts(p0: Point, p1: Point, p2: Point, p3: Point) -> List[float]:
    """Find interior t in (0.015, 0.985) where cubic Bezier has a true x or y extremum."""
    ts: List[float] = []
    for axis in (0, 1):
        v0, v1, v2, v3 = p0[axis], p1[axis], p2[axis], p3[axis]
        lo, hi = min(v0, v3), max(v0, v3)
        # Derivative of cubic: 3*a*t^2 + 2*b*t + c = 0
        a = -v0 + 3.0 * v1 - 3.0 * v2 + v3
        b = 2.0 * (v0 - 2.0 * v1 + v2)
        c = v1 - v0
        cand: List[float] = []
        if abs(a) < 1e-7:
            if abs(b) > 1e-7:
                cand.append(-c / b)
        else:
            disc = b * b - 4.0 * a * c
            if disc >= 0.0:
                sq = math.sqrt(disc)
                cand.append((-b + sq) / (2.0 * a))
                cand.append((-b - sq) / (2.0 * a))
        for t in cand:
            if 0.015 < t < 0.985:
                mt = 1.0 - t
                val = (
                    mt * mt * mt * v0
                    + 3.0 * mt * mt * t * v1
                    + 3.0 * mt * t * t * v2
                    + t * t * t * v3
                )
                # Split if extremum bulges > 0.35u outside segment endpoint interval
                # OR if curve reverses direction mid-segment
                if val < lo - 0.35 or val > hi + 0.35:
                    ts.append(t)
    # Deduplicate close t values
    ts.sort()
    dedup: List[float] = []
    for t in ts:
        if not dedup or abs(t - dedup[-1]) > 0.02:
            dedup.append(t)
    return dedup


class ContourBuilder:
    """Helper to construct UFO contours with automatic extremum-splitting support."""

    def __init__(self, start: Point):
        self.start: Point = rpt(*start)
        self.ops: List[tuple] = []
        self.curr: Point = self.start

    def line_to(self, x: float, y: float) -> "ContourBuilder":
        pt = rpt(x, y)
        if pt != self.curr:
            self.ops.append(("line", pt))
            self.curr = pt
        return self

    def curve_to(
        self, c1: Point, c2: Point, end: Point, smooth: bool = True
    ) -> "ContourBuilder":
        p0 = self.curr
        p1, p2, p3 = rpt(*c1), rpt(*c2), rpt(*end)
        ext_ts = _interior_cubic_extrema_ts(p0, p1, p2, p3)
        if ext_ts:
            pieces = splitCubicAtT(p0, p1, p2, p3, *ext_ts)
            for idx, seg in enumerate(pieces):
                _, sc1, sc2, send = seg
                is_last = idx == len(pieces) - 1
                self.ops.append(
                    ("curve", rpt(*sc1), rpt(*sc2), rpt(*send), True if not is_last else smooth)
                )
            self.curr = rpt(*pieces[-1][3])
        else:
            self.ops.append(("curve", p1, p2, p3, smooth))
            self.curr = p3
        return self

    def hv_to(
        self, x: float, y: float, t0: float = 0.585, t1: float = 0.585, smooth: bool = True
    ) -> "ContourBuilder":
        c1, c2, end = hv_quadrant(self.curr, (x, y), t0, t1)
        return self.curve_to(c1, c2, end, smooth=smooth)

    def vh_to(
        self, x: float, y: float, t0: float = 0.585, t1: float = 0.585, smooth: bool = True
    ) -> "ContourBuilder":
        c1, c2, end = vh_quadrant(self.curr, (x, y), t0, t1)
        return self.curve_to(c1, c2, end, smooth=smooth)

    def translated(self, dx: float, dy: float) -> "ContourBuilder":
        nc = ContourBuilder((self.start[0] + dx, self.start[1] + dy))
        for op in self.ops:
            if op[0] == "line":
                nc.line_to(op[1][0] + dx, op[1][1] + dy)
            elif op[0] == "curve":
                c1, c2, end, sm = op[1], op[2], op[3], op[4]
                nc.ops.append(
                    (
                        "curve",
                        rpt(c1[0] + dx, c1[1] + dy),
                        rpt(c2[0] + dx, c2[1] + dy),
                        rpt(end[0] + dx, end[1] + dy),
                        sm,
                    )
                )
                nc.curr = nc.ops[-1][3]
        return nc

    def draw_to_pen(self, pen) -> None:
        pen.moveTo(self.start)
        for op in self.ops:
            if op[0] == "line":
                if op[1] == self.start and op is self.ops[-1]:
                    continue
                pen.lineTo(op[1])
            elif op[0] == "curve":
                pen.curveTo(op[1], op[2], op[3])
        pen.closePath()


def clean_contour_nicks(cb: "ContourBuilder") -> "ContourBuilder":
    """Review 3: last clean-up before a contour is written to the font.
      1. segments of 2.5 units or less are removed (rounding slivers left by boolean operations);
      2. spurs are removed: a vertex where the outline turns back on itself (inside angle
         of 16 degrees or less) made of two short edges.
    Everything else is returned unchanged."""
    segs = []
    cur = cb.start
    for op in cb.ops:
        if op[0] == "line":
            if op[1] != cur:
                segs.append(["line", cur, None, None, op[1]])
                cur = op[1]
        else:
            segs.append(["curve", cur, op[1], op[2], op[3]])
            cur = op[3]
    if cur != cb.start:
        segs.append(["line", cur, None, None, cb.start])
    if len(segs) < 4:
        return cb

    def _chord(sg):
        return math.hypot(sg[4][0] - sg[1][0], sg[4][1] - sg[1][1])

    def _t_in(sg):
        a = sg[3] if sg[0] == "curve" and sg[3] != sg[4] else (sg[2] if sg[0] == "curve" and sg[2] != sg[4] else sg[1])
        return (sg[4][0] - a[0], sg[4][1] - a[1])

    def _t_out(sg):
        b = sg[2] if sg[0] == "curve" and sg[2] != sg[1] else (sg[3] if sg[0] == "curve" and sg[3] != sg[1] else sg[4])
        return (b[0] - sg[1][0], b[1] - sg[1][1])

    changed = False
    for _ in range(6):
        again = False
        n = len(segs)
        if n < 4:
            break
        for i in range(n):
            sg = segs[i]
            if _chord(sg) <= 2.5:
                prev, nxt = segs[i - 1], segs[(i + 1) % n]
                def _axis_line(q):
                    return q[0] == "line" and (q[1][0] == q[4][0] or q[1][1] == q[4][1])
                if _axis_line(prev):        # keep an upright or level neighbour exactly as it is
                    mid = sg[1]
                elif _axis_line(nxt):
                    mid = sg[4]
                else:
                    mid = ((sg[1][0] + sg[4][0]) / 2.0, (sg[1][1] + sg[4][1]) / 2.0)
                if prev[0] == "curve":
                    prev[3] = (prev[3][0] + mid[0] - prev[4][0], prev[3][1] + mid[1] - prev[4][1])
                if nxt[0] == "curve":
                    nxt[2] = (nxt[2][0] + mid[0] - nxt[1][0], nxt[2][1] + mid[1] - nxt[1][1])
                prev[4] = mid
                nxt[1] = mid
                del segs[i]
                again = changed = True
                break
            nxt = segs[(i + 1) % n]
            t1, t2 = _t_in(sg), _t_out(nxt)
            l1, l2 = math.hypot(*t1), math.hypot(*t2)
            if l1 < 1e-6 or l2 < 1e-6:
                continue
            turn = abs(math.degrees(math.atan2(t1[0] * t2[1] - t1[1] * t2[0], t1[0] * t2[0] + t1[1] * t2[1])))
            if turn >= 150.0 and _chord(nxt) < 26.0 and _chord(sg) >= 26.0:
                # short hook-back after a long segment: the long one takes over its end point
                d = (nxt[4][0] - sg[4][0], nxt[4][1] - sg[4][1])
                if sg[0] == "curve":
                    sg[3] = (sg[3][0] + d[0], sg[3][1] + d[1])
                sg[4] = nxt[4]
                del segs[(i + 1) % n]
                again = changed = True
                break
            if turn >= 150.0 and _chord(sg) < 26.0 and _chord(nxt) >= 26.0:
                d = (sg[1][0] - nxt[1][0], sg[1][1] - nxt[1][1])
                if nxt[0] == "curve":
                    nxt[2] = (nxt[2][0] + d[0], nxt[2][1] + d[1])
                nxt[1] = sg[1]
                del segs[i]
                again = changed = True
                break
            if turn >= 164.0 and _chord(sg) < 70.0 and _chord(nxt) < 70.0:
                merged = ["line", sg[1], None, None, nxt[4]]
                j = (i + 1) % n
                segs[i] = merged
                del segs[j]
                again = changed = True
                break
        if not again:
            break
    if not changed:
        return cb
    out = ContourBuilder(segs[0][1])
    for sg in segs:
        if sg[0] == "line":
            out.line_to(*sg[4])
        else:
            out.curve_to(sg[2], sg[3], sg[4], smooth=False)
    return out


def rect_contour(
    x0: float, y0: float, x1: float, y1: float, clockwise: bool = False
) -> ContourBuilder:
    if not clockwise:
        return ContourBuilder((x0, y0)).line_to(x1, y0).line_to(x1, y1).line_to(x0, y1)
    return ContourBuilder((x0, y0)).line_to(x0, y1).line_to(x1, y1).line_to(x1, y0)


def bar_segment_contour(p0: Point, p1: Point, thickness: float) -> ContourBuilder:
    """CCW rectangular bar centered along segment p0 -> p1 with exact perpendicular thickness."""
    dx = p1[0] - p0[0]
    dy = p1[1] - p0[1]
    length = math.hypot(dx, dy)
    nx = -dy / length * (thickness / 2.0)
    ny = dx / length * (thickness / 2.0)
    # p0-n -> p1-n -> p1+n -> p0+n is CCW!
    return (
        ContourBuilder((p0[0] - nx, p0[1] - ny))
        .line_to(p1[0] - nx, p1[1] - ny)
        .line_to(p1[0] + nx, p1[1] + ny)
        .line_to(p0[0] + nx, p0[1] + ny)
    )


def humanist_oval_contour(
    cx: float,
    cy: float,
    rx: float,
    ry: float,
    t_h: float = 0.585,
    t_v: float = 0.585,
    clockwise: bool = False,
) -> ContourBuilder:
    if not clockwise:
        cb = ContourBuilder((cx, cy - ry))
        cb.hv_to(cx + rx, cy, t_h, t_v)
        cb.vh_to(cx, cy + ry, t_v, t_h)
        cb.hv_to(cx - rx, cy, t_h, t_v)
        cb.vh_to(cx, cy - ry, t_v, t_h)
        return cb
    else:
        cb = ContourBuilder((cx, cy - ry))
        cb.hv_to(cx - rx, cy, t_h, t_v)
        cb.vh_to(cx, cy + ry, t_v, t_h)
        cb.hv_to(cx + rx, cy, t_h, t_v)
        cb.vh_to(cx, cy - ry, t_v, t_h)
        return cb


def union_contours(contours: Sequence[ContourBuilder]) -> List[ContourBuilder]:
    """
    Boolean-union ContourBuilders into clean, non-overlapping, extremum-aligned
    ContourBuilders with PostScript winding (CCW outer, CW inner counters).
    If contours contain inner CW counters (e.g. rings of 0 or O), group each
    base shape first or pass separate positive shapes to union cleanly.
    """
    if not contours:
        return []

    # Separate positive (CCW) and negative (CW counter) contours:
    # First build base path from all contours up to any positive overlay strokes,
    # or union each positive component after combining base outer+inner rings.
    from fontTools.pens.areaPen import AreaPen

    signed_paths: List[tuple[float, pathops.Path]] = []
    for cb in contours:
        tg = ufoLib2.objects.Glyph()
        cb.draw_to_pen(tg.getPen())
        ap = AreaPen( None )
        tg.draw(ap)
        sp = pathops.Path()
        tg.draw(sp.getPen())
        signed_paths.append((ap.value, sp))

    # Accumulate sequentially: negative area contours subtract (counter holes of
    # the preceding outer contour), positive area contours boolean-UNION!
    acc = pathops.Path()
    for area, sp in signed_paths:
        if len(acc) == 0:
            acc = pathops.simplify(sp, fix_winding=True)
        elif area < 0:
            # Counter hole belonging to current shape: subtract inner from acc
            hole = pathops.simplify(sp, fix_winding=True)
            acc = pathops.op(acc, hole, pathops.PathOp.DIFFERENCE, fix_winding=True)
        else:
            pos = pathops.simplify(sp, fix_winding=True)
            acc = pathops.op(acc, pos, pathops.PathOp.UNION, fix_winding=True)

    simplified = pathops.simplify(acc, fix_winding=True)

    # Convert simplified path (which may contain Skia qCurveTo quadratics) into
    # pure cubic Beziers via Qu2CuPen so ContourBuilder never misaligns point counts!
    from fontTools.pens.qu2cuPen import Qu2CuPen

    out_glyph = ufoLib2.objects.Glyph()
    q2c_pen = Qu2CuPen(out_glyph.getPen(), max_err=0.5, all_cubic=True)
    simplified.draw(q2c_pen)

    result: List[ContourBuilder] = []
    for ufo_contour in out_glyph.contours:
        pts = list(ufo_contour.points)
        if not pts:
            continue
        # Rotate so pts[0] is an on-curve point
        on_idx = next((i for i, pt in enumerate(pts) if pt.type is not None), 0)
        pts = pts[on_idx:] + pts[:on_idx]
        cb = ContourBuilder((pts[0].x, pts[0].y))
        i = 1
        n = len(pts)
        while i <= n:
            pt = pts[i % n]
            if pt.type == "line":
                cb.line_to(pt.x, pt.y)
                i += 1
            elif pt.type is None:
                c1 = (pt.x, pt.y)
                c2_pt = pts[(i + 1) % n]
                end_pt = pts[(i + 2) % n]
                cb.curve_to(c1, (c2_pt.x, c2_pt.y), (end_pt.x, end_pt.y))
                i += 3
            else:
                cb.line_to(pt.x, pt.y)
                i += 1
        result.append(cb)
    return result
