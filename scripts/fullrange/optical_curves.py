"""Vary the ink between opposing edges while carrying the release's smooth tangents."""
import math
from functools import cached_property

import numpy as np
import osqp
from scipy import sparse
from scipy.spatial import Delaunay, QhullError
from fontTools.pens.transformPen import TransformPen

from compatible import Contour, OutlinePen, Profile, compatible_points
from optical_master import direction
import thin_figures
import junction_drawings
from straight_masters import COMPARISONS, DIAGONAL, RECTILINEAR, comparison_ring, pi_curve, pi_stations, straight_ring


def scaled(z, scale):
    return z.real*scale + 1j*z.imag


def split_curves(ring):
    pieces = []
    for i, piece in enumerate(ring.pieces):
        a, b, c, d = piece
        bend = abs(a-2*b+c)+abs(b-2*c+d)
        span = ring.breaks[i+1]-ring.breaks[i]
        count = max(1, math.ceil(span/60)) if bend > .1 else 1
        for j in range(count):
            lo, hi = j/count, (j+1)/count
            def point(t):
                return (1-t)**3*a + 3*(1-t)**2*t*b + 3*(1-t)*t*t*c + t**3*d
            def handle(t):
                return ((1-t)**2*(b-a)+2*t*(1-t)*(c-b)+t*t*(d-c))/count
            start, end = point(lo), point(hi)
            pieces.append([start, start+handle(lo), end-handle(hi), end])
    return Contour(pieces)


class BoundaryFit:
    def __init__(self, rings):
        self.rings = [split_curves(r) for r in rings]
        self.pieces = np.concatenate([r.pieces for r in self.rings])
        self.z = self.pieces[:, 0]
        self.sizes = np.cumsum([len(r.pieces) for r in self.rings])
        parts = np.split(np.arange(len(self.z)), self.sizes[:-1])
        self.follow = np.concatenate([np.roll(p, -1) for p in parts])
        self.prior = np.concatenate([np.roll(p, 1) for p in parts])
        self.turn = np.concatenate([r.turns for r in self.rings])
        # A slight kink from a rounded quadratic control point is not a pen lift.
        self.corner = self.turn > math.radians(20)
        self.length = np.maximum(1., np.concatenate([np.diff(r.breaks) for r in self.rings]))
        self.eye = np.eye(len(self.z))
        self.diff = self.eye[self.follow]-self.eye
        a, b, c, d = self.pieces.T
        self.linear = abs(a-2*b+c)+abs(b-2*c+d) < .01

    @cached_property
    def rays(self):
        a, b, c, d = self.pieces.T
        # The same material samples and interpolation weights address all widths.
        count = np.maximum(1, np.ceil(self.length/12).astype(int))
        seg = np.repeat(np.arange(len(a)), count)
        t = np.concatenate([np.arange(n)/n for n in count])
        step = 1/count[seg]
        def source(u):
            return ((1-u)**3*a[seg]+3*u*(1-u)**2*b[seg]+3*u*u*(1-u)*c[seg]+u**3*d[seg])
        p, q = source(t), source(t+step)
        v = q-p
        mid = (p+q)/2
        tangent = direction(v)
        norm = -1j*tangent
        cross0 = ((p[None, :]-mid[:, None])*norm[:, None].conj()).imag
        cross1 = ((q[None, :]-mid[:, None])*norm[:, None].conj()).imag
        hits = (cross0 > 0) != (cross1 > 0)
        f = np.divide(cross0, cross0-cross1, out=np.zeros_like(cross0), where=hits)
        length = ((p[None, :]+v*f-mid[:, None])*norm[:, None].conj()).real
        def paired(sign):
            dist = np.where(hits & (sign*length > 1.3), sign*length, np.inf)
            j = dist.argmin(axis=1)
            i = np.arange(len(j))
            ok = (dist[i, j] < 185) & ((tangent*tangent[j].conj()).real < -.73) & (abs(v) > 1.2)
            i, j = i[ok], j[ok]
            def blend(k, u):
                return self.eye[seg[k]]+(u[:, None])*self.diff[seg[k]]
            first = blend(i, t[i]+.5*step[i])
            second = blend(j, t[j]+f[i, j]*step[j])
            return second-first, dist[i, j], norm[i]*sign, abs(v[i]), (first+second)/2
        return paired(1), paired(-1)

    @cached_property
    def mesh(self):
        # Include points in the interiors of long straight rails: a vertex on
        # another contour may otherwise slip through between two distant ends.
        pts, blends = [], []
        for i, (a, b, c, d) in enumerate(self.pieces):
            t = np.arange(max(1, math.ceil(self.length[i]/18)))/max(1, math.ceil(self.length[i]/18))
            pts.extend((1-t)**3*a+3*(1-t)**2*t*b+3*(1-t)*t*t*c+t**3*d)
            blends.extend(self.eye[i]+t[:, None]*self.diff[i])
        pts = np.asarray(pts)
        blends = np.asarray(blends)
        xy = np.column_stack((pts.real, pts.imag))
        ix = np.unique(np.round(xy, 2), axis=0, return_index=True)[1]
        try:
            tri = ix[Delaunay(xy[ix]).simplices]
        except QhullError:
            tri = np.empty((0, 3), int)
        sides = pts[tri[:, 1:]]-pts[tri[:, :1]]
        ref = np.stack((sides.real, sides.imag), axis=1)
        keep = abs(np.linalg.det(ref)) > .25
        return pts, blends, tri[keep], np.linalg.inv(ref[keep])

    def fit(self, weight, width, scale, shift, serif, name):
        base = scaled(self.z, scale)+shift
        edges = base[self.follow]-base
        along = direction(edges)
        n = len(base)
        ident = self.eye
        shape, target = [], []
        constraints, floors = [], []
        def proj(mat, v):
            return np.hstack([mat*v.real[:, None], mat*v.imag[:, None]])
        def add(mat, t=0, importance=1.):
            importance = np.broadcast_to(importance, (len(mat),))
            shape.append(mat*importance[:, None])
            target.append(np.broadcast_to(t, (len(mat),))*importance)
        for ink, (pairs, original, norm, arcs, center) in zip((True, False), self.rays):
            tangent = norm*1j
            normal = -1j*direction(scaled(tangent, scale))
            effective = original*scale/np.maximum(abs(scaled(tangent, scale)), .0001)
            rows = proj(pairs, normal)
            if ink:
                if weight == 100:
                    # Calibrate a full shaft to t; fine hairlines, and small
                    # figures such as superior numerals, retain their hierarchy.
                    goal = np.clip(24*(original/83)**(.43 if serif else .25), 7, 31)
                elif weight == 900:
                    goal = original+np.minimum(48, original*(.43 if serif else .53))
                else:
                    goal = original*(1+.09*(width/100-1))
                # Inside a branching stroke the normal can hit the far side
                # of the join. Give ordinary, opposed sections precedence.
                add(rows, goal-effective, np.sqrt(arcs/12)*2.5)
                add(proj(center, normal), importance=.17*np.sqrt(arcs/12))
                low = np.minimum(goal*.68, effective*.84)
            else:
                low = np.minimum(19, effective*.53)
            constraints.append(rows)
            floors.append(low-effective)
        xy = np.block([[ident, np.zeros_like(ident)], [np.zeros_like(ident), ident]])
        add(xy, importance=.30)
        # Thin a stroke around its own centreline. Opposing-edge distances
        # alone admit a second solution in which an entire loop shrinks or
        # a disconnected dot slides horizontally toward another component.
        if name not in ('ampersand', 'S', 'germandbls', 'Germandbls'):
            movement = {100: 48., 400: 21., 900: 34.}[weight]
            constraints.extend([xy, -xy])
            floors.extend([np.full(2*n, -movement), np.full(2*n, -movement)])
            bisector = direction(along+along[self.prior])
            add(proj(ident, bisector), importance=np.where(self.corner, .7, 1.6))
            for indices in np.split(np.arange(n), self.sizes[:-1]):
                average = ident[indices].mean(axis=0, keepdims=True)
                add(proj(average, np.ones(1)), importance=4.)
                add(proj(average, 1j*np.ones(1)), importance=4.)
        rails = []
        if weight == 100 and name in ('germandbls', 'Germandbls'):
            # The two long rails of the Eszett form one upright. Pin both
            # ends so that the pressure in its bowl cannot taper the shaft.
            vertical = self.linear & (abs(edges.real) < 2.5) & (abs(edges.imag) > 260)
            rails = np.flatnonzero(vertical)
            if len(rails) == 2:
                rails = rails[np.argsort(base[rails].real)]
                center = base[rails].real.mean()
                for i, x in zip(rails, (center-12, center+12)):
                    ids = [i, self.follow[i]]
                    add(xy[ids], x-base[ids].real, importance=18.)
        # A normal through a branched symbol can land on a different arm.
        # The envelope is a property of the *whole* drawing. Keep the solver
        # from trading hundreds of units of sidebearing for a local width.
        for block, axis, margin in ((xy[:n], base.real, 16), (xy[n:], base.imag, 10)):
            constraints.extend([block, -block])
            floors.extend([axis.min()-margin-axis, axis-axis.max()-margin])
        # Keep straight rails on their axes. A change in the normal offset of
        # a curve is distributed along the whole arc, with a shared tangent.
        strength = np.where(self.linear, 3.8, 1.45)*np.sqrt(36/np.maximum(self.length, 6))
        rail = self.linear & (self.length > 80) & (np.minimum(abs(edges.real), abs(edges.imag)) < 1.5)
        strength[rail] = np.maximum(strength[rail], 18.)
        if np.all(self.linear):
            # Both corners of a cut share its rail. Solve for parallel
            # offset lines, so rectangular arms and diagonal ends cannot
            # turn into wedges when a Thin stem loses most of its ink.
            normals = proj(self.diff, 1j*along)
            constraints.extend([normals, -normals])
            floors.extend([np.full(n, -.08), np.full(n, -.08)])
        elif weight == 100:
            # A Boolean union cuts a single rule into several contour edges.
            # Give co-directed pieces on that line one normal displacement,
            # including edges on different counters. Otherwise each fragment
            # can be internally straight while the full rule has steps.
            straight = np.flatnonzero(self.linear & (self.length > 24))
            for j, i in enumerate(straight):
                others = straight[j+1:]
                normal = 1j * along[i]
                on_line = (abs(along[others]-along[i]) < .012) & (
                    abs(((base[others]-base[i])*normal.conjugate()).real) < 1.1)
                for k in others[on_line]:
                    ends = [self.follow[i], k, self.follow[k]]
                    add(proj(ident[ends]-ident[i], np.full(3, normal)), importance=28.)
        add(proj(self.diff, 1j*along), importance=strength)
        add(proj(self.diff, along), importance=.44*np.sqrt(35/np.maximum(self.length, 5)))
        lengths = np.maximum(5, abs(edges))
        v = self.diff/lengths[:, None]
        bend = (v-v[self.prior])*np.minimum(lengths, lengths[self.prior])[:, None]
        smooth = ~self.corner
        for axis in (np.ones(n), 1j*np.ones(n)):
            add(proj(bend, axis)[smooth], importance=2.6)
        horizontal = self.linear & (abs(edges.imag) < .2)
        heights = np.array([-224, -220, -12, -10, 0, 520, 530, 700, 712, 740, 752])
        key_y = np.min(abs(self.z.imag[:, None]-heights), axis=1) < .6
        # Constrain a flat baseline or cap, while a detached point and both
        # edges of a hairline remain free to move inward.
        pinned = key_y & (horizontal | horizontal[self.prior])
        start = 0
        for ring, end in zip(self.rings, self.sizes):
            ys = self.z[start:end].imag
            if np.ptp(ys) > 170 and ring.area < 0:
                outer = (abs(ys-ys.min()) < .6) | (abs(ys-ys.max()) < .6)
                pinned[start:end] |= outer
            start = end
        add(proj(ident, 1j*np.ones(n))[pinned], importance=8.)
        constraints.append(proj(self.diff, along))
        floors.append(-.76*abs(edges))
        A = np.vstack(shape); rhs = np.concatenate(target)
        P = sparse.csc_matrix(A.T@A)
        C = sparse.csc_matrix(np.vstack(constraints))
        lo = np.concatenate(floors)
        vertices, blends, tri, inv = self.mesh
        for iteration in range(8):
            solver = osqp.OSQP()
            solver.setup(P=P, q=-(A.T@rhs), A=C, l=lo, u=np.full(len(lo), np.inf),
                         verbose=False, eps_abs=.009, eps_rel=.00012, max_iter=15000)
            sol = solver.solve(raise_error=False)
            if sol.info.status_val not in (1, 2):
                raise ArithmeticError(sol.info.status)
            dx, dy = np.split(sol.x, 2)
            delta = dx+1j*dy
            actual = base+delta
            dest = scaled(vertices, scale)+blends@delta
            side = dest[tri[:, 1:]]-dest[tri[:, :1]]
            jac = np.stack((side.real, side.imag), axis=1)@inv
            eig, vec = np.linalg.eigh((jac+jac.transpose(0, 2, 1))/2)
            weak = eig[:, 0] < .092
            if not np.any(weak):
                break
            unit = vec[weak, :, 0]
            coeff = (inv[weak]@unit[:, :, None])[:, :, 0]
            ids = tri[weak]
            difference = blends[ids[:, 1:]]-blends[ids[:, :1]]
            row = np.einsum('ij,ijk->ik', coeff, difference)
            u = unit[:, 0]+1j*unit[:, 1]
            norm = 1/np.maximum(np.linalg.norm(row, axis=1), .00001)
            extra = proj(row*norm[:, None], u)
            floor = (.102-(scaled(u, scale)*u.conj()).real)*norm
            C = sparse.vstack((C, sparse.csc_matrix(extra)), format='csc')
            lo = np.r_[lo, floor]
        if len(rails) == 2:
            # Close the last few units of error from the junction constraints.
            # Carry the adjacent arch with the rail, tapering the correction
            # in space so there is no new joint at the top of the straight.
            sides = []
            for i in rails:
                points = sorted(actual[[i, self.follow[i]]], key=lambda z: z.imag)
                sides.append(np.interp(actual.imag, [z.imag for z in points], [z.real for z in points]))
            left, right = sides
            center = np.mean(actual[np.r_[rails, self.follow[rails]]].real)
            t = np.clip((actual.real-left)/(right-left), 0., 1.)
            blend = t*t*(3-2*t)
            dist = np.maximum(np.maximum(left-actual.real, actual.real-right), 0.)
            dy = np.maximum(actual.imag-max(actual[np.r_[rails, self.follow[rails]]].imag), 0.)
            offset = (1-blend)*(center-12-left)+blend*(center+12-right)
            actual += offset*np.exp(-(dist/54)**2-(dy/80)**2)
        return self.contours(scale, actual)

    def contours(self, scale, points):
        original = scaled(self.pieces, scale)
        delta = points[self.follow]-points
        chord = original[:, 3]-original[:, 0]
        # Rotate endpoint tangents by the shared change of direction at the
        # station. At corners each side receives its own rotation.
        rot = direction(delta/chord)
        joint = direction(rot+rot[self.prior])
        a, b, c, d = original.T
        r0 = np.where(self.corner, rot, joint)
        r1 = np.where(self.corner[self.follow], rot, joint[self.follow])
        t0 = direction(b-a)*r0
        t1 = direction(d-c)*r1
        # Curves meeting a straight take the straight's direction exactly.
        lc = self.linear[self.prior] & ~self.corner
        rc = self.linear[self.follow] & ~self.corner[self.follow]
        t0[lc] = direction(delta[self.prior[lc]])
        t1[rc] = direction(delta[self.follow[rc]])
        ratio = abs(delta)/np.maximum(.01, abs(chord))
        first = points+t0*abs(b-a)*ratio
        last = points[self.follow]-t1*abs(d-c)*ratio
        first[self.linear] = points[self.linear]+delta[self.linear]/3
        last[self.linear] = points[self.linear]+2*delta[self.linear]/3
        cur = np.column_stack([points, first, last, points[self.follow]])
        return [Contour(part) for part in np.split(cur, self.sizes[:-1])]


def round_default(points, target_area):
    """Choose between adjacent grid positions without biasing a long diagonal."""
    z = points.copy()
    rounded = np.rint(z.real)+1j*np.rint(z.imag)
    a, b = rounded[::2], rounded[1::2]
    c = np.roll(a, -1)
    cross = lambda x, y: (x.conj()*y).imag
    area = (cross(a, b)/3+cross(b, c)/3+cross(a, c)/6).sum()
    # An off-curve move has a linear effect on the ink integral. Select only
    # a neighbouring grid value within a single unit of its true position.
    used = np.zeros(len(b), bool)
    options = np.array([-1, 1, -1j, 1j])
    changes = cross(options[None, :], (c-a)[:, None])/3
    while abs(target_area-area) > 12:
        trials = b[:, None]+options
        valid = (abs(trials-z[1::2, None]) < 1.06) & ~used[:, None]
        errors = np.where(valid, abs(target_area-area-changes), np.inf)
        i, j = np.unravel_index(np.argmin(errors), errors.shape)
        if errors[i, j] >= abs(target_area-area)-.01:
            break
        b[i] += options[j]
        area += changes[i, j]
        used[i] = True
    return rounded


def optical_tracks(design, name, cells):
    p = OutlinePen(None)
    design.regular.getGlyphSet()[name].draw(TransformPen(p, (1, 0, -design.slant, 1, 0, 0)))
    model = BoundaryFit(p.contours)
    if name == 'pi':
        ring, station_knots, offset = pi_stations(model.rings[0])
        model.rings = [ring]
    profiles = [[] for r in model.rings]
    consistent_width = (name in {'uni20BE', 'three', 'three.tnum', 'threesuperior', 'uni2083'}
                        or name in junction_drawings.NAMES
                        or name in thin_figures.FIGURES or not design.serif and name in thin_figures.SANS_CAPS)
    if consistent_width:
        sx, dx = design.transform(name, 100, 100)
        nominal = thin_figures.thin_rings(name, model.rings, sx, dx, design.serif, design.mono, bool(design.slant))
        fixed = [thin_figures.register_figure(ref, c) for ref,c in zip(model.rings, nominal)]
    straight = not design.serif and name.split('.')[0] in RECTILINEAR | DIAGONAL and np.all(model.linear)
    for w, d in cells:
        scale, shift = design.transform(name, w, d)
        native = (w, d) == (400, 100)
        drawn = w == 100 and (name in thin_figures.NAMES or name in junction_drawings.NAMES or design.mono and name in thin_figures.MONO_LETTERS
                              or not design.serif and name in thin_figures.SANS_CAPS)
        if drawn:
            contours = thin_figures.thin_rings(name, model.rings, scale, shift, design.serif, design.mono, bool(design.slant))
        elif native:
            contours = model.rings
        elif name == 'pi':
            contours = [pi_curve(offset, scale, shift, w, d)]
        elif name in COMPARISONS and np.all(model.linear):
            contours = [comparison_ring(r, name, scale, shift, w, d) for r in model.rings]
            if name in ('lessequal', 'greaterequal'):
                bar = next(c for c in contours if len(c.pieces) == 4)
                j = next(i for i, c in enumerate(contours) if c is not bar)
                arrow = contours[j]
                gap = arrow.pieces.imag.min()-bar.pieces.imag.max()
                if gap < 24:
                    contours[j] = Contour(arrow.pieces+1j*(24-gap))
        elif straight:
            contours = [straight_ring(r, name, scale, shift, w, d) for r in model.rings]
        else:
            contours = model.fit(w, d, scale, shift, design.serif, name)
        for index,(prof, ref, curve) in enumerate(zip(profiles, model.rings, contours)):
            radius = ({100: 4, 400: 12, 900: 20} if design.serif else {100: 9, 400: 30, 900: 49})[w]
            # Interior corners in a small eye cannot carry the radius of a
            # full-height cap. Keep the aperture visible throughout the dial.
            if ref.area > 0:
                span = min(np.ptp(curve.pieces[:, 0].real), np.ptp(curve.pieces[:, 0].imag))
                radius = min(radius, .14*span)
            if drawn and consistent_width:
                aligned, source, target = fixed[index]
                if d != 100:
                    aligned, a, b = thin_figures.width_station_map(aligned, curve)
                    stations = np.unique(np.r_[target,a])
                    source, target = np.interp(stations,target,source), np.interp(stations,a,b)
            elif drawn:
                aligned, source, target = thin_figures.register_figure(ref, curve)
            if drawn:
                radius = min(radius, 4)
            for radius in (0, radius):
                anchors = station_knots if name == 'pi' and not native else ref.knots
                if drawn:
                    prof.append(Profile(aligned, source, target, radius))
                else:
                    prof.append(Profile(curve, anchors, curve.knots, radius))
    tracks = [[] for _ in range(2*len(cells))]
    ends = []
    for group, ref in zip(profiles, model.rings):
        samples = compatible_points(group, .20, compact=.24)
        for i, (out, z) in enumerate(zip(tracks, samples)):
            z = z+design.slant*z.imag
            if i == 0:
                z = round_default(z, ref.area)
            out.extend(z)
        ends.append(len(tracks[0])-1)
    return list(map(np.asarray, tracks)), ends
