"""
Admiralty Sans, Serif and Mono — Google Fonts "Latin Plus" additions (75 characters).

Every style is extended from its own glyphs, after the style is built, so each new
character has that style's weight, slant and proportions:
  * superscripts and subscripts 4-9 use the same scale as the existing ² and ³;
  * ⅓ and ⅔ use the layout of the existing ½;
  * currency signs are the base letter plus bars sized from the style's stems;
  * ↖ ↙ ↕ are the existing arrows turned; ∂ is a mirrored 6;
  * geometric shapes, ∏ ∑ ∫ ℓ and ⟨ ⟩ are drawn from simple geometry.
Sans and Serif get the same advance widths (the duplex rule), Mono gets 600 everywhere.
"""

from __future__ import annotations
import math
from typing import Callable, Dict, List, Optional, Tuple

import pathops

from design_system import ContourBuilder
from glyphs_box import _to_contours

SLANT_K = math.tan(math.radians(9.5))
CAP, XH = 700.0, 520.0

STEM = {"sans": {400: 86, 500: 105, 700: 134}, "serif": {400: 92, 500: 110, 700: 141}, "mono": {400: 86, 500: 98, 700: 116}}
HBAR = {"sans": 0.88, "serif": 0.68, "mono": 0.86}

Glyph = Tuple[int, Optional[int], List[ContourBuilder]]


# ---------------------------------------------------------------------------
# geometry helpers (pathops paths)
# ---------------------------------------------------------------------------

def _path(cbs: List[ContourBuilder]) -> pathops.Path:
    p = pathops.Path()
    pen = p.getPen()
    for cb in cbs:
        cb.draw_to_pen(pen)
    return p


def _clean(p: pathops.Path) -> pathops.Path:
    return pathops.simplify(p, fix_winding=True)


def _union(paths: List[pathops.Path]) -> pathops.Path:
    acc = pathops.Path()
    for q in paths:
        acc.addPath(q)
    return _clean(acc)


def _minus(a: pathops.Path, b: pathops.Path) -> pathops.Path:
    return pathops.op(a, b, pathops.PathOp.DIFFERENCE)


def _xf(p: pathops.Path, a=1.0, b=0.0, c=0.0, d=1.0, e=0.0, f=0.0) -> pathops.Path:
    return p.transform(a, b, c, d, e, f)


def _poly(pts) -> pathops.Path:
    p = pathops.Path()
    p.moveTo(*pts[0])
    for q in pts[1:]:
        p.lineTo(*q)
    p.close()
    return _clean(p)


def _rect(x0, y0, x1, y1) -> pathops.Path:
    return _poly([(x0, y0), (x1, y0), (x1, y1), (x0, y1)])


def _ellipse(cx, cy, rx, ry) -> pathops.Path:
    k = 0.5523
    p = pathops.Path()
    p.moveTo(cx + rx, cy)
    p.cubicTo(cx + rx, cy + ry * k, cx + rx * k, cy + ry, cx, cy + ry)
    p.cubicTo(cx - rx * k, cy + ry, cx - rx, cy + ry * k, cx - rx, cy)
    p.cubicTo(cx - rx, cy - ry * k, cx - rx * k, cy - ry, cx, cy - ry)
    p.cubicTo(cx + rx * k, cy - ry, cx + rx, cy - ry * k, cx + rx, cy)
    p.close()
    return p


def _ring(cx, cy, r, w) -> pathops.Path:
    return _minus(_ellipse(cx, cy, r, r), _ellipse(cx, cy, r - w, r - w))


def _stroke(build: Callable[[pathops.Path], None], w: float, cap=pathops.LineCap.ROUND_CAP,
            join=pathops.LineJoin.ROUND_JOIN) -> pathops.Path:
    p = pathops.Path()
    build(p)
    p.stroke(w, cap, join, 4.0)
    p.convertConicsToQuads()
    return _clean(p)


def _outline(shape: pathops.Path, w: float) -> pathops.Path:
    """Outline of a filled shape, drawn inside it (the outer size stays the same)."""
    p = pathops.Path()
    p.addPath(shape)
    p.stroke(w * 2.0, pathops.LineCap.BUTT_CAP, pathops.LineJoin.MITER_JOIN, 10.0)
    p.convertConicsToQuads()
    inner = pathops.op(shape, _clean(p), pathops.PathOp.DIFFERENCE)
    return _minus(shape, inner)


def _bounds(p: pathops.Path) -> Tuple[float, float, float, float]:
    return p.bounds


def _shear(p: pathops.Path, k: float, y0: float) -> pathops.Path:
    return _xf(p, 1.0, 0.0, k, 1.0, -k * y0, 0.0) if k else p


# ---------------------------------------------------------------------------
# builder
# ---------------------------------------------------------------------------

class _Style:
    def __init__(self, data: Dict[str, Glyph], family: str, weight: int, italic: bool):
        self.data, self.family, self.weight, self.italic = data, family, weight, italic
        self.k = SLANT_K if italic else 0.0
        self.stem = float(STEM[family][weight])
        self.hb = self.stem * HBAR[family]          # horizontal bar thickness
        self.mono = family == "mono"

    def has(self, *names: str) -> bool:
        return all(n in self.data and self.data[n][2] for n in names)

    def p(self, name: str) -> pathops.Path:
        return _path(self.data[name][2])

    def w(self, name: str) -> int:
        return int(self.data[name][0])

    # bars that follow the italic slant -----------------------------------
    def vbar(self, xc_mid: float, y0: float, y1: float, w: float, ymid: float) -> pathops.Path:
        k = self.k
        xa, xb = xc_mid + k * (y0 - ymid), xc_mid + k * (y1 - ymid)
        return _poly([(xa - w / 2, y0), (xa + w / 2, y0), (xb + w / 2, y1), (xb - w / 2, y1)])

    def hbar(self, x0_mid: float, x1_mid: float, y0: float, y1: float, ymid: float) -> pathops.Path:
        k = self.k
        return _poly([(x0_mid + k * (y0 - ymid), y0), (x1_mid + k * (y0 - ymid), y0),
                      (x1_mid + k * (y1 - ymid), y1), (x0_mid + k * (y1 - ymid), y1)])

    def edges(self, b, y: float) -> Tuple[float, float]:
        """Left and right ink edge of a (slanted) letter at height y, from its bounds."""
        return b[0] + self.k * (y - b[1]), b[2] - self.k * (b[3] - y)

    def bar_at(self, b, y: float, h: float, ext_l: float, ext_r: float) -> pathops.Path:
        xl, xr = self.edges(b, y)
        return self.hbar(xl - ext_l, xr + ext_r, y - h / 2, y + h / 2, y)

    def slant(self, p: pathops.Path, y0: float = 350.0) -> pathops.Path:
        return _shear(p, self.k, y0)

    def unslant(self, p: pathops.Path, y0: float) -> pathops.Path:
        return _shear(p, -self.k, y0)


def _center_in(p: pathops.Path, width: float) -> pathops.Path:
    x0, _, x1, _ = p.bounds
    return _xf(p, e=(width - (x1 - x0)) / 2.0 - x0)


def _fit_mono(p: pathops.Path, max_w: float = 540.0) -> pathops.Path:
    x0, y0, x1, y1 = p.bounds
    s = min(1.0, max_w / max(x1 - x0, 1.0))
    if s < 1.0:
        cx = (x0 + x1) / 2.0
        p = _xf(p, s, 0, 0, 1, cx - s * cx, 0)
    return _center_in(p, 600.0)


def build_latin_plus(data: Dict[str, Glyph], family: str, weight: int, italic: bool) -> Dict[str, Glyph]:
    S = _Style(data, family, weight, italic)
    out: Dict[str, Glyph] = {}
    stem, hb, k = S.stem, S.hb, S.k
    thin = stem * 0.62                                # thin lines for currency signs

    def put(name: str, cp: int, path: pathops.Path, width: float) -> None:
        if S.mono:
            path, width = _fit_mono(path), 600
        out[name] = (int(round(width)), cp, _to_contours(_clean(path)))

    # -- superscripts / subscripts 4..9 -----------------------------------------
    if S.has("two", "twosuperior"):
        a0, a1 = _bounds(S.p("two")), _bounds(S.p("twosuperior"))
        sx = (a1[2] - a1[0]) / (a0[2] - a0[0])
        sy = (a1[3] - a1[1]) / (a0[3] - a0[1])
        bx, by = a1[0] - sx * a0[0], a1[1] - sy * a0[1]
        sup_w = S.w("twosuperior")
        figs = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine"]
        drop = 450.0
        for n in range(1, 10):
            if not S.has(figs[n]):
                continue
            if n >= 4:
                sp = _xf(S.p(figs[n]), sx, 0, 0, sy, bx, by)
                put(f"uni{0x2070 + n:04X}", 0x2070 + n, sp, sup_w)
            # subscripts: the superscript form, lowered (slant-corrected in the italics)
            src = {1: "onesuperior", 2: "twosuperior", 3: "threesuperior"}.get(n)
            sp = S.p(src) if src and S.has(src) else _xf(S.p(figs[n]), sx, 0, 0, sy, bx, by)
            sw = S.w(src) if src and S.has(src) else sup_w
            put(f"uni{0x2080 + n:04X}", 0x2080 + n, _xf(sp, e=-k * drop, f=-drop), sw)

    # -- fraction slash, one third, two thirds ------------------------------------
    if S.has("onehalf", "one", "two", "three"):
        half = S.data["onehalf"][2]
        parts = [(_path([cb]), _bounds(_path([cb]))) for cb in half]
        slash = max(parts, key=lambda t: t[1][3] - t[1][1])
        rest = [t for t in parts if t is not slash]
        num = max(rest, key=lambda t: t[1][1])
        den = min(rest, key=lambda t: t[1][1])
        put("fraction", 0x2044, _center_in(slash[0], 160.0) if not S.mono else slash[0], 160)
        if S.mono:
            out["fraction"] = (600, 0x2044, _to_contours(_fit_mono(slash[0], 420.0)))

        def digit_into(fig: str, box) -> pathops.Path:
            g = S.p(fig)
            gb = _bounds(g)
            s = (box[3] - box[1]) / (gb[3] - gb[1])
            g = _xf(g, s, 0, 0, s, 0, 0)
            gb = _bounds(g)
            return _xf(g, e=(box[0] + box[2]) / 2 - (gb[0] + gb[2]) / 2, f=box[1] - gb[1])

        hw = S.w("onehalf")
        put("uni2153", 0x2153, _union([digit_into("one", num[1]), slash[0], digit_into("three", den[1])]), hw)
        put("uni2154", 0x2154, _union([digit_into("two", num[1]), slash[0], digit_into("three", den[1])]), hw)

    # -- currency signs ---------------------------------------------------------
    ymid = CAP / 2.0

    def through(name: str, fx: float = 0.5, top: float = 820.0, bot: float = -120.0, wv: float = None):
        b = _bounds(S.p(name))
        xc = b[0] + (b[2] - b[0]) * fx
        return S.vbar(xc, bot, top, wv or thin, ymid)

    if S.has("B"):
        b = _bounds(S.p("B"))
        put("uni0E3F", 0x0E3F, _union([S.p("B"), through("B", 0.47)]), S.w("B"))
        stubs = []
        for fx in (0.36, 0.62):
            xc = b[0] + (b[2] - b[0]) * fx
            stubs += [S.vbar(xc, CAP - 20, CAP + 110, thin, ymid), S.vbar(xc, -110, 20, thin, ymid)]
        put("uni20BF", 0x20BF, _union([S.p("B")] + stubs), S.w("B"))
    if S.has("C"):
        b = _bounds(S.p("C"))
        put("uni20B5", 0x20B5, _union([S.p("C"), through("C", 0.52)]), S.w("C"))
        diag = []
        for fx in (0.40, 0.64):
            x = b[0] + (b[2] - b[0]) * fx
            dx = 0.30 * (CAP + 220)
            diag.append(_poly([(x - dx / 2 - thin / 2, -110), (x - dx / 2 + thin / 2, -110),
                               (x + dx / 2 + thin / 2, CAP + 110), (x + dx / 2 - thin / 2, CAP + 110)]))
        put("uni20A1", 0x20A1, _union([S.p("C")] + diag), S.w("C"))
    if S.has("N"):
        b = _bounds(S.p("N"))
        bars = [S.bar_at(b, y, hb, 40, 40) for y in (CAP * 0.36, CAP * 0.62)]
        put("uni20A6", 0x20A6, _xf(_union([S.p("N")] + bars), e=20), S.w("N") + 40)
    if S.has("R", "s"):
        rw = S.w("R")
        s_p = _xf(S.p("s"), 0.8, 0, 0, 0.8, rw - 30, 0)
        put("uni20A8", 0x20A8, _union([S.p("R"), s_p]), rw + 0.8 * S.w("s") - 30)
    if S.has("dcroat"):
        b = _bounds(S.p("dcroat"))
        put("uni20AB", 0x20AB, _union([S.p("dcroat"), S.bar_at(b, -190 + hb / 2, hb, -10, -10)]), S.w("dcroat"))
    if S.has("K"):
        b = _bounds(S.p("K"))
        put("uni20AD", 0x20AD, _union([S.p("K"), S.bar_at(b, ymid, hb, 30, -10)]), S.w("K"))
    if S.has("T", "L"):
        def two_diags(name: str, fx: float) -> List[pathops.Path]:
            b = _bounds(S.p(name))
            xc = b[0] + (b[2] - b[0]) * fx
            res = []
            for yc in (CAP * 0.30, CAP * 0.52):
                xs = xc + k * (yc - ymid)
                res.append(_poly([(xs - 150, yc - 60 - thin / 2), (xs + 150, yc + 60 - thin / 2),
                                  (xs + 150, yc + 60 + thin / 2), (xs - 150, yc - 60 + thin / 2)]))
            return res
        put("uni20AE", 0x20AE, _union([S.p("T")] + two_diags("T", 0.5)), S.w("T"))
        bL = _bounds(S.p("L"))
        stem_x = bL[0] + stem / 2.0 + (40 if family == "serif" else 0)
        put("uni20BA", 0x20BA, _union([S.p("L")] + two_diags("L", (stem_x - bL[0]) / (bL[2] - bL[0]))), S.w("L"))
        # tenge: a T lowered under a second top bar
        tb = _bounds(S.p("T"))
        gap = hb * 1.1
        t_low = S.slant(_xf(S.unslant(S.p("T"), 0.0), 1, 0, 0, (CAP - hb - gap) / CAP, 0, 0), 0.0)
        top = S.hbar(tb[0], tb[2], CAP - hb, CAP, CAP - hb / 2)
        put("uni20B8", 0x20B8, _union([t_low, top]), S.w("T"))
    if S.has("P"):
        b = _bounds(S.p("P"))
        bars = [S.bar_at(b, y, hb * 0.84, 50, 30) for y in (CAP * 0.60, CAP * 0.78)]
        put("uni20B1", 0x20B1, _union([S.p("P")] + bars), S.w("P"))
    if S.has("G"):
        put("uni20B2", 0x20B2, _union([S.p("G"), through("G", 0.5)]), S.w("G"))
    if S.has("S"):
        sp = S.p("S")
        b = _bounds(sp)
        flat = S.unslant(sp, ymid)
        fb = _bounds(flat)
        mir = S.slant(_xf(flat, -1, 0, 0, 1, fb[0] + fb[2], 0), ymid)
        bars = [S.bar_at(b, y, hb * 0.84, 20, 20) for y in (CAP * 0.40, CAP * 0.60)]
        put("uni20B4", 0x20B4, _union([mir] + bars), S.w("S"))

    # sheqel, manat, lari: drawn from strokes (slanted in the italics)
    wv = stem * 0.92
    def sheqel() -> pathops.Path:
        x0, x1, h = 90.0, 730.0, 620.0
        def build(p):
            p.moveTo(x0 + wv / 2, 0); p.lineTo(x0 + wv / 2, h - wv / 2); p.lineTo(x1 - 210, h - wv / 2); p.lineTo(x1 - 210, 250)
            p.moveTo(x1 - wv / 2, h); p.lineTo(x1 - wv / 2, wv / 2); p.lineTo(x0 + 210, wv / 2); p.lineTo(x0 + 210, h - 250)
        return S.slant(_stroke(build, wv, pathops.LineCap.BUTT_CAP, pathops.LineJoin.MITER_JOIN))
    put("uni20AA", 0x20AA, sheqel(), 820)

    def manat() -> pathops.Path:
        x0, x1, h = 80.0, 620.0, 540.0
        r = (x1 - x0) / 2.0
        def build(p):
            p.moveTo(x0, 0); p.lineTo(x0, h - r)
            p.cubicTo(x0, h - r + r * 0.55, x0 + r - r * 0.55, h, x0 + r, h)
            p.cubicTo(x1 - r + r * 0.55, h, x1, h - r + r * 0.55, x1, h - r)
            p.lineTo(x1, 0)
        arch = _stroke(build, wv, pathops.LineCap.BUTT_CAP, pathops.LineJoin.ROUND_JOIN)
        mid = _rect(x0 + r - thin / 2, 0, x0 + r + thin / 2, h + 140)
        return S.slant(_union([arch, mid]))
    put("uni20BC", 0x20BC, manat(), 700)

    def lari() -> pathops.Path:
        x0, x1, h = 70.0, 640.0, 640.0
        r = 260.0
        def build(p):
            p.moveTo(x1, wv / 2)
            p.lineTo(x0 + 150, wv / 2)
            p.cubicTo(x0 + 40, wv / 2, x0, 90, x0, 240)
            p.cubicTo(x0, 470, x0 + 130, h - wv / 2, (x0 + x1) / 2, h - wv / 2)
            p.cubicTo(x1 - 120, h - wv / 2, x1 - 40, 520, x1 - 40, 330)
        body = _stroke(build, wv, pathops.LineCap.BUTT_CAP, pathops.LineJoin.ROUND_JOIN)
        xm = (x0 + x1) / 2.0
        lines = [_rect(xm - 80 - thin / 2, 300, xm - 80 + thin / 2, h + 90), _rect(xm + 80 - thin / 2, 300, xm + 80 + thin / 2, h + 90)]
        return S.slant(_union([body] + lines))
    put("uni20BE", 0x20BE, lari(), 720)

    # -- letterlike ---------------------------------------------------------------
    def script_l() -> pathops.Path:
        def build(p):
            p.moveTo(90, 150)
            p.cubicTo(220, 250, 320, 420, 320, 575)
            p.cubicTo(320, 690, 280, 735, 236, 735)
            p.cubicTo(180, 735, 158, 662, 158, 540)
            p.lineTo(158, 190)
            p.cubicTo(158, 60, 205, -10, 285, -10)
            p.cubicTo(328, -10, 360, 12, 388, 50)
        return S.slant(_stroke(build, stem * 0.9))
    put("uni2113", 0x2113, script_l(), 450)
    if S.has("e"):
        s = CAP / (XH + 10)
        put("uni212E", 0x212E, _xf(S.p("e"), s, 0, 0, s, 0, 0), S.w("e") * s)
    if S.has("O", "D"):
        # Mono: a smaller true circle that fits the 600 cell (no squeezing by _fit_mono)
        cx, r, s, wd = (300.0, 268.0, 0.40, 600) if S.mono else (430.0, 380.0, 0.54, 860)
        ring = _ring(cx, 350.0, r, stem * (0.56 if S.mono else 0.62))
        d = _xf(S.p("D"), s, 0, 0, s, 0, 0)
        db = _bounds(d)
        d = _xf(d, e=cx - (db[0] + db[2]) / 2, f=350.0 - (db[1] + db[3]) / 2)
        put("uni24B9", 0x24B9, _union([ring, d]), wd)

    # -- arrows ----------------------------------------------------------------------
    def turned(name: str, quarter: int) -> Tuple[pathops.Path, float]:
        g = S.p(name)
        b = _bounds(g)
        cx, cy = (b[0] + b[2]) / 2, (b[1] + b[3]) / 2
        flat = S.unslant(g, cy)
        c, s_ = (0.0, 1.0) if quarter == 1 else (0.0, -1.0)  # +90 (ccw) or -90 (cw)
        rot = _xf(flat, c, s_, -s_, c, cx - c * cx + s_ * cy, cy - s_ * cx - c * cy)
        return S.slant(rot, cy), S.w(name)
    if S.has("arrowupright"):
        p, w = turned("arrowupright", 1)
        put("uni2196", 0x2196, p, w)
    if S.has("arrowdownright"):
        p, w = turned("arrowdownright", -1)
        put("uni2199", 0x2199, p, w)
    if S.has("arrowboth", "arrowup"):
        p, _ = turned("arrowboth", 1)
        put("uni2195", 0x2195, _center_in(p, S.w("arrowup")), S.w("arrowup"))

    # -- math --------------------------------------------------------------------------
    if S.has("six"):
        g = S.p("six")
        b = _bounds(g)
        flat = S.unslant(g, (b[1] + b[3]) / 2)
        fb = _bounds(flat)
        mir = _xf(flat, -1, 0, 0, 1, fb[0] + fb[2], 0)
        put("partialdiff", 0x2202, S.slant(mir, (b[1] + b[3]) / 2), S.w("six"))
    if S.has("Oslash"):
        put("emptyset", 0x2205, S.p("Oslash"), S.w("Oslash"))
    def n_ary(kind: str) -> pathops.Path:
        x0, x1, y0, y1 = 70.0, 690.0, -150.0, CAP
        if kind == "prod":
            parts = [_rect(x0, y1 - hb, x1, y1), _rect(x0 + 70, y0, x0 + 70 + stem, y1),
                     _rect(x1 - 70 - stem, y0, x1 - 70, y1)]
            if family == "serif":
                parts += [_rect(x0 + 20, y0, x0 + 120 + stem, y0 + hb * 0.8), _rect(x1 - 120 - stem, y0, x1 - 20, y0 + hb * 0.8)]
        else:
            ymid_ = (y0 + y1) / 2
            parts = [_rect(x0, y1 - hb, x1, y1), _rect(x0, y0, x1, y0 + hb),
                     _poly([(x0, y1), (x0 + stem * 1.2, y1), (x0 + 380 + stem * 0.6, ymid_), (x0 + 380 - stem * 0.6, ymid_)]),
                     _poly([(x0 + 380 - stem * 0.6, ymid_), (x0 + 380 + stem * 0.6, ymid_), (x0 + stem * 1.2, y0), (x0, y0)])]
        return S.slant(_union(parts), (y0 + y1) / 2)
    put("product", 0x220F, n_ary("prod"), 760)
    put("summation", 0x2211, n_ary("sum"), 760)
    def integral() -> pathops.Path:
        def build(p):
            p.moveTo(70, -150)
            p.cubicTo(150, -175, 205, -120, 215, -10)
            p.lineTo(250, 610)
            p.cubicTo(258, 720, 318, 770, 400, 745)
        return S.slant(_stroke(build, stem * 0.82), 300.0)
    put("integral", 0x222B, integral(), 470)

    # -- angle brackets ------------------------------------------------------------------
    if S.has("parenleft"):
        b = _bounds(S.p("parenleft"))
        pw = S.w("parenleft")
        def angle(left: bool) -> pathops.Path:
            y0, y1 = b[1] + 20, b[3] - 20
            xa, xb = (pw - 70, 80) if left else (70, pw - 80)
            def build(p):
                p.moveTo(xa, y1); p.lineTo(xb, (y0 + y1) / 2); p.lineTo(xa, y0)
            return S.slant(_stroke(build, stem * 0.86, pathops.LineCap.BUTT_CAP, pathops.LineJoin.MITER_JOIN), (y0 + y1) / 2)
        put("uni27E8", 0x27E8, angle(True), pw)
        put("uni27E9", 0x27E9, angle(False), pw)
    if S.has("bar"):
        bw = S.w("bar")
        step = 200.0                     # same in Sans and Serif (duplex widths)
        put("uni2016", 0x2016, _union([S.p("bar"), _xf(S.p("bar"), e=step)]), bw + step)

    # -- geometric shapes (upright in every style) -----------------------------------------
    axis = 300.0
    if S.has("minus"):
        mb = _bounds(S.p("minus"))
        axis = (mb[1] + mb[3]) / 2
    ow = stem * 0.72
    def shape(kind: str, size: float) -> pathops.Path:
        h = size / 2
        cx, cy = 60 + h, axis
        if kind == "square":
            return _rect(cx - h, cy - h, cx + h, cy + h)
        if kind == "circle":
            return _ellipse(cx, cy, h, h)
        if kind == "diamond":
            return _poly([(cx, cy - h), (cx + h, cy), (cx, cy + h), (cx - h, cy)])
        if kind == "lozenge":
            return _poly([(cx, cy - h * 1.15), (cx + h * 0.62, cy), (cx, cy + h * 1.15), (cx - h * 0.62, cy)])
        th = size * 0.866
        if kind == "up":
            return _poly([(cx - h, cy - th / 2), (cx + h, cy - th / 2), (cx, cy + th / 2)])
        if kind == "down":
            return _poly([(cx - h, cy + th / 2), (cx, cy - th / 2), (cx + h, cy + th / 2)])
        if kind == "right":
            return _poly([(cx - th / 2, cy - h), (cx + th / 2, cy), (cx - th / 2, cy + h)])
        return _poly([(cx + th / 2, cy - h), (cx + th / 2, cy + h), (cx - th / 2, cy)])
    BIG, SMALL = (540.0, 300.0) if not S.mono else (480.0, 300.0)
    geo = [
        (0x25A0, "filledbox", "square", BIG, True), (0x25A1, "whitesquare", "square", BIG, False),
        (0x25AA, "uni25AA", "square", SMALL, True), (0x25AB, "uni25AB", "square", SMALL, False),
        (0x25B2, "triagup", "up", BIG, True), (0x25B3, "uni25B3", "up", BIG, False),
        (0x25B4, "uni25B4", "up", SMALL, True), (0x25B5, "uni25B5", "up", SMALL, False),
        (0x25B6, "uni25B6", "right", BIG, True), (0x25B7, "uni25B7", "right", BIG, False),
        (0x25B8, "uni25B8", "right", SMALL, True), (0x25B9, "uni25B9", "right", SMALL, False),
        (0x25BC, "triagdn", "down", BIG, True), (0x25BD, "uni25BD", "down", BIG, False),
        (0x25BE, "uni25BE", "down", SMALL, True), (0x25BF, "uni25BF", "down", SMALL, False),
        (0x25C0, "uni25C0", "left", BIG, True), (0x25C1, "uni25C1", "left", BIG, False),
        (0x25C2, "uni25C2", "left", SMALL, True), (0x25C3, "uni25C3", "left", SMALL, False),
        (0x25C6, "uni25C6", "diamond", BIG, True), (0x25C7, "uni25C7", "diamond", BIG, False),
        (0x25CA, "lozenge", "lozenge", 440.0, False),
        (0x25CB, "circle", "circle", BIG, False), (0x25CF, "uni25CF", "circle", BIG, True),
    ]
    for cp, name, kind, size, filled in geo:
        sh = shape(kind, size)
        if not filled:
            sh = _outline(sh, ow if size > 400 else ow * 0.8)
        put(name, cp, sh, size + 120 if kind != "lozenge" else size * 0.62 + 160)
    if S.has("bullet"):
        bb = _bounds(S.p("bullet"))
        r = (bb[3] - bb[1]) / 2
        cx, cy = (bb[0] + bb[2]) / 2, (bb[1] + bb[3]) / 2
        put("openbullet", 0x25E6, _ring(cx, cy, r, max(stem * 0.42, r * 0.36)), S.w("bullet"))
    return out


LATIN_PLUS_CODEPOINTS = (
    [0x0E3F, 0x2016, 0x2044] + list(range(0x2074, 0x207A)) + list(range(0x2081, 0x208A)) +
    [0x20A1, 0x20A6, 0x20A8, 0x20AA, 0x20AB, 0x20AD, 0x20AE, 0x20B1, 0x20B2, 0x20B4, 0x20B5, 0x20B8,
     0x20BA, 0x20BC, 0x20BE, 0x20BF, 0x2113, 0x212E, 0x2153, 0x2154, 0x2195, 0x2196, 0x2199, 0x2202,
     0x2205, 0x220F, 0x2211, 0x222B, 0x24B9, 0x25A0, 0x25A1, 0x25AA, 0x25AB] + list(range(0x25B2, 0x25C4)) +
    [0x25C6, 0x25C7, 0x25CA, 0x25CB, 0x25CF, 0x25E6, 0x27E8, 0x27E9]
)
