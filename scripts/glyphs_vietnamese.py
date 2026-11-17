"""
Admiralty Sans, Serif and Mono — Vietnamese.

Runs on each finished UFO (after anchors, composites and kerning exist), so it works
the same way for every family, weight and slant:

  * three new marks, drawn from the style's own dot accent size:
      hookabovecomb (U+0309, plus a .cap form), dotbelowcomb (U+0323), horncomb (U+031B);
  * the horn letters Ơ ơ Ư ư (U+01A0, U+01A1, U+01AF, U+01B0);
  * all 90 precomposed letters U+1EA0–U+1EF9, built from components.

Stacking follows common Vietnamese practice: acute, grave and hook sit to the upper
right of a circumflex; a tilde over a circumflex and every mark over a breve are
stacked. Stacks on capitals are kept under the font's 980 ascent.
"""

from __future__ import annotations
import math
import unicodedata
from typing import Dict, List, Optional, Tuple

import pathops
import ufoLib2
from ufoLib2.objects import Anchor, Component

from design_system import clean_contour_nicks
from glyphs_box import _to_contours

MAX_Y = 975.0
HORN_EXTRA = {"O": 40, "o": 36, "U": 56, "u": 52}  # advance added to the horn letters (Sans = Serif)

MARK_OF = {0x0300: "gravecomb", 0x0301: "acutecomb", 0x0303: "tildecomb", 0x0309: "hookabovecomb",
           0x0302: "circumflexcomb", 0x0306: "brevecomb", 0x0323: "dotbelowcomb"}
SIDE_MARKS = {"acutecomb", "gravecomb", "hookabovecomb"}
HORN_BASE = {"O": "Ohorn", "o": "ohorn", "U": "Uhorn", "u": "uhorn"}


# ---------------------------------------------------------------------------
# small helpers
# ---------------------------------------------------------------------------

def _glyph_path(ufo: ufoLib2.Font, name: str) -> pathops.Path:
    p = pathops.Path()
    pen = p.getPen()
    g = ufo[name]
    g.draw(pen)
    for c in g.components:  # flatten one level of components
        sub = pathops.Path()
        ufo[c.baseGlyph].draw(sub.getPen())
        a, b, cc, d, e, f = c.transformation
        p.addPath(sub.transform(a, b, cc, d, e, f))
    return p


def _xf(p: pathops.Path, a=1.0, b=0.0, c=0.0, d=1.0, e=0.0, f=0.0) -> pathops.Path:
    return p.transform(a, b, c, d, e, f)


def _shear(p: pathops.Path, k: float, y0: float) -> pathops.Path:
    return _xf(p, 1.0, 0.0, k, 1.0, -k * y0, 0.0) if k else p


def _clean(p: pathops.Path) -> pathops.Path:
    return pathops.simplify(p, fix_winding=True)


def _stroke(points, w: float) -> pathops.Path:
    """points: [(x, y), (c1, c2, p), ...] — a move then cubic segments."""
    p = pathops.Path()
    p.moveTo(*points[0])
    for seg in points[1:]:
        if len(seg) == 3:
            p.cubicTo(*seg[0], *seg[1], *seg[2])
        else:
            p.lineTo(*seg)
    p.stroke(w, pathops.LineCap.ROUND_CAP, pathops.LineJoin.ROUND_JOIN, 4.0)
    p.convertConicsToQuads()
    return _clean(p)


def _put_outline(g, path: pathops.Path) -> None:
    g.clearContours()
    pen = g.getPen()
    for cb in _to_contours(path):
        clean_contour_nicks(cb).draw_to_pen(pen)


def _bounds(ufo, name) -> Tuple[float, float, float, float]:
    return ufo[name].getBounds(ufo)


def _anchor(g, name) -> Optional[Tuple[float, float]]:
    for a in g.anchors:
        if a.name == name:
            return (a.x, a.y)
    return None


def _samples(p: pathops.Path, n: int = 24):
    """Points along a pathops path (for finding attach points)."""
    out, cur = [], None
    for verb, pts in p:
        if verb == pathops.PathVerb.MOVE:
            cur = pts[0]
            out.append(cur)
        elif verb == pathops.PathVerb.LINE:
            out.append(pts[0]); cur = pts[0]
        elif verb == pathops.PathVerb.QUAD:
            c, e = pts
            for i in range(1, n + 1):
                t = i / n
                out.append(((1 - t) ** 2 * cur[0] + 2 * (1 - t) * t * c[0] + t * t * e[0],
                            (1 - t) ** 2 * cur[1] + 2 * (1 - t) * t * c[1] + t * t * e[1]))
            cur = e
        elif verb == pathops.PathVerb.CUBIC:
            c1, c2, e = pts
            for i in range(1, n + 1):
                t = i / n
                mt = 1 - t
                out.append((mt ** 3 * cur[0] + 3 * mt * mt * t * c1[0] + 3 * mt * t * t * c2[0] + t ** 3 * e[0],
                            mt ** 3 * cur[1] + 3 * mt * mt * t * c1[1] + 3 * mt * t * t * c2[1] + t ** 3 * e[1]))
            cur = e
    return out


# ---------------------------------------------------------------------------
# the new marks
# ---------------------------------------------------------------------------

def _draw_marks(ufo: ufoLib2.Font, k: float, mono: bool) -> Dict[str, float]:
    db = _bounds(ufo, "dotaccentcomb")
    dot_d = db[3] - db[1]                       # the style's dot size sets the mark weight
    hook_w = dot_d * 0.50
    horn_w = dot_d * 0.80

    # dot below: the dot accent itself, moved under the baseline (along the slant)
    dot = _glyph_path(ufo, "dotaccentcomb")
    cx, cy = (db[0] + db[2]) / 2, (db[1] + db[3]) / 2
    ty = -(64 + dot_d / 2)
    tx = k * ty
    g = ufo.newGlyph("dotbelowcomb")
    g.width, g.unicodes = 0, [0x0323]
    _put_outline(g, _xf(dot, e=tx - cx, f=ty - cy))
    g.anchors = [Anchor(x=0, y=0, name="_bottom"), Anchor(x=round(k * -240), y=-240, name="bottom")]

    # hook above: the top of a question mark, centred on the mark axis
    def hook(y0: float, sy: float) -> pathops.Path:
        def P(x, y):
            return (x, y0 + (y - 520) * sy)
        pts = [P(-56, 702), (P(-40, 728), P(-12, 740), P(16, 740)),
               (P(56, 740), P(78, 718), P(78, 688)), (P(78, 656), P(52, 640), P(14, 634)),
               P(14, 588)]
        return _shear(_stroke(pts, hook_w), k, y0)

    g = ufo.newGlyph("hookabovecomb")
    g.width, g.unicodes = 0, [0x0309]
    _put_outline(g, hook(520.0, 1.0))
    g.anchors = [Anchor(x=0, y=520, name="_top"), Anchor(x=round(k * 200), y=720, name="top")]

    g = ufo.newGlyph("hookabovecomb.cap")
    g.width = 0
    _put_outline(g, _xf(hook(700.0, 0.80), e=0, f=0))
    # cap marks start ~40 above cap height, like the existing .cap marks
    g.anchors = [Anchor(x=0, y=700, name="_top"), Anchor(x=round(k * 160), y=860, name="top")]

    # horn: a short spur that leaves the letter's right side and rises; origin = attach point
    t = horn_w
    pts = [(0.02 * t, -0.42 * t), ((0.24 * t, -0.05 * t), (0.62 * t, 0.62 * t), (0.62 * t, 1.80 * t))]
    horn = _shear(_stroke(pts, horn_w), k, 0.0)
    g = ufo.newGlyph("horncomb")
    g.width, g.unicodes = 0, [0x031B]
    _put_outline(g, horn)
    g.anchors = [Anchor(x=0, y=0, name="_horn")]
    return {"horn_w": horn_w}


# ---------------------------------------------------------------------------
# horn letters
# ---------------------------------------------------------------------------

def _horn_attach(ufo: ufoLib2.Font, base: str, horn_w: float, k: float) -> Tuple[float, float]:
    p = _glyph_path(ufo, base)
    pts = _samples(p)
    xmin, ymin, xmax, ymax = p.bounds
    if base in ("O", "o"):
        # the right side of the bowl, a little below its top
        ty = ymax - (ymax - ymin) * 0.24
        xs = []
        for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
            if (y0 - ty) * (y1 - ty) <= 0 and y0 != y1:
                xs.append(x0 + (x1 - x0) * (ty - y0) / (y1 - y0))
        x = max(xs)
        return (x - horn_w * 0.40, ty)
    # U / u: top of the right stem
    top = max(q[1] for q in pts)
    right = max(q[0] for q in pts if q[1] > top - 4)
    return (right - horn_w * 0.40, top - horn_w * 0.45 - 46)


def _make_horn_letters(ufo, k: float, mono: bool, horn_w: float, order: List[str]) -> None:
    for base, name in HORN_BASE.items():
        bg = ufo[base]
        ax, ay = _horn_attach(ufo, base, horn_w, k)
        bg.anchors = list(bg.anchors) + [Anchor(x=round(ax), y=round(ay), name="horn")]
        g = ufo.newGlyph(name)
        g.unicodes = [{"Ohorn": 0x01A0, "ohorn": 0x01A1, "Uhorn": 0x01AF, "uhorn": 0x01B0}[name]]
        g.width = bg.width + (0 if mono else HORN_EXTRA[base])
        if bg.components:
            for c in bg.components:
                g.components.append(Component(baseGlyph=c.baseGlyph, transformation=c.transformation))
        else:
            g.components.append(Component(baseGlyph=base))
        g.components.append(Component(baseGlyph="horncomb", transformation=(1, 0, 0, 1, round(ax), round(ay))))
        g.anchors = [Anchor(x=a.x, y=a.y, name=a.name) for a in bg.anchors if a.name != "horn"]
        order.append(name)


# ---------------------------------------------------------------------------
# precomposed letters
# ---------------------------------------------------------------------------

def _cap_variant(ufo, mark: str, is_cap: bool) -> str:
    return f"{mark}.cap" if is_cap and f"{mark}.cap" in ufo else mark


def _place(ufo, mark: str, anchor_xy, anchor_name: str) -> Tuple[float, float]:
    m = _anchor(ufo[mark], f"_{anchor_name}")
    return (anchor_xy[0] - m[0], anchor_xy[1] - m[1])


def _shifted_bounds(ufo, mark, dx, dy):
    b = _bounds(ufo, mark)
    return (b[0] + dx, b[1] + dy, b[2] + dx, b[3] + dy)


def _compose(ufo, cp: int, k: float, order: List[str], new_bases: Dict[str, str]) -> None:
    ch = chr(cp)
    nfd = unicodedata.normalize("NFD", ch)
    base_ch, marks = nfd[0], [ord(c) for c in nfd[1:]]
    base = base_ch
    if 0x031B in marks:
        base = HORN_BASE[base_ch]
        marks.remove(0x031B)
    below = [MARK_OF[m] for m in marks if m == 0x0323]
    above = [MARK_OF[m] for m in marks if m != 0x0323]
    if base == "i" and above:
        base = "dotlessi"
    is_cap = base_ch.isupper()

    bg = ufo[base]
    name = f"uni{cp:04X}"
    g = ufo.newGlyph(name)
    g.width, g.unicodes = bg.width, [cp]
    if bg.components:
        for c in bg.components:
            g.components.append(Component(baseGlyph=c.baseGlyph, transformation=c.transformation))
    else:
        g.components.append(Component(baseGlyph=base))
    anchors = {a.name: (a.x, a.y) for a in bg.anchors}
    comps: List[Tuple[str, float, float]] = []

    # --- below -------------------------------------------------------------------
    for m in below:
        if base_ch == "y":
            top = anchors["top"]
            pos = (top[0] - k * top[1] + bg.width * 0.20, 0.0)
        else:
            pos = anchors.get("bottom", (bg.width / 2, 0.0))
        dx, dy = _place(ufo, m, pos, "bottom")
        comps.append((m, dx, dy))
        out = _anchor(ufo[m], "bottom")
        anchors["bottom"] = (out[0] + dx, out[1] + dy)

    # --- above -------------------------------------------------------------------
    if above:
        m1 = _cap_variant(ufo, above[0], is_cap)
        dx1, dy1 = _place(ufo, m1, anchors["top"], "top")
        placed = [(m1, dx1, dy1)]
        b1 = _shifted_bounds(ufo, m1, dx1, dy1)
        top1 = _anchor(ufo[m1], "top")
        top_anchor = (top1[0] + dx1, top1[1] + dy1)
        if len(above) == 2:
            m2 = _cap_variant(ufo, above[1], is_cap)
            mb = _bounds(ufo, m2)
            if above[0] == "circumflexcomb" and above[1] in SIDE_MARKS:
                # beside the circumflex, to its upper right
                h1 = b1[3] - b1[1]
                ty = b1[1] + h1 * (0.50 if is_cap else 0.56)
                lift = ty - mb[1]
                tx = b1[2] - (b1[2] - b1[0]) * 0.10 + (6 if above[1] == "gravecomb" else 0)
                dx2 = tx - mb[0] + k * 0.0
                dy2 = lift
            else:
                # stacked: centred on the first mark's top anchor, small gap
                gap = 18 if is_cap else 26
                a2 = _anchor(ufo[m2], "_top")
                dy2 = b1[3] + gap - mb[1]
                dx2 = top_anchor[0] - a2[0] + k * ((dy2 + a2[1]) - top_anchor[1])
            b2 = (mb[0] + dx2, mb[1] + dy2, mb[2] + dx2, mb[3] + dy2)
            over = b2[3] - MAX_Y
            if over > 0:
                # keep the stack under the ascent: lower both marks a little toward the letter
                sink = min(over, 24.0)
                dy1 -= sink; dy2 -= sink
                dx1 -= k * sink; dx2 -= k * sink
                placed = [(m1, dx1, dy1)]
                over -= sink
                if over > 0:
                    # then flatten the upper mark (scale y about its bottom)
                    s = max(0.70, 1.0 - over / (mb[3] - mb[1]))
                    placed.append((m2, dx2, dy2, s))
                else:
                    placed.append((m2, dx2, dy2))
            else:
                placed.append((m2, dx2, dy2))
            top2 = _anchor(ufo[m2], "top")
            top_anchor = (top2[0] + dx2, top2[1] + dy2)
        comps += placed
        anchors["top"] = top_anchor

    for c in comps:
        if len(c) == 4:
            m, dx, dy, s = c
            yb = _bounds(ufo, m)[1]
            # y' = s*y + (dy + yb*(1-s)) keeps the mark's bottom in place
            g.components.append(Component(baseGlyph=m, transformation=(1, 0, 0, s, round(dx), round(dy + yb * (1 - s)))))
        else:
            m, dx, dy = c
            g.components.append(Component(baseGlyph=m, transformation=(1, 0, 0, 1, round(dx), round(dy))))
    g.anchors = [Anchor(x=round(x), y=round(y), name=n) for n, (x, y) in anchors.items()]
    order.append(name)
    new_bases[name] = base


VIET_CODEPOINTS = list(range(0x1EA0, 0x1EFA))


def add_vietnamese(ufo: ufoLib2.Font) -> List[str]:
    """Add Vietnamese marks and letters to a finished UFO. Returns the new glyph names."""
    if "dotaccentcomb" not in ufo or "Ohorn" in ufo:
        return []
    k = math.tan(math.radians(-(ufo.info.italicAngle or 0.0)))
    mono = all(ufo[n].width == 600 for n in ("i", "m", "O") if n in ufo)
    order = list(ufo.lib.get("public.glyphOrder", []))
    before = set(order)
    info = _draw_marks(ufo, k, mono)
    order += ["dotbelowcomb", "hookabovecomb", "hookabovecomb.cap", "horncomb"]
    _make_horn_letters(ufo, k, mono, info["horn_w"], order)
    new_bases: Dict[str, str] = {n: b for b, n in HORN_BASE.items()}
    have = {u for g in ufo for u in g.unicodes}
    for cp in VIET_CODEPOINTS:
        if cp in have:          # e.g. Ygrave/ygrave already exist (Welsh)
            continue
        _compose(ufo, cp, k, order, new_bases)
    ufo.lib["public.glyphOrder"] = order

    # kerning: new letters join their base letter's classes (horn letters: left side only)
    if ufo.groups:
        for name, base in new_bases.items():
            root = base
            horned = False
            for b, hn in HORN_BASE.items():
                if base == hn:
                    root, horned = b, True
            if name in HORN_BASE.values():
                root, horned = base, True
            for gname, members in ufo.groups.items():
                if root in members and name not in members:
                    if horned and gname.startswith("public.kern1."):
                        continue
                    members.append(name)
    return [n for n in order if n not in before]
