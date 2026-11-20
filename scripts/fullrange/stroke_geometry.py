"""Draw parallel edges of a smooth centreline. Coordinates are in design units."""
from bisect import bisect_right
from math import atan2, comb, radians, tan

import pathops
from fontTools.pens.recordingPen import RecordingPen
from fontTools.misc.bezierTools import splitCubicAtTC


def dot(a, b):
    return (a.conjugate() * b).real


def cross(a, b):
    return (a.conjugate() * b).imag


def unit(v):
    return v / abs(v)


def bezier(points, t):
    n = len(points) - 1
    return sum(comb(n, j) * (1 - t) ** (n - j) * t ** j * p for j, p in enumerate(points))


def derivative(points):
    degree = len(points) - 1
    return tuple(degree * (b - a) for a, b in zip(points, points[1:]))


def curvature(velocity, acceleration):
    return cross(velocity, acceleration) / abs(velocity) ** 3


class Curve:
    def __init__(self, points):
        self.points = tuple(points)
        self.velocity = derivative(self.points)
        self.acceleration = derivative(self.velocity) if len(self.velocity) > 1 else (0j,)

    def boundary(self, t, offset):
        position = bezier(self.points, t)
        velocity = bezier(self.velocity, t)
        bend = curvature(velocity, bezier(self.acceleration, t))
        return position + 1j * unit(velocity) * offset, velocity * (1 - offset * bend)


def fair_curves(pieces):
    """Join with a shared tangent and signed curvature, including zero curvature at a straight."""
    curves = [list(points) for points in pieces]
    for a, b in zip(curves, curves[1:]):
        incoming, outgoing = a[-1] - a[-2], b[1] - b[0]
        if len(a) == 2:
            tangent = unit(incoming)
        elif len(b) == 2:
            tangent = unit(outgoing)
        else:
            tangent = unit(unit(incoming) + unit(outgoing))
        if len(a) == 4:
            a[-2] = a[-1] - tangent * abs(incoming)
        if len(b) == 4:
            b[1] = b[0] + tangent * abs(outgoing)
    joins = []
    for a, b in zip(curves, curves[1:]):
        if len(a) == 2 or len(b) == 2:
            joins.append(0.)
        else:
            ka = curvature(3*(a[3]-a[2]), 6*(a[3]-2*a[2]+a[1]))
            kb = curvature(3*(b[1]-b[0]), 6*(b[2]-2*b[1]+b[0]))
            joins.append(2 * ka * kb / (ka + kb) if ka * kb > 0 else 0.)

    result = []
    for i, c in enumerate(curves):
        if len(c) == 2:
            result.append(Curve(c))
            continue
        result.append(quintic(c, joins[i-1] if i else None, joins[i] if i < len(joins) else None))
    return result


def quintic(cubic, k_start, k_end):
    # Degree elevation leaves an independent curvature handle at each end.
    a, b, c, d = cubic
    q = [a, .4*a+.6*b, .1*a+.6*b+.3*c, .3*b+.6*c+.1*d, .6*c+.4*d, d]
    for pos, origin, v, k in [(2, a, q[1]-a, k_start), (3, d, d-q[4], k_end)]:
        if k is not None:
            normal = 1j * unit(v)
            q[pos] += normal * (1.25 * abs(v)**2 * k - dot(q[pos]-origin,normal))
    return Curve(q)


def fit_edge(curve, radius, a=0., b=1.):
    """Fit a cubic to the actual offset, in glyph space, to 0.025 design units."""
    p, v = curve.boundary(a, radius)
    q, w = curve.boundary(b, radius)
    if len(curve.points) == 2:
        return [(p,q)]
    dt = b-a
    controls = (p, p+v*dt/3, q-w*dt/3, q)
    error = max(abs(bezier(controls,t)-curve.boundary(a+t*dt,radius)[0]) for t in (.25,.5,.75))
    if error <= .025:
        return [controls]
    mid = (a+b)/2
    return fit_edge(curve, radius, a, mid) + fit_edge(curve, radius, mid, b)


def xy(z):
    return z.real, z.imag


def stroke(pieces, thickness):
    curves = fair_curves(pieces)
    left = [c for s in curves for c in fit_edge(s, thickness/2)]
    right = [c for s in curves for c in fit_edge(s, -thickness/2)]
    path = pathops.Path()
    pen = path.getPen()
    pen.moveTo(xy(left[0][0]))
    for side in (left, [c[::-1] for c in reversed(right)]):
        for c in side:
            if len(c) == 2:
                pen.lineTo(xy(c[1]))
            else:
                pen.curveTo(*(xy(z) for z in c[1:]))
        if side is left:
            pen.lineTo(xy(right[-1][-1]))
    pen.closePath()
    return path

def emit(pen, points):
    if len(points) == 2:
        pen.lineTo(xy(points[-1]))
    else:
        pen.curveTo(*(xy(z) for z in points[1:]))


def trim_piece(points, lo, hi):
    if lo == 0 and hi == 1:
        return points
    if len(points) == 2:
        return (bezier(points, lo), bezier(points, hi))
    cuts = [t for t in (lo, hi) if 0 < t < 1]
    return list(splitCubicAtTC(*points, *cuts))[int(lo > 0)]


def round_branches(path, thickness):
    """Blend re-entrant branch seams. Keep the square cuts on stems and terminals."""
    recording = RecordingPen()
    path.draw(recording)
    result = pathops.Path()
    pen = result.getPen()
    for op, pts in recording.value:
        pts = tuple(complex(*pt) for pt in pts)
        if op == "moveTo":
            start = last = pts[0]
            segments = []
        elif op in ("lineTo", "curveTo"):
            segments.append((last, *pts))
            last = pts[-1]
        elif op == "closePath":
            if last != start:
                segments.append((last, start))
            blend_contour(pen, segments, thickness)
    return result


def blend_contour(pen, segments, thickness):
    distances = [0.]
    tables = []
    corners = []
    for i, seg in enumerate(segments):
        a = segments[i-1]
        turn = (a[-1]-a[-2]).conjugate() * (seg[1]-seg[0])
        angle = atan2(turn.imag, turn.real)
        if abs(angle) > radians(1):
            corners.append((distances[-1], angle))
        ts = [j/16 for j in range(17)] if len(seg) == 4 else [0.,1.]
        points = [bezier(seg,t) for t in ts]
        arc = [0.]
        for p, q in zip(points,points[1:]):
            arc.append(arc[-1]+abs(q-p))
        tables.append((ts,arc))
        distances.append(distances[-1]+arc[-1])
    total = distances[-1]

    def position(s):
        s %= total
        i = min(bisect_right(distances,s)-1,len(segments)-1)
        ts, arc = tables[i]
        local = s-distances[i]
        j = min(bisect_right(arc,local)-1,len(arc)-2)
        t = ts[j]+(ts[j+1]-ts[j])*(local-arc[j])/(arc[j+1]-arc[j])
        return i,t

    cuts = []
    for i,(s,angle) in enumerate(corners):
        if angle <= 0 or angle >= radians(175):
            continue
        # Limit the trim by both neighbours. A serif-like spur or a short
        # stem cap must survive even when it sits directly beside a branch.
        # A counter with one corner has a full circuit to either neighbour.
        before = (s-corners[i-1][0]) % total if len(corners) > 1 else total
        after = (corners[(i+1)%len(corners)][0]-s) % total if len(corners) > 1 else total
        reach = min(2.0+.35*thickness*tan(angle/2), .36*before, .36*after, .55*thickness)
        if reach > .04:
            cuts.append((s-reach,s+reach,reach))

    if not cuts:
        pen.moveTo(xy(segments[0][0]))
        for seg in segments:
            emit(pen,seg)
    else:
        for j,(a,b,reach) in enumerate(cuts):
            i0,t0 = position(a)
            i1,t1 = position(b)
            c0,c1 = Curve(segments[i0]),Curve(segments[i1])
            p,v = c0.boundary(t0,0)
            q,w = c1.boundary(t1,0)
            if j == 0:
                pen.moveTo(xy(p))
            k0 = curvature(v,bezier(c0.acceleration,t0))
            k1 = curvature(w,bezier(c1.acceleration,t1))
            handle = .58*reach
            transition = quintic((p,p+unit(v)*handle,q-unit(w)*handle,q),k0,k1)
            for seg in fit_edge(transition,0):
                emit(pen,seg)
            # Emit the untouched span until the next corner, including a wrap.
            end = cuts[(j+1)%len(cuts)][0]
            end_i,end_t = position(end)
            if end_i < i1 or (end_i == i1 and end_t < t1):
                end_i += len(segments)
            for k in range(i1,end_i+1):
                lo = t1 if k == i1 else 0.
                hi = end_t if k == end_i else 1.
                if hi-lo > 1e-8:
                    emit(pen,trim_piece(segments[k%len(segments)],lo,hi))
    pen.closePath()
