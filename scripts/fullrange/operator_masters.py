"""Design Mono's two-cell programming operators in a shared 1200-unit space."""

import numpy as np
import pathops

from compatible import Profile, compatible_points, OutlinePen

PAIRS = {
    "->": ("hyphen.lig_r", "greater.lig_arrow"),
    "<-": ("less.lig_arrow", "hyphen.lig_l"),
    "==": ("equal.lig_r", "equal.lig_l"),
    "=>": ("equal.lig_r", "greater.lig_fatarrow"),
    "!=": ("exclam.lig_neq", "equal.lig_l"),
    "<=": ("less.lig_le", "equal.lig_le"),
    ">=": ("greater.lig_ge", "equal.lig_ge"),
}


def rings_for(op, cell, weight, width):
    t = {100: 22, 400: 66, 900: 96}[weight]
    sx = np.interp(width, (65, 100, 150), (0.83, 1, 1.085))

    def x(v):
        return 600 + (v - 600) * sx

    def stroke(points, diameter):
        p = pathops.Path()
        p.moveTo(x(points[0][0]), points[0][1])
        for a, b in points[1:]:
            p.lineTo(x(a), b)
        p.stroke(diameter, pathops.LineCap.BUTT_CAP, pathops.LineJoin.BEVEL_JOIN, 4)
        return p

    def rule(left, right, y):
        return stroke([(left, y), (right, y)], t)

    if op in ("<=", ">="):
        a, b = (1090, 103) if op == "<=" else (110, 1097)
        # The same diagonal crosses the cell boundary in both glyphs.
        low = 196 if weight == 900 else 167
        shapes = [stroke([(a, 720 - low), (b, 360), (a, low)], t), rule(97, 1103, 76)]
    elif op in ("==", "!="):
        shapes = [rule(76, 1124, y) for y in (188, 364)]
        if op == "!=":
            shapes.append(stroke([(346, 36), (523 if weight == 900 else 546, 516)], t))
    else:
        mirror = op == "<-"
        xx = lambda a: 1200 - a if mirror else a
        tip = xx(1103)
        wing = xx(861)
        shapes = [stroke([(wing, 491), (tip, 276), (wing, 61)], t)]
        if op == "=>":
            for y in (188, 364):
                shapes.append(rule(76, 1103 - abs(y - 276) * 242 / 215, y))
        else:
            shapes.append(rule(xx(76), tip, 276))
    p = shapes[0]
    for shape in shapes[1:]:
        p = pathops.op(p, shape, pathops.PathOp.UNION)
    clip = pathops.Path()
    start = cell * 600
    clip.moveTo(start, -100)
    clip.lineTo(start + 600, -100)
    clip.lineTo(start + 600, 800)
    clip.lineTo(start, 800)
    clip.close()
    half = pathops.op(p, clip, pathops.PathOp.INTERSECTION).transform(
        1, 0, 0, 1, -start, 0
    )
    half.simplify(clockwise=True)
    pen = OutlinePen(None)
    half.draw(pen)
    return sorted(pen.contours, key=lambda r: r.center.imag)


def round_polygon_reference(points):
    """Round quadratic splits of the native polygon without accumulating one-sided ink error."""
    rounded = np.rint(points.real) + 1j * np.rint(points.imag)

    def area(row):
        a, control = row[::2], row[1::2]
        b = np.roll(a, -1)
        return (
            np.imag(np.vdot(a, control) + np.vdot(control, b) + 0.5 * np.vdot(a, b)) / 3
        )

    error = area(points) - area(rounded)
    a = rounded[::2]
    chord = np.roll(a, -1) - a
    # Only the quadratic controls of split edges may move. Corners and
    # aligned seams keep exactly the same coordinates as the source.
    candidates = []
    for dim in (1, 1j):
        remainder = ((points[1::2] - rounded[1::2]) * dim.conjugate()).real
        for i in np.flatnonzero(abs(remainder) > 1e-6):
            step = dim * np.sign(remainder[i])
            gain = (step.conjugate() * chord[i]).imag / 3
            candidates.append((gain, 2 * i + 1, step))
    for gain, index, step in sorted(candidates, key=lambda item: -abs(item[0])):
        if abs(error - gain) < abs(error):
            rounded[index] += step
            error -= gain
    return rounded


def operator_tracks(design, name, cells):
    from thin_figures import register_figure
    from compatible import ordered_contours
    from fontTools.pens.transformPen import TransformPen

    op, cell = next((s, pair.index(name)) for s, pair in PAIRS.items() if name in pair)
    # Italic cells meet at x=600+slant*(y-260), as in the release.
    shift = design.slant * 260
    p = OutlinePen(None)
    design.regular.getGlyphSet()[name].draw(
        TransformPen(p, (1, 0, -design.slant, 1, shift, 0))
    )
    ref = p.contours
    groups = [[] for ring in ref]
    for w, d in cells:
        native = (w, d) == (400, 100)
        rings = ref if native else ordered_contours(ref, rings_for(op, cell, w, d))
        for orig, cur, group in zip(ref, rings, groups):
            # The clip edges are permanent landmarks. Register their two
            # ends before fitting the rest of the arm.
            seam = 600 * (1 - cell)

            def register_at_seam(r):
                nodes = r.pieces[:, 0]
                ends = np.roll(nodes, -1)
                hits = np.flatnonzero(
                    (abs(nodes.real - seam) < 1.1)
                    & (abs(ends.real - seam) < 1.1)
                    & (abs(ends.imag - nodes.imag) > 3)
                )
                return r.roll(int(hits[nodes[hits].imag.argmin()])) if len(hits) else r

            orig = register_at_seam(orig)
            cur = register_at_seam(cur)
            if len(orig.pieces) == len(cur.pieces):
                a, b = orig.knots, cur.knots
            else:
                cur, a, b = register_figure(orig, cur)
            for rad in (0, {100: 3, 400: 8, 900: 12}[w]):
                pro = Profile(cur, a, b, rad)
                pro.fillets = [
                    f
                    for f in pro.fillets
                    if abs(cur.eval(np.array([f[0]]))[0].real - seam) > 1.1
                ]
                group.append(pro)
    out = [[] for _ in range(2 * len(cells))]
    ends = []
    for group in groups:
        for idx, (row, z) in enumerate(
            zip(out, compatible_points(group, 0.12, compact=0.12))
        ):
            points = z + design.slant * z.imag - shift
            if cells[idx // 2] == (400, 100) and idx % 2 == 0:
                points = round_polygon_reference(points)
            row.extend(points)
        ends.append(len(out[0]) - 1)
    return list(map(np.asarray, out)), ends
