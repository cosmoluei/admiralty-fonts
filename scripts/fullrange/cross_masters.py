"""Keep opposite arms of a cross on the same physical rail, including Serif brackets."""

import numpy as np
from scipy.spatial import cKDTree
from fontTools.pens.transformPen import TransformPen

from compatible import Contour, OutlinePen, Profile, compatible_points, cubic


def section(vertices, y):
    end = np.roll(vertices, -1)
    active = (vertices.imag > y) != (end.imag > y)
    p, q = vertices[active], end[active]
    return np.sort(p.real + (y - p.imag) * (q.real - p.real) / (q.imag - p.imag))


class Cross:
    def __init__(self, ring, sign):
        self.ring = ring
        self.nodes = z = ring.pieces[:, 0]
        self.low, self.high = z.imag.min(), z.imag.max()
        self.mid = (self.low + self.high) / 2
        self.cx = (z.real.min() + z.real.max()) / 2
        self.sign = sign
        span = self.high - self.low
        ys = self.low + span * np.array([0.22, 0.25, 0.28, 0.72, 0.75, 0.78])
        rows = np.array([section(z, y) for y in ys])
        centers = (rows[:, ::2] + rows[:, 1::2]) / 2
        widths = rows[:, 1::2] - rows[:, ::2]
        centers[3:] = centers[3:, ::-1]
        widths[3:] = widths[3:, ::-1]
        self.slopes, self.intercepts = np.polyfit(ys, centers, 1)
        self.half = np.median(widths, axis=0) / 2
        self.arm = np.where((z.real < self.cx) == (z.imag < self.mid), 0, 1)
        self.middle = abs(z.imag - self.mid) < span * 0.20
        self.sides = np.sign(z.real[:, None] - z.imag[:, None] * self.slopes - self.intercepts)
        self.tips = {}
        if sign:
            for arm in range(2):
                for high in (False, True):
                    sel = (~self.middle) & (self.arm == arm) & ((z.imag > self.mid) == high)
                    self.tips[arm, high] = z[sel].mean()

    def targets(self, weight, scale, shift):
        k = self.slopes * scale
        b = self.intercepts * scale + shift
        regular = self.half / np.hypot(1, self.slopes)
        physical = (
            np.full(2, 10.5 if self.sign else 12.0)
            if weight == 100
            else regular * (1.45 if weight == 900 else 1.0)
        )
        half = physical * np.hypot(1, k)
        target = []
        for i, z in enumerate(self.nodes):
            if self.middle[i]:
                # Re-entrant vertices are the intersections of two physical
                # edges. All four arms use these very same two line equations.
                edge = b + self.sides[i] * half
                y = (edge[1] - edge[0]) / (k[0] - k[1])
                x = edge[0] + k[0] * y
            else:
                arm = self.arm[i]
                sign = self.sides[i, arm]
                if self.sign:
                    tip = self.tips[arm, z.imag > self.mid]
                    normal = (1 - 1j * k[arm]) / np.hypot(1, k[arm])
                    new = tip.real * scale + shift + 1j * tip.imag + sign * normal * physical[arm]
                    x, y = new.real, new.imag
                else:
                    y = z.imag
                    old = z.real - self.intercepts[arm] - self.slopes[arm] * y
                    # Carry the outer brackets with the stroke. The straight
                    # part of either side stays on its rail up to the bracket.
                    e = self.half[arm]
                    if abs(abs(old) - e) < 2.5:
                        old = sign * e
                    inside = np.clip(old, -e, e)
                    x = b[arm] + k[arm] * y + inside * half[arm] / e + (old - inside) * scale**0.38
            target.append(x + 1j * y)
        return np.array(target)


def multiply_tracks(design, name, cells):
    pen = OutlinePen(None)
    design.regular.getGlyphSet()[name].draw(TransformPen(pen,(1,0,-design.slant,1,0,0)))
    original = pen.contours[0]
    cross = Cross(original,True)
    profiles=[]
    for w,d in cells:
        scale,shift=design.transform(name,w,d)
        nodes=original.pieces[:,0] if (w,d)==(400,100) else cross.targets(w,scale,shift)
        nodes=nodes+design.slant*nodes.imag
        end=np.roll(nodes,-1)
        ring=Contour(np.column_stack((nodes,(2*nodes+end)/3,(nodes+2*end)/3,end)))
        for radius in (0,{100:6,400:21,900:34}[w]):
            profiles.append(Profile(ring,original.knots,ring.knots,radius))
    rows=list(map(np.asarray,compatible_points(profiles,.16)))
    return rows,[len(rows[0])-1]


def cross_tracks(design, name, cells, tracks):
    from serif_letters import retension

    p = OutlinePen(None)
    design.regular.getGlyphSet()[name].draw(TransformPen(p, (1, 0, -design.slant, 1, 0, 0)))
    ring = p.contours[0]
    cross = Cross(ring, name == "multiply")
    # Sample each native segment at the exported grid resolution. Project
    # existing control points onto it to retain their material correspondence
    # and the approved Thin Serif outline exactly.
    index = np.concatenate(
        [np.full(max(3, int(np.ceil(length * 3))), i) for i, length in enumerate(np.diff(ring.breaks))]
    )
    ts = np.concatenate(
        [np.linspace(0, 1, max(3, int(np.ceil(length * 3)))) for length in np.diff(ring.breaks)]
    )
    positions = cubic(ring.pieces[index], ts)
    tree = cKDTree(np.column_stack((positions.real, positions.imag)))
    plain = [z - design.slant * z.imag for z in tracks[:2]]
    nearest = [tree.query(np.column_stack((z.real, z.imag)))[1] for z in plain]
    out = list(tracks)
    for j, (w, d) in enumerate(cells):
        if (w, d) == (400, 100) or w == 100 and design.serif and name != "multiply":
            continue
        sx, dx = design.transform(name, w, d)
        shape = retension(ring.pieces, cross.targets(w, sx, dx), sx)
        dst = cubic(shape.pieces[index], ts)
        delta = dst - (positions.real * sx + dx + 1j * positions.imag)
        for r, (xy, point) in enumerate(zip(plain, nearest)):
            z = xy.real * sx + dx + 1j * xy.imag + delta[point]
            out[2 * j + r] = z + design.slant * z.imag
    return out
