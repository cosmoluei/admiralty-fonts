"""Shared stems, bowls, dots and bars for related letters and currency signs."""

from functools import lru_cache
import copy

import numpy as np
import pathops
from fontTools.ttLib.tables._g_l_y_f import GlyphCoordinates
from fontTools.varLib.models import normalizeLocation, supportScalar

from accent_masters import as_path
from build_axis_study import AXES
from serif_thin import ThinPen
from sign_masters import fit_box, outlined, Nib
from bowl_drawings import thin_d, thin_g, thin_bitcoin, estimated
from check_word_proof import Edges, section

STEMS = {
    "i",
    "j",
    "l",
    "dotlessi",
    "dotlessj",
    "f",
    "longs",
    "h",
    "n",
    "m",
    "r",
    "u",
    "t",
    "micro",
    "kgreenlandic",
}
BARRED = {"hbar": "h", "tbar": "t", "Tbar": "T", "dcroat": "d", "Dcroat": "D", "Eth": "D", "Hbar": "H"}
DOTTED = {"ldot": "l", "Ldot": "L"}
SLASHED = {"lslash": "l", "Lslash": "L"}
DERIVED = {"partialdiff": "six", "uni212E": "e"}
PAIRS = {"ij": ("i", "j"), "IJ": ("I", "J"), "uni20A8": ("R", "s"), "napostrophe": ("quoteright", "n")}
CURRENCIES = {
    "uni0E3F": "B",
    "uni20BF": "B",
    "uni20B2": "G",
    "uni20B5": "C",
    "uni20A1": "C",
    "uni20AB": "dcroat",
}
PUNCT = {"exclam", "exclamdown", "exclamdown.case", "question", "questiondown", "questiondown.case"}
DIAGONAL = {"v", "w", "x", "y", "z"}
SMALL = {"numero", "trademark", "ordfeminine", "ordmasculine"}
BOWLS = {"g", "q", "eth", "section"}
MONEY = {"dollar", "cent", "yen"}
JOINED = {
    "uni20A6",
    "uni20B1",
    "uni20AD",
    "uni20AE",
    "uni20B4",
    "rupee",
    "ruble",
    "uni20B8",
    "germandbls",
    "Germandbls",
}
NAMES = (
    STEMS
    | {"Eng", "eng"}
    | DIAGONAL
    | SMALL
    | BOWLS
    | MONEY
    | JOINED
    | BARRED.keys()
    | DOTTED.keys()
    | SLASHED.keys()
    | DERIVED.keys()
    | PAIRS.keys()
    | CURRENCIES.keys()
    | PUNCT
)


def handles(design, name):
    if design.serif and (
        name in ("t", "tbar", "germandbls", "Germandbls")
        or name in DIAGONAL
        or name == "g"
        and not design.slant
    ):
        return False  # The reviewed Serif ascender and foot have dedicated masters.
    return name in NAMES or name=="B" and not design.serif or design.serif and design.slant and name in ("F","I")


@lru_cache(maxsize=160)
def base_masters(design, name):
    return design.design_glyph(name)


@lru_cache(maxsize=1500)
def component(design, name, w, d):
    glyph, tuples = base_masters(design, name)
    loc = normalizeLocation(dict(wght=w, wdth=d, RADI=0), AXES)
    xy = np.asarray(glyph.coordinates, dtype=float).copy()
    for variation in tuples:
        amount = supportScalar(loc, variation.axes)
        if amount:
            xy += amount * np.asarray(variation.coordinates[:-4])
    instance = copy.copy(glyph)
    instance.coordinates = GlyphCoordinates(xy.tolist())
    p = pathops.Path()
    instance.draw(p.getPen(), design.regular["glyf"])
    result = p.transform(1, 0, -design.slant, 1, 0, 0)
    result.simplify(clockwise=True)
    clean = pathops.Path()
    for contour in result.contours:
        if contour.area > 2:
            clean.addPath(contour)
    return clean


def crossings(path, y):
    edges = Edges(None, 1)
    path.draw(edges)
    return section(np.asarray(edges.edges), y)


def black_body(design, name, native, d):
    # Expand the released contour along its normal so its original curved
    # shoulders, serif brackets and ball terminals survive in the Black.
    # Hold the baseline and ascender while leaving room for wider stems.
    sx, dx = design.transform(name, 400, d)
    advance = design.advance(name, 900, d)
    dx += (advance - design.advance(name, 400, d)) / 2
    current = native.transform(sx, 0, 0, 1, dx, 0)
    l, b, r, t = current.bounds
    spread = 23
    expected = len(list(native.contours))
    for _ in range(8):
        nib = current.transform(1 / spread, 0, 0, 1 / (spread * 0.83), 0, 0)
        nib.stroke(2, pathops.LineCap.BUTT_CAP, pathops.LineJoin.MITER_JOIN, 2)
        nib.convertConicsToQuads(0.002)
        expanded = pathops.op(current, nib.transform(spread, 0, 0, spread * 0.83, 0, 0), pathops.PathOp.UNION)
        if name in ("uni20A6", "uni20AD"):
            # The small triangles between a diagonal and two crossing bars
            # need their own counter master. Preserve a minimum fraction of
            # each original opening while the exterior gains its Black weight.
            for hole in sorted(current.contours, key=lambda c: c.area, reverse=True)[1:]:
                x0, y0, x1, y1 = hole.bounds
                k = 0.61 if hole.area < 1400 else 0.36
                opening = hole.transform(k, 0, 0, k, (1 - k) * (x0 + x1) / 2, (1 - k) * (y0 + y1) / 2)
                expanded = pathops.op(expanded, opening, pathops.PathOp.DIFFERENCE)
        rings = [c for c in expanded.contours if c.area > 2]
        # Vanishing counter fragments would disappear after final integer
        # rounding; leave several design units of white at the narrowest.
        stable = len(rings) == expected and min(c.area for c in rings) > 50
        if stable and name in ("uni20A6", "uni20AD"):
            # Leave room for grid fitting on both sides of a counter or
            # aperture. In a narrow K or N crossed by rails the last few
            # units can otherwise turn into a pinhole between masters.
            probe = pathops.Path(expanded)
            probe.stroke(5, pathops.LineCap.ROUND_CAP, pathops.LineJoin.ROUND_JOIN, 2)
            probe.convertConicsToQuads(0.04)
            probe = pathops.op(expanded, probe, pathops.PathOp.UNION)
            stable = len([c for c in probe.contours if c.area > 6]) == expected
        if stable:
            left, right = l - spread, r + spread
            if design.mono:
                left, right = (
                    max(left, l - 8, 8 - design.slant * 350),
                    min(right, r + 8, 592 - design.slant * 350),
                )
            return fit_box(expanded, (left, b, right, t))
        spread *= 0.80
    raise ValueError(f"Black counter pinched in {name}")


def stems(design, name, native, w, d, transform=None):
    sx, dx = transform or design.transform(name, w, d)
    forms = list(native.contours)
    body = max(forms, key=lambda c: c.bounds[3] - c.bounds[1])
    x0, y0, x1, y1 = body.bounds
    xs = crossings(body, 235)
    centers = (xs[::2] + xs[1::2]) / 2 * sx + dx
    X = lambda x: x * sx + dx
    l, r = X(x0), X(x1)
    t = 24 if w == 100 else min(128, max(97, (xs[1] - xs[0]) + 40))
    hair = (0.72 if design.serif else 0.89) * t
    p = ThinPen(1)
    x = centers[0]
    mono, serif, italic = design.mono, design.serif, bool(design.slant)

    def line(x, y, xx, yy, ink=t):
        p.stroke((x, y), (xx, yy), width=ink, aspect=1)

    def cap(x, y):
        if mono:
            line(l, y - hair / 2, x + t / 2, y - hair / 2, hair)
        elif serif:
            if w == 100:
                p.entry(x, y)
            else:
                p.serif(x, y, t / 2, top=True, right=0.08)

    def foot(x):
        if serif and not italic:
            p.serif(x, 0, t / 2)

    def curl(x, end, rise=16):
        horizontal = max(end - x, t * 0.77)
        mid = x + 0.49 * horizontal
        y = y0 + hair / 2
        p.stroke(
            (x, y + 95),
            (x, y + 48, x + 0.05 * horizontal, y, mid, y),
            (mid + 0.20 * horizontal, y, end - 0.09 * horizontal, y + 0.65 * rise, end, y + rise),
            width=t,
            aspect=hair / t,
        )

    kind = {"dotlessi": "i", "dotlessj": "j"}.get(name, name)
    if kind in ("i", "j", "l"):
        cap(x, y1)
        if kind == "j":
            y = y0 + hair / 2
            end = min(l + 0.08 * t, x - 0.70 * t)
            mid = end + 0.37 * (x - end)
            p.stroke(
                (x, y1),
                (x, y + 125),
                (x, y + 42, mid + 0.32 * (x - mid), y, mid, y),
                (mid - 0.37 * (mid - end), y, end + 0.2 * (mid - end), y + 9, end, y + 20),
                width=t,
                aspect=hair / t,
            )
        elif (kind == "l" and (mono or italic or not serif) and x1 - x0 > 1.4 * (xs[1] - xs[0])) or (
            kind == "i" and italic and not mono
        ):
            line(x, y1, x, y0 + hair / 2 + 95)
            curl(x, max(x + 64, r - t * 0.16), rise=29)
        else:
            line(x, y1, x, 0)
            if mono:
                line(l, hair / 2, r, hair / 2, hair)
            else:
                foot(x)
        if len(forms) > 1:
            dot = min(forms, key=lambda c: c.bounds[3] - c.bounds[1])
            a, b, z, h = dot.bounds
            ray = 20 if w == 100 else min(66, (h - b) * 0.62)
            p.drop(X((a + z) / 2), (b + h) / 2, ray, ray)
    elif kind in ("t", "f", "longs"):
        # Get the shaft in the middle of its unbranched lower stem.
        if kind == "t":
            line(x, y1, x, y0 + hair / 2 + 95)
            curl(x, r - t * 0.12)
        else:
            hi = y1 - hair / 2
            h = x + max(t * 0.65, 0.55 * (r - x))
            lo = y0 if y0 > -100 else 0
            p.stroke(
                (x, lo),
                (x, hi - 115),
                (x, hi - 40, x + 0.30 * (h - x), hi, h, hi),
                (h + 0.35 * (r - h), hi, r - 0.20 * (r - h), hi - 4, r - t * 0.10, hi - 15),
                width=t,
                aspect=hair / t,
            )
            if y0 < -100:
                y = y0 + hair / 2
                p.stroke(
                    (x, 4),
                    (x, y + 70, x - 24, y, x - 70, y),
                    (x - 83, y, x - 94, y + 2, x - 102, y + 7),
                    width=t,
                    aspect=hair / t,
                )
            elif mono:
                line(l + 8, hair / 2, x + max(t * 0.67, (r - l) * 0.23), hair / 2, hair)
            else:
                foot(x)
        at = 520 - hair / 2 if kind == "t" or design.serif else 486
        line(l, at, x + t * 0.4 if kind == "longs" else r, at, hair)
    elif kind in ("h", "n", "m", "r"):
        cap(x, y1 if kind == "h" else 520)
        line(x, y1 if kind == "h" else 520, x, 0)
        foot(x)
        if mono and kind == "r":
            line(l, hair / 2, x + (x - l), hair / 2, hair)
        if kind == "r":
            high = 530 - hair / 2
            end = r - t * 0.12
            p.stroke(
                (x, 310),
                (x + 12, 427, x + 0.37 * (end - x), high, x + 0.70 * (end - x), high),
                (x + 0.82 * (end - x), high, end - 13, high - 4, end, high - 19),
                width=t,
                aspect=hair / t,
            )
        else:
            for a, z in zip(centers, centers[1:]):
                span = z - a
                high = 530 - hair / 2
                mid = a + 0.55 * span
                hooked = serif and italic and z == centers[-1]
                p.stroke(
                    (a, 305),
                    (a + 0.08 * span, 418, mid - 0.28 * span, high, mid, high),
                    (mid + 0.30 * span, high, z, high - 65, z, high - 170),
                    (z, y0 + hair / 2 + 95 if hooked else 0),
                    width=t,
                    aspect=hair / t,
                )
                if hooked:
                    curl(z, z + max(50, 48*sx), rise=40)
                foot(z)
    elif kind == "kgreenlandic":
        x = crossings(body, 75)[:2].mean() * sx + dx
        cap(x, 520)
        line(x, 520, x, 0)
        foot(x)
        tip = r - (27 if serif else 14)
        joint = (x, 208)
        knee = (x + 0.33 * (tip - x), 311)
        p.ribbon(joint, (tip, 520), hair, head=serif, start_cut=0)
        p.ribbon(knee, (tip + 3, 0), t, foot=serif, start_cut=(tip - x) / 312)
    elif kind in ("u", "micro"):
        a, z = centers[0], centers[-1]
        mid = a + 0.46 * (z - a)
        low = -10 + hair / 2
        p.stroke(
            (a, 520),
            (a, 177),
            (a, low + 66, mid - 0.27 * (z - a), low, mid, low),
            (mid + 0.26 * (z - a), low, z, low + 72, z, 195),
            width=t,
            aspect=hair / t,
        )
        line(z, 520, z, 0)
        foot(z)
        if kind == "micro":
            line(a, 520, a, y0)
        elif serif:
            p.entry(a, 520)
            p.entry(z, 520)
    return p.shape


def mapped_part(design, child, w, d, source_box, sx, dx, mirror=False):
    # Map the *reference frame* into the component, then carry the new ink
    # with it. Fitting the current ink to a fixed bbox would re-fatten Thin i.
    release = as_path(design.regular.getGlyphSet(), child, (1, 0, -design.slant, 1, 0, 0))
    a, b, c, e = release.bounds
    l, lo, r, hi = source_box
    scale, shift = design.transform(child, w, d)
    mx = (r - l) / (c - a) * sx / scale
    my = (hi - lo) / (e - b)
    start = c if mirror else a
    if mirror:
        mx = -mx
    return component(design, child, w, d).transform(
        mx, 0, 0, my, l * sx + dx - (start * scale + shift) * mx, lo - b * my
    )


def quadratic_parts(glyph, xy):
    """Expose implied TrueType points without changing the quadratic curves."""
    parts = []
    start = 0
    for end in glyph.endPtsOfContours:
        nodes = xy[start : end + 1]
        on = np.asarray(glyph.flags[start : end + 1]) & 1
        segments = []
        for i, a in enumerate(nodes):
            j = (i + 1) % len(nodes)
            if on[i] and on[j]:
                segments.extend((a, (a + nodes[j]) / 2))
            elif not on[i]:
                prev = nodes[i - 1]
                segments.extend((prev if on[i - 1] else (prev + a) / 2, a))
        parts.append(np.array(segments))
        start = end + 1
    return parts


def part_bounds(contours):
    return (
        min(c.bounds[0] for c in contours),
        min(c.bounds[1] for c in contours),
        max(c.bounds[2] for c in contours),
        max(c.bounds[3] for c in contours),
    )


def assembled_tracks(design, name, cells):
    """Attach existing variable letters before rounding; keep their own point correspondence."""
    native = as_path(design.regular.getGlyphSet(), name, (1, 0, -design.slant, 1, 0, 0))
    if name == "uni20AB":
        parts = list(native.contours)
        bar = min(parts, key=lambda c: c.bounds[3])
        groups = [("dcroat", [c for c in parts if c is not bar])]
    else:
        a, b = PAIRS[name]
        parts = sorted(native.contours, key=lambda c: (c.bounds[0] + c.bounds[2]) / 2)
        n = design.regular["glyf"][a].numberOfContours
        groups = [(a, parts[:n]), (b, parts[n:])]
    rows = []
    for w, d in cells:
        sx, dx = design.transform(name, w, d)
        # A wider master of a monospaced pair uses the same cell as the
        # default. Let its two smaller letters grow in their own frames.
        if design.mono:
            sx, dx = design.transform(name, 400, d)
        for radius in (0, 100):
            row = []
            for child, forms in groups:
                glyph, tuples = base_masters(design, child)
                loc = normalizeLocation(dict(wght=w, wdth=d, RADI=radius), AXES)
                xy = np.asarray(glyph.coordinates, dtype=float).copy()
                for var in tuples:
                    amount = supportScalar(loc, var.axes)
                    if amount:
                        xy += amount * np.asarray(var.coordinates[:-4])
                ux, offset = design.transform(child, w, d)
                x0, y0, x1, y1 = as_path(
                    design.regular.getGlyphSet(), child, (1, 0, -design.slant, 1, 0, 0)
                ).bounds
                l, b, r, h = part_bounds(forms)
                z = xy[:, 0] - design.slant * xy[:, 1]
                # Keep the prototype scale of each letter rather than
                # fitting the Thin ink back to its Regular ink bounds.
                mx = (r - l) / (x1 - x0)
                horizontal_scale = sx / ux
                if design.mono:
                    horizontal_scale = 1
                cx = (l + r) * sx / 2 + dx
                xy[:, 0] = cx + (z - ((x0 + x1) * ux / 2 + offset)) * mx * horizontal_scale
                xy[:, 1] = b + (xy[:, 1] - y0) * (h - b) / (y1 - y0)
                row.append(quadratic_parts(glyph, xy))
            if name == "uni20AB":
                l, b, r, h = bar.bounds
                height = {100: 21, 400: h - b, 900: 94}[w]
                mid = (b + h) / 2
                b, h = mid - height / 2, mid + height / 2
                pts = np.array([[l * sx + dx, b], [l * sx + dx, h], [r * sx + dx, h], [r * sx + dx, b]])
                row.append([np.stack([pts, (pts + np.roll(pts, -1, axis=0)) / 2], axis=1).reshape(-1, 2)])
            elif (w, d) != (400, 100):
                left, right = row
                # Only consider slices at heights occupied by both letters.
                paths = []
                for group in row:
                    path = pathops.Path()
                    pen = path.getPen()
                    for nodes in group:
                        pen.moveTo(tuple(nodes[0]))
                        for k in range(1, len(nodes), 2):
                            pen.qCurveTo(tuple(nodes[k]), tuple(nodes[(k + 1) % len(nodes)]))
                        pen.closePath()
                    edges = Edges(None, 2)
                    path.draw(edges)
                    paths.append(np.array(edges.edges))
                gaps = []
                for y in (1, 6, 14, 24, 40, 64, 96, 200, 355, 448, 494, 516, 610, 640, 685):
                    a, b = (section(path, y) for path in paths)
                    if len(a) and len(b):
                        gaps.append(b.min() - a.max())
                shift = max(0, (17 - min(gaps, default=17)) / 2)
                for part in left:
                    part[:, 0] -= shift
                for part in right:
                    part[:, 0] += shift
            all_parts = [q for group in row for q in group]
            ends = np.cumsum([len(q) for q in all_parts]) - 1
            coords = np.vstack(all_parts)
            rows.append(coords[:, 0] + design.slant * coords[:, 1] + 1j * coords[:, 1])
    return rows, ends.tolist()


def mono_pair(design, name, native, w, d):
    a, b = PAIRS[name]
    parts = sorted(native.contours, key=lambda c: (c.bounds[0] + c.bounds[2]) / 2)
    n = design.regular["glyf"][a].numberOfContours
    sx, dx = design.transform(name, 400, d)
    paths = []
    for child, forms in [(a, parts[:n]), (b, parts[n:])]:
        group = pathops.Path()
        for form in forms:
            group.addPath(form)
        if w == 900:
            # The prototype in IJ has a short foot and a full-width stem.
            # Grow those two features in its own frame.
            current = group.transform(sx, 0, 0, 1, dx, 0)
            nib = current.transform(1 / 21, 0, 0, 1 / 15, 0, 0)
            nib.stroke(2, pathops.LineCap.BUTT_CAP, pathops.LineJoin.MITER_JOIN, 2)
            nib.convertConicsToQuads(0.002)
            grown = pathops.op(current, nib.transform(21, 0, 0, 15, 0, 0), pathops.PathOp.UNION)
            l, lo, r, hi = current.bounds
            path = fit_box(grown, (l - 7, lo, r + 7, hi))
        elif child in ("i", "j"):
            path = stems(design, child, group, 100, d, (sx, dx))
        else:
            l, lo, r, hi = group.bounds
            x = crossings(group, 350).mean() * sx + dx
            pen = ThinPen(1)
            top = crossings(group, hi - 5) * sx + dx
            pen.stroke((top[0], hi - 10), (top[-1], hi - 10), width=20, aspect=1)
            if child == "I":
                pen.stroke((x, 0), (x, hi), width=24, aspect=1)
                pen.stroke((l * sx + dx, 10), (r * sx + dx, 10), width=20, aspect=1)
            else:
                end = l * sx + dx + 8
                mid = end + 0.50 * (x - end)
                y = lo + 10
                pen.stroke(
                    (x, hi),
                    (x, 175),
                    (x, 68, mid + 0.50 * (x - mid), y, mid, y),
                    (mid - 0.45 * (mid - end), y, end + 16, y + 23, end, y + 52),
                    width=24,
                    aspect=0.88,
                )
            path = pen.shape
        paths.append(path)
    left, right = paths
    gap = min(
        (
            b.min() - a.max()
            for y in (2, 10, 35, 62, 120, 240, 420, 500, 645)
            for a, b in [(crossings(left, y), crossings(right, y))]
            if len(a) and len(b)
        ),
        default=20,
    )
    target = 43 if name == "IJ" and w == 900 and not design.slant else 23
    shift = max(0, (target - gap) / 2)
    out = left.transform(1, 0, 0, 1, -shift, 0)
    out.addPath(right.transform(1, 0, 0, 1, shift, 0))
    return out


def grouped_pair(design, name, native, w, d, sx, dx):
    a, b = PAIRS[name]
    rings = sorted(native.contours, key=lambda p: (p.bounds[0] + p.bounds[2]) / 2)
    na = design.regular["glyf"][a].numberOfContours
    first, second = rings[:na], rings[na:]
    if not first or not second:
        raise ValueError(f"missing component of {name}")
    paths = []
    for child, group in [(a, first), (b, second)]:
        box = (
            min(p.bounds[0] for p in group),
            min(p.bounds[1] for p in group),
            max(p.bounds[2] for p in group),
            max(p.bounds[3] for p in group),
        )
        paths.append(mapped_part(design, child, w, d, box, sx, dx))
    if name in ("ij", "IJ", "uni20A8"):
        # Preserve a strip of white where two letters have to share one cell.
        # Compress only the excess of the inner sidebearings, symmetrically.
        left, right = paths
        if name=="uni20A8" and design.mono and w==900:
            l,lo,left_end,hi=left.bounds
            _,b,r,h=right.bounds
            span=r-l
            split=l+.60*span
            left=fit_box(left,(l,lo,split-10,hi))
            right=fit_box(right,(split+10,b,r,h-.09*(h-b)))
            paths=[left,right]
        gap = right.bounds[0] - left.bounds[2]
        needed = 12 if w == 100 else 17
        if gap < needed:
            mid = (left.bounds[2] + right.bounds[0]) / 2
            paths = [
                fit_box(left, (left.bounds[0], left.bounds[1], mid - needed / 2, left.bounds[3])),
                fit_box(right, (mid + needed / 2, right.bounds[1], right.bounds[2], right.bounds[3])),
            ]
    p = pathops.Path()
    for path in paths:
        p.addPath(path)
    return p


def diagonals(design, name, native, w, d):
    sx, dx = design.transform(name, w, d)
    l, b, r, h = native.bounds
    l, r = l * sx + dx, r * sx + dx
    width = r - l
    t = 24 if w == 100 else min(130, width * (0.205 if name == "w" else 0.29))
    p = ThinPen(1)

    def polygon(points):
        path = pathops.Path()
        pen = path.getPen()
        pen.moveTo(points[0])
        for pt in points[1:]:
            pen.lineTo(pt)
        pen.closePath()
        p.add(path)

    def band(x, y, xx, yy):
        # Horizontal cuts at both ends, constant normal thickness.
        half = 0.5 * t * np.hypot(1, (xx - x) / (yy - y))
        polygon([(x - half, y), (x + half, y), (xx + half, yy), (xx - half, yy)])

    x = lambda u: l + width * u
    if name in ("v", "w"):
        left, right = l + t * 0.50, r - t * 0.50
        if name == "v":
            pts = [(left, h), (x(0.50), 0), (right, h)]
        else:
            pts = [(left, h), (x(0.265), 0), (x(0.50), h * 0.77), (x(0.735), 0), (right, h)]
        # A single outline has one corner at either end of each flat foot.
        # Overlaid bands leave a short collinear seam that blocks the fillet.
        sides = [t*.5*np.hypot(1,(xx-x0)/(yy-y0)) for (x0,y0),(xx,yy) in zip(pts,pts[1:])]
        left_side, right_side = [], []
        for i,(xx,yy) in enumerate(pts):
            if i in (0,len(pts)-1):
                half=sides[0 if i==0 else -1]
                left_side.append((xx-half,yy))
                right_side.append((xx+half,yy))
                continue
            (ax,ay),(cx,cy)=pts[i-1],pts[i+1]
            m1,m2=(xx-ax)/(yy-ay),(cx-xx)/(cy-yy)
            # The inside edges meet above a valley (below a peak). The
            # exterior is clipped at the specified baseline / crown.
            inside_y=(sides[i-1]+sides[i])/(abs(m2-m1))
            valley=yy<ay
            outer_y=yy
            inner_y=yy+(inside_y if valley else -inside_y)
            inner_x=xx+sides[i-1]+m1*(inner_y-yy)
            before=(xx-sides[i-1],outer_y)
            after=(xx+sides[i],outer_y)
            # Walk the top edge left to right, then the underside in reverse.
            left_side.extend([before,after] if not valley else [(inner_x,inner_y)])
            right_side.extend([(inner_x,inner_y)] if not valley else [before,after])
        # The contour follows the upper and lower edges, alternating physical
        # sides of each diagonal at every turn.
        left_side[0],right_side[0]=right_side[0],left_side[0]
        polygon(left_side+right_side[::-1])
    elif name == "x":
        band(l + t * 0.53, 0, r - t * 0.53, h)
        band(r - t * 0.53, 0, l + t * 0.53, h)
    elif name == "z":
        hair = t * 0.88
        diagonal = t
        for _ in range(6):
            diagonal = t * np.hypot(1, (width - diagonal) / (h - 2 * hair))
        polygon(
            [
                (l, 0),
                (r, 0),
                (r, hair),
                (l + diagonal, hair),
                (r, h - hair),
                (r, h),
                (l, h),
                (l, h - hair),
                (r - diagonal, h - hair),
                (l, hair),
            ]
        )
    else:
        joint = x(0.50)
        band(l + t * 0.5, h, joint, 45)
        end = x(.13)
        low = b + .44*t
        slope = (r - t*.5-joint)/(h-45)
        p.stroke(
            (r - t * 0.5, h),
            (joint, 45),
            (joint - 148*slope, -103, end + .22*width, low, end, low),
            (end-.06*width,low,end-.095*width,low+4,end-.115*width,low+11),
            width=t,
            aspect=0.87,
        )
    return p.shape


def eng_letter(design, name, native, w, d):
    if w == 900 and name != "Eng":
        return black_body(design, name, native, d)
    sx, dx = design.transform(name, 400 if design.mono and w==900 else w, d)
    edges = crossings(native, 190)
    left, right = [(edges[i] + edges[i + 1]) * sx / 2 + dx for i in (0, len(edges) - 2)]
    span = right - left
    p = ThinPen(1)
    t = 24 if w==100 else min(135,max(100,(edges[-1]-edges[-2])*1.48))
    high = 700 if name == "Eng" else 520
    p.stroke((left, 0), (left, high), width=t, aspect=1)
    if name == "Eng":
        half = t * 0.48 * np.hypot(1, span / high)
        q = pathops.Path()
        q.moveTo(left - half, high)
        q.lineTo(left + half, high)
        q.lineTo(right + half, 0)
        q.lineTo(right - half, 0)
        q.close()
        p.add(q)
        start = high
    else:
        mid = left + 0.55 * span
        p.stroke(
            (left, 312),
            (left + 0.05 * span, 424, mid - 0.28 * span, 518, mid, 518),
            (mid + 0.25 * span, 518, right, 473, right, 337),
            width=t,
            aspect=0.87,
        )
        start = 338
    end = right - (0.70 if w==900 else .47) * span
    y = native.bounds[1] + .43*t
    p.stroke(
        (right, start),
        (right, -54),
        (right, y+70, right-.13*span, y, right-.37*span, y),
        (right-.48*span, y, end+.07*span, y+9, end, y+(30 if w==900 else 15)),
        width=t,
        aspect=0.86,
    )
    if design.serif:
        p.serif(left, 0)
        if name == "Eng":
            p.serif(left, high, top=True)
            p.serif(right, high, top=True)
        else:
            p.entry(left, high)
    return p.shape


def small_sign(design, name, native, w, d):
    sx, dx = design.transform(name, w, d)
    if w == 900:
        # Grow the component strokes together, tracking the counters at the
        # scale of the miniature. The outer ink keeps its original bearings.
        from sign_masters import black_numeral, to_path

        if name in ("numero", "trademark"):
            groups = sorted(native.contours, key=lambda c: (c.bounds[0] + c.bounds[2]) / 2)
            left = black_body(design, name, groups[0], d)
            lb = groups[0].bounds
            left = fit_box(left, (lb[0] * sx + dx, lb[1], lb[2] * sx + dx, lb[3]))
            whole = pathops.Path()
            for c in groups[1:]:
                whole.addPath(c)
            if name == "numero":
                # Its small oval and underscore have different optical sizes.
                lower = min(groups[1:], key=lambda c: c.bounds[3])
                oval = pathops.Path()
                for c in groups[1:]:
                    if c is not lower:
                        oval.addPath(c)
                right = to_path(black_numeral(name, outlined(oval), sx, dx))
                l, b, r, h = lower.bounds
                bar = ThinPen(1)
                bar.stroke(
                    (l * sx + dx, (b + h) / 2), (r * sx + dx, (b + h) / 2), width=(h - b) * 1.30, aspect=1
                )
                right.addPath(bar.shape)
            else:
                right = to_path(black_numeral(name, outlined(whole), sx, dx))
            shift = max(0, 16 + left.bounds[2] - right.bounds[0]) / 2
            left = left.transform(1, 0, 0, 1, -shift, 0)
            left.addPath(right.transform(1, 0, 0, 1, shift, 0))
            return left
        return to_path(black_numeral(name, outlined(native), sx, dx))
    contours = sorted(native.contours, key=lambda c: c.bounds[0])
    if name.startswith("ord"):
        import junction_drawings
        from sign_masters import to_path

        return to_path(
            junction_drawings.thin(
                name, outlined(native), sx, dx, design.serif, design.mono, bool(design.slant)
            )
        )
    p = ThinPen(1)
    if name == "numero":
        body = max(contours, key=lambda c: c.bounds[3] - c.bounds[1])
        l, b, r, h = body.bounds
        a, z = l * sx + dx + 10, r * sx + dx - 10
        p.stroke((a, b), (a, h), (z, b), (z, h), width=20, aspect=0.85)
        # Select by vertical position rather than relying on contour winding.
        bar = min(contours, key=lambda c: c.bounds[3])
        ring = max((c for c in contours if c.bounds[1] > 400), key=lambda c: c.area)
        l, b, r, h = ring.bounds
        nib = Nib((l * sx + dx, b, r * sx + dx, h), 17)
        nib.loop(0.5, 0.5, 0.47, 0.47)
        p.add(nib.pen.shape)
        l, b, r, h = bar.bounds
        p.stroke((l * sx + dx, (b + h) / 2), (r * sx + dx, (b + h) / 2), width=16, aspect=1)
    else:
        t, m = contours
        for form, kind in [(t, "T"), (m, "M")]:
            l, b, r, h = form.bounds
            l, r = l * sx + dx, r * sx + dx
            if kind == "T":
                p.stroke((l, h - 8), (r, h - 8), width=16, aspect=1)
                p.stroke(((l + r) / 2, b), ((l + r) / 2, h - 6), width=19, aspect=1)
            else:
                a, z = l + 10, r - 10
                p.stroke((a, b), (a, h - 9), ((a + z) / 2, b + 10), (z, h - 9), (z, b), width=19, aspect=0.85)
    return p.shape


def bowls(design, name, native, w, d):
    sx, dx = design.transform(name, w, d)
    l, b, r, h = native.bounds
    l, r = l * sx + dx, r * sx + dx
    if w == 900:
        return black_body(design, name, native, d)
    p = ThinPen(1)
    ink = 24
    if name in ("g", "q"):
        # Measure the two uprights in the regular bowl to preserve the
        # relation between the counter, the descender and the outside edge.
        cuts = crossings(native, 245)
        right = (cuts[-2] + cuts[-1]) * sx / 2 + dx
        left = l + 12
        s = right - left
        x = lambda u: left + u * s
        p.stroke(
            (right, 357),
            (right, 418, x(0.79), 519, x(0.49), 519),
            (x(0.198), 519, left, 412, left, 261),
            (left, 114, x(0.18), 2, x(0.46), 2),
            (x(0.73), 2, right, 105, right, 179),
            width=ink,
            aspect=0.79,
        )
        if name == "g":
            bottom = b + 10
            p.stroke(
                (right, 520),
                (right, -27),
                (right, -151, x(0.75), bottom, x(0.48), bottom),
                (x(0.33), bottom, x(0.16), bottom + 15, x(0.07), bottom + 43),
                width=ink,
                aspect=0.84,
            )
        else:
            p.stroke((right, 520), (right, b), width=ink, aspect=1)
            if design.serif:
                p.serif(right, b)
                p.serif(right, 520, top=True, left=0.12)
    elif name == "eth":
        box = (l, b, r, h)
        n = Nib(box, 24)
        n.stroke(
            (0.29, 0.99),
            (0.61, 0.863, 0.966, 0.595, 0.965, 0.347),
            (0.965, 0.154, 0.775, 0.017, 0.507, 0.017),
            (0.223, 0.017, 0.034, 0.154, 0.034, 0.312),
            (0.034, 0.473, 0.206, 0.603, 0.463, 0.603),
            (0.715, 0.603, 0.913, 0.49, 0.965, 0.347),
            aspect=0.86,
        )
        n.stroke((0.265, 0.759), (0.784, 0.909), ratio=0.85)
        p = n.pen
    else:
        n = Nib((l, b, r, h), 24)
        # Both S curves follow the same tilted spine around the open eye.
        n.stroke(
            (0.91, 0.89),
            (0.79, 0.955, 0.68, 0.982, 0.50, 0.982),
            (0.275, 0.982, 0.105, 0.904, 0.105, 0.803),
            (0.105, 0.735, 0.224, 0.692, 0.365, 0.653),
            (0.60, 0.586, 0.916, 0.535, 0.916, 0.435),
            (0.916, 0.385, 0.817, 0.349, 0.635, 0.321),
            aspect=0.89,
        )
        n.stroke(
            (0.365, 0.653),
            (0.180, 0.623, 0.084, 0.582, 0.084, 0.527),
            (0.084, 0.439, 0.41, 0.386, 0.635, 0.321),
            (0.792, 0.276, 0.896, 0.228, 0.896, 0.164),
            (0.896, 0.074, 0.72, 0.017, 0.515, 0.017),
            (0.33, 0.017, 0.193, 0.054, 0.09, 0.109),
            aspect=0.89,
        )
        p = n.pen
    return p.shape


def money(design, name, native, w, d):
    sx, dx = design.transform(name, w, d)
    if w == 900:
        return black_body(design, name, native, d)
    l, b, r, h = native.bounds
    p = ThinPen(1)
    if name == "yen":
        low = crossings(native, b + 30).mean() * sx + dx
        h0 = 323
        outer = crossings(native, h - 2)
        left = (outer[0] + outer[1]) * sx / 2 + dx
        right = (outer[-2] + outer[-1]) * sx / 2 + dx
        p.ribbon((low,h0),(left,h),23,head=design.serif)
        p.ribbon((low,h0),(right,h),23,head=design.serif)
        p.stroke((low, h0), (low, b), width=24, aspect=1)
        midlines = []
        for y in range(60, 367, 4):
            row = crossings(native, y)
            if len(row) == 2 and row[-1] - row[0] > (r - l) * 0.40:
                midlines.append(y)
        for ys in np.split(midlines, np.where(np.diff(midlines) > 4)[0] + 1):
            if not len(ys):
                continue
            row = crossings(native, ys.mean())
            p.stroke((row[0] * sx + dx, ys.mean()), (row[-1] * sx + dx, ys.mean()), width=21, aspect=1)
        if design.serif:
            p.serif(low, b)

    else:
        child = "S" if name == "dollar" else "c"
        nativechild = as_path(design.regular.getGlyphSet(), child, (1, 0, -design.slant, 1, 0, 0))
        a, lo, z, hi = nativechild.bounds
        p.add(mapped_part(design, child, w, d, (l, lo, r, hi), sx, dx))
        x = crossings(native, h - 3).mean() * sx + dx
        p.stroke((x, b), (x, h), width=18 if design.serif else 21, aspect=1)
    return p.shape


def draw(design, name, native, w, d):
    sx, dx = design.transform(name, w, d)
    p = ThinPen(1)
    if name == "B":
        from bowl_drawings import capital_b
        l,b,r,h = native.bounds
        if design.mono and w==900:
            sx,dx=design.transform(name,400,d)
        return capital_b((l*sx+dx,b,r*sx+dx,h),w)
    if name in ("F","I"):
        if w==900:
            return black_body(design,name,native,d)
        l,b,r,h=native.bounds
        l,r=l*sx+dx,r*sx+dx
        x=crossings(native,145)[:2].mean()*sx+dx
        p.stroke((x,b),(x,h),width=24,aspect=1)
        serif_reach=min(2.7,max(1,(x-l-12)/24))
        p.serif(x,b,left=serif_reach,right=serif_reach)
        p.serif(x,h,top=True,left=serif_reach,right=serif_reach if name=="I" else 0)
        if name=="F":
            # Short vertical hairlines bracket the level, constant-width arms.
            for y,end,upper in [(h-8,r,True),(369,l+.88*(r-l),False)]:
                p.stroke((x,y),(end,y),width=16,aspect=1)
                p.stroke((end-6,y+8 if upper else y+30),(end-6,y-36),width=12,aspect=1)
        return p.shape
    if name in BOWLS:
        return bowls(design, name, native, w, d)
    if name in MONEY:
        return money(design, name, native, w, d)
    if name in JOINED:
        if w == 900:
            if name == "uni20B1":
                left, bottom, right, top = native.bounds
                if design.mono:
                    sx,dx=design.transform(name,400,d)
                left, right = left * sx + dx, right * sx + dx
                span = right - left
                stem = min(164, span * 0.26)
                shaft = left + 0.19 * span
                shoulder = left + 0.55 * span
                outer = right - stem * 0.69
                crown = top - 44
                floor = 300
                p.stroke((shaft, bottom), (shaft, top), width=stem, aspect=1)
                p.stroke(
                    (shaft - stem / 2, crown),
                    (shoulder, crown),
                    (shoulder + 0.19 * span, crown, outer, 620, outer, 505),
                    (outer, 399, shoulder + 0.19 * span, floor, shoulder, floor),
                    (shaft, floor),
                    width=stem,
                    aspect=88 / stem,
                )
                for y in (435, 551):
                    p.stroke((left, y), (right, y), width=67, aspect=1)
                if design.serif:
                    p.serif(shaft, bottom, stem / 2)
                return p.shape
            if name in ("germandbls", "Germandbls"):
                import mono_heavy

                if design.mono:
                    from sign_masters import to_path

                    return to_path(mono_heavy.draw(design, name, outlined(native), d))
                left, _, right, _ = native.bounds
                left, right = left * sx + dx, right * sx + dx
                stem = min(124, (right - left) * 0.265)
                return mono_heavy.sharp_s(left, right, stem, stem * 0.76, name == "Germandbls")
            return black_body(design, name, native, d)
        if name=="uni20AD" and design.serif:
            l,b,r,h=native.bounds
            l,r=l*sx+dx,r*sx+dx
            shaft=crossings(native,110)[:2].mean()*sx+dx
            span=r-shaft
            join=349
            top=shaft+.90*span
            slope=(top-shaft)/(h-join)
            knee_y=join+86
            knee=shaft+slope*(knee_y-join)
            p.ribbon((shaft,b),(shaft,h),24,head=True,foot=True)
            p.ribbon((shaft,join),(top,h),19,head=True,start_cut=0)
            p.ribbon((knee,knee_y),(r-21,b),24,foot=True,start_cut=slope)
            p.stroke((l,join),(r,join),width=19,aspect=1)
            return p.shape
        import junction_drawings
        from sign_masters import to_path

        return to_path(
            junction_drawings.thin(
                name, outlined(native), sx, dx, design.serif, design.mono, bool(design.slant)
            )
        )
    if name in DIAGONAL:
        return diagonals(design, name, native, w, d)
    if name in ("Eng", "eng"):
        return eng_letter(design, name, native, w, d)
    if name in SMALL:
        return small_sign(design, name, native, w, d)
    if name in STEMS:
        if w == 900:
            return black_body(design, name, native, d)
        return stems(design, name, native, w, d)
    if design.mono and name in ("ij", "IJ"):
        return mono_pair(design, name, native, w, d)
    if name in PAIRS:
        return grouped_pair(design, name, native, w, d, sx, dx)
    if name == "uni212E" and w == 100:
        l,b,r,t = native.bounds
        estimated(p,(l*sx+dx,b,r*sx+dx,t))
        return p.shape
    if name in DERIVED:
        return mapped_part(design, DERIVED[name], w, d, native.bounds, sx, dx, name == "partialdiff")
    if name in SLASHED:
        child = SLASHED[name]
        body = component(design, child, w, d)
        base_x = crossings(body, 225)[:2].mean()
        reference_x = crossings(native, 225)[:2].mean()
        p.add(body.transform(1, 0, 0, 1, reference_x * sx + dx - base_x, 0))
        # Locate the two exposed end cuts of the original diagonal. Keep
        # their midpoints and redraw a single stroke through the upright.
        caps = []
        for ring in outlined(native):
            for a, _, _, z in ring.pieces:
                if (
                    180 < min(a.imag, z.imag)
                    and max(a.imag, z.imag) < 560
                    and (z - a).real * (z - a).imag < 0
                    and abs(z - a) > 13
                ):
                    caps.append((a + z) / 2)
        a, z = min(caps, key=lambda k: k.real), max(caps, key=lambda k: k.real)
        p.stroke(
            (a.real * sx + dx, a.imag), (z.real * sx + dx, z.imag), width=20 if w == 100 else 76, aspect=1
        )
        return p.shape
    if name in DOTTED:
        body, dot = sorted(native.contours, key=lambda c: abs(c.area), reverse=True)
        p.add(mapped_part(design, DOTTED[name], w, d, body.bounds, sx, dx))
        l, b, r, t = dot.bounds
        rad = 19 if w == 100 else 0.59 * (t - b)
        p.drop((l + r) * sx / 2 + dx, (b + t) / 2, rad, rad)
        return p.shape
    if name in PUNCT:
        body, dot = sorted(native.contours, key=lambda c: c.bounds[3] - c.bounds[1], reverse=True)
        l, b, r, t = body.bounds
        x = (l + r) * sx / 2 + dx
        if name.startswith("exclam"):
            # Keep the optical taper, and keep the end facing the dot flat.
            ink = 24 if w == 100 else 128
            widths = (0.40 * ink, 0.50 * ink) if name == "exclam" else (0.50 * ink, 0.40 * ink)
            ab, at = widths
            q = p.shape
            q.moveTo(x - ab, b)
            q.lineTo(x - at, t)
            q.lineTo(x + at, t)
            q.lineTo(x + ab, b)
            q.close()
        else:
            up = name == "question"
            h = t - b

            def pt(x, y):
                return (l + (r - l) * (x if up else 1 - x)) * sx + dx, b + h * (y if up else 1 - y)

            def seg(*a):
                return sum((pt(x, y) for x, y in zip(a[::2], a[1::2])), ())

            ink = 24 if w == 100 else min(117, (r - l) * sx * 0.36)
            p.stroke(
                pt(0.04, 0.78),
                seg(0.15, 0.90, 0.29, 0.97, 0.49, 0.97),
                seg(0.75, 0.97, 0.95, 0.83, 0.95, 0.64),
                seg(0.95, 0.45, 0.77, 0.39, 0.60, 0.27),
                seg(0.51, 0.20, 0.485, 0.14, 0.485, 0.09),
                seg(0.485, 0.015),
                width=ink,
                aspect=0.87,
            )
        l, b, r, t = dot.bounds
        rad = 20 if w == 100 else 67
        p.drop((l + r) * sx / 2 + dx, (b + t) / 2, rad, rad)
        return p.shape
    child = (BARRED | CURRENCIES)[name]
    base = component(design, child, w, d)
    l,b,r,t = base.bounds
    if w == 100 and name in ("Eth","Dcroat") and not design.serif:
        base=thin_d((l,b,r,t))
    if w == 100 and name == "uni20B2":
        thin_g(p,(l,b,r,t))
    elif w == 100 and name == "uni20BF":
        # The two bowls share one waist rail. The serif face also carries
        # its stem brackets into the currency drawing.
        thin_bitcoin(p,(l,b,r,t))
        if design.serif:
            p.serif(l+12,b)
            p.serif(l+12,t,top=True)
    else:
        p.add(base)
    ink = 21 if w == 100 else 94
    if name in BARRED:
        y = {"hbar": 590, "tbar": 270, "Tbar": 368, "dcroat": 588, "Dcroat": 355, "Eth": 355, "Hbar": 568}[
            name
        ]
        edge = crossings(native, y)
        if name in ("Dcroat", "Eth"):
            edge = edge[:2]
        if name == "Hbar":
            # The upper cross-stroke clears both uprights.
            edge = np.array(native.bounds)[[0, 2]]
        x0, x1 = edge[0] * sx + dx, edge[-1] * sx + dx
        p.stroke((x0, y), (x1, y), width=ink, aspect=1)
    elif name == "uni20AB":
        bar = min(native.contours, key=lambda c: c.bounds[3])
        l, b, r, t = bar.bounds
        p.stroke((l * sx + dx, (b + t) / 2), (r * sx + dx, (b + t) / 2), width=ink, aspect=1)
    else:
        l, b, r, t = base.bounds
        if name == "uni20BF":
            for frac in (0.36, 0.62):
                x = l + (r - l) * frac
                for y, z in [(-110, 21), (679, 810)]:
                    p.stroke((x, y), (x, z), width=ink * 0.70, aspect=1)
        else:
            fractions = (0.40, 0.64) if name == "uni20A1" else (0.47,) if name == "uni0E3F" else (0.52,)
            for frac in fractions:
                x = l + (r - l) * frac
                if name == "uni20B2":
                    # The right-hand counter is bounded by G's shelf. Extend
                    # the shaft into that shelf at every width and weight.
                    edges = [
                        (a, c)
                        for ring in outlined(base)
                        for a, _, _, c in ring.pieces
                        if 280 < a.imag < 420 and abs(c.imag - a.imag) < 4 and abs(c.real - a.real) > 28
                    ]
                    if w == 100:
                        start = l + 12 + .55*(r-l-24)
                        x = start - ink if len(list(native.contours)) == 2 else start + ink
                    elif edges:
                        start = min(min(a.real, c.real) for a, c in edges)
                        x = (
                            min(x, start - ink * 0.68)
                            if len(list(native.contours)) == 2
                            else max(x, start + ink * 0.35)
                        )
                rise = (r - l) * 0.45 if name == "uni20A1" else 0
                p.stroke((x - rise / 2, -110), (x + rise / 2, 810), width=ink * 0.7, aspect=1)
    return p.shape


def slashed_l_tracks(design, name, cells):
    """Keep the slash straight while the letter's shaft and hook interpolate."""
    from reviewed_capitals import rounded
    upright=(1,0,-design.slant,1,0,0)
    native=as_path(design.regular.getGlyphSet(),name,upright)
    base=as_path(design.regular.getGlyphSet(),"l",upright)
    shift=(crossings(native,140)-crossings(base,140)).mean()
    caps=[(a,b) for ring in outlined(native) for a,_,_,b in ring.pieces
          if 180<min(a.imag,b.imag) and max(a.imag,b.imag)<560
          and (a-b).real*(a-b).imag<0 and abs(a-b)>13]
    caps.sort(key=lambda cap:(cap[0]+cap[1]).real)
    glyph,tuples=base_masters(design,"l")
    tracks=[]
    for w,d in cells:
        sx,dx=design.transform(name,w,d)
        ux,off=design.transform("l",w,d)
        for rad in (0,100):
            loc=normalizeLocation(dict(wght=w,wdth=d,RADI=rad),AXES)
            xy=np.array(glyph.coordinates,dtype=float)
            for var in tuples:
                k=supportScalar(loc,var.axes)
                if k: xy+=k*np.asarray(var.coordinates[:-4])
            xy[:,0]=((xy[:,0]-design.slant*xy[:,1]-off)/ux+shift)*sx+dx
            parts=quadratic_parts(glyph,xy)
            ends=[(a.real*sx+dx+1j*a.imag,b.real*sx+dx+1j*b.imag) for a,b in caps]
            centers=[(a+b)/2 for a,b in ends]
            axis=centers[1]-centers[0]
            normal=1j*axis/abs(axis)
            if w!=400:
                half=10 if w==100 else 39
                ends=[(c-half*normal,c+half*normal) for c in centers]
            pts=np.array([z for cap in ends for z in cap])
            pts=pts[np.argsort(-np.angle(pts-pts.mean()))]
            bar=rounded(pts,{100:4,400:10,900:16}[w] if rad else 0)
            parts.append(np.column_stack((bar.real,bar.imag)))
            coords=np.vstack(parts)
            tracks.append(coords[:,0]+design.slant*coords[:,1]+1j*coords[:,1])
    return tracks,(np.cumsum([len(part) for part in parts])-1).tolist()
