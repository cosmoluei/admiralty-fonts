"""Match closed outlines across masters and soften their existing corners in glyph space."""
from __future__ import annotations

import math
import sys
from pathlib import Path

import numpy as np
from fontTools.pens.basePen import BasePen
from scipy.optimize import linear_sum_assignment
from scipy.signal import find_peaks

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from vf_align import _Feat, _best_alignment


def cubic(points, t):
    a, b, c, d = points.T
    u = 1-t
    return u**3*a + 3*u*u*t*b + 3*u*t*t*c + t**3*d


class OutlinePen(BasePen):
    """Decompose components and implied quadratic points into cubic Bézier segments."""
    def __init__(self, glyphs):
        super().__init__(glyphs)
        self.contours = []

    def _moveTo(self, p):
        self.parts = []
        self.start = self.last = complex(*p)

    def _lineTo(self, p):
        q = complex(*p)
        if self.last != q:
            v = (q-self.last)/3
            self.parts.append((self.last, self.last+v, q-v, q))
        self.last = q

    def _qCurveToOne(self, control, end):
        q, c = complex(*end), complex(*control)
        self._curveToOne(pair((self.last+2*c)/3), pair((q+2*c)/3), end)

    def _curveToOne(self, a, b, end):
        pts = (self.last, complex(*a), complex(*b), complex(*end))
        if max(abs(p-pts[0]) for p in pts) > .0001:
            self.parts.append(pts)
        self.last = pts[-1]

    def _closePath(self):
        if abs(self.last-self.start) > .0001:
            self._lineTo(pair(self.start))
        if self.parts:
            self.contours.append(Contour(self.parts))


def pair(z):
    return (z.real, z.imag)


def mapped_landmarks(nodes, source, target):
    """Look up named design stations across contour rotations and winding changes."""
    original = np.array([complex(*point) for point in source])
    distance = abs(nodes[:, None] - original)
    closest = distance.argmin(axis=1)
    errors = distance[np.arange(len(nodes)), closest]
    if np.max(errors) > 2:
        raise ValueError(f'Unassigned design landmark {nodes[np.argmax(errors)]}')
    return np.array([complex(*point) for point in target])[closest]


class Contour:
    """Parameterize by physical arc length to place fillets and match design landmarks."""
    def __init__(self, pieces):
        self.pieces = np.asarray(pieces, dtype=complex)
        self.ts = np.linspace(0, 1, 49)
        a,b,c,d = self.pieces.T[:, :, None]
        t = self.ts
        samples = (1-t)**3*a + 3*(1-t)**2*t*b + 3*(1-t)*t**2*c + t**3*d
        lengths = np.abs(np.diff(samples, axis=1))
        self.arcs = np.column_stack([np.zeros(len(pieces)), lengths.cumsum(axis=1)])
        self.breaks = np.r_[0., np.cumsum(self.arcs[:,-1])]
        self.length = self.breaks[-1]
        self.knots = self.breaks / self.length
        flat = samples.flatten()
        self.area = np.sum((flat.conj()*np.roll(flat, -1)).imag)/2
        self.center = (flat.real.max()+flat.real.min() + 1j*(flat.imag.max()+flat.imag.min()))/2
        segments = [('curve', *(np.array(pair(z)) for z in c)) for c in self.pieces]
        self.features = _Feat(segments)
        dot = (self.features.inn*self.features.out).sum(axis=1).clip(-1,1)
        self.turns = np.arccos(dot)
        self.corners = np.flatnonzero(self.turns > math.radians(12))

    def eval(self, u, *, tangent=False):
        s = (np.asarray(u)%1)*self.length
        ix = np.searchsorted(self.breaks, s, side='right')-1
        arc = self.arcs[ix]
        local = s-self.breaks[ix]
        j = np.sum(arc <= local[:,None], axis=1).clip(1, len(self.ts)-1)-1
        rows = np.arange(len(ix))
        t = (j+(local-arc[rows,j])/np.maximum(1e-12, arc[rows,j+1]-arc[rows,j]))/(len(self.ts)-1)
        points = self.pieces[ix]
        if not tangent:
            return cubic(points, t)
        a,b,c,d = points.T
        v = (1-t)**2*(b-a) + 2*(1-t)*t*(c-b) + t**2*(d-c)
        return v/np.maximum(abs(v),1e-15)

    def terminals(self, bar=False):
        # A cut end turns into the ink on both sides. An inside notch can
        # have the very same angle; including it would move an entire stem.
        u, v = self.features.inn.T
        x, y = self.features.out.T
        nodes = np.flatnonzero(((u*y - v*x) < 0) & (self.turns > math.radians(55))
                               & (self.turns < math.radians(122)))
        if bar:
            # Both borders of e's crossbar must stay horizontal through
            # interpolation. The stroke union can split one straight edge at
            # the bowl's wall. Register its real ends, never that internal seam.
            flat = np.ptp(self.pieces.imag, axis=1) < .001
            starts = np.flatnonzero(flat & ~np.roll(flat, 1))
            if len(starts):
                stops = np.flatnonzero(~flat & np.roll(flat, 1))
                # A contour need not start at the bar, so a run can wrap.
                after = stops[np.searchsorted(stops, starts) % len(stops)]
                x = self.pieces[:, 0].real
                longest = np.argmax(abs(x[after] - x[starts]))
                nodes = np.unique(np.r_[nodes, starts[longest], after[longest]])
        return nodes

    def roll(self, index):
        return Contour(np.roll(self.pieces, -int(index), axis=0)) if index else self

    def extrema_in_span(self, start, end):
        # When two masters share a crown or a crotch in this span, constrain
        # its correspondence before fitting intermediate weights.
        z = np.r_[self.pieces[:,0], self.pieces[0,0]][start:end+1]
        features = []
        for label, values in enumerate([z.imag, -z.imag, z.real, -z.real]):
            nodes = find_peaks(values, prominence=5)[0]
            features.extend((start+int(i), label) for i in nodes)
        return sorted(features)

    def registered(self, reference, bar=False):
        candidate = self
        if self.area*reference.area < 0:
            candidate = Contour(self.pieces[::-1,::-1])
        anchors, targets = reference.terminals(bar), candidate.terminals(bar)
        if len(anchors) >= 2 and len(anchors) == len(targets) and anchors[0] == 0:
            # Match flat ends before any curve nodes. Their positions split
            # even strongly compressed arches into independent monotone spans.
            def alignment_cost(shift):
                b = np.roll(targets, -shift)
                diff = reference.features.npos[anchors] - candidate.features.npos[b]
                return (diff**2).sum() + .1*((reference.features.out[anchors]-candidate.features.out[b])**2).sum()
            shift = min(range(len(anchors)), key=alignment_cost)
            target = candidate.roll(targets[shift])
            a = np.r_[anchors,len(reference.pieces)]
            b = np.r_[target.terminals(bar),len(target.pieces)]
            matched = list(zip(a,b))
            for p,q,r,s in zip(a,a[1:],b,b[1:]):
                source_extrema = reference.extrema_in_span(p,q)
                target_extrema = target.extrema_in_span(r,s)
                if [x[1] for x in source_extrema] == [x[1] for x in target_extrema]:
                    matched.extend((x[0],y[0]) for x,y in zip(source_extrema,target_extrema))
            ai, bi = np.array(sorted(set(matched))).T
            return target, reference.knots[ai], target.knots[bi]
        _, shift, matched = _best_alignment(reference.features, candidate.features)
        target = candidate.roll(shift)
        ai, bi = np.asarray(matched).T
        return target, np.r_[reference.knots[ai],1.], np.r_[target.knots[bi],1.]


class Profile:
    def __init__(self, contour, reference_knots, target_knots, radius):
        self.contour = contour
        self.ref = reference_knots
        self.target = target_knots
        self.fillets = []
        stops = [*target_knots, *contour.knots[contour.corners]]
        corners = contour.corners
        for j, idx in enumerate(corners):
            if radius <= 0:
                break
            pos = contour.knots[idx]
            angle = contour.turns[idx]
            before = (pos-contour.knots[corners[j-1]])%1 if len(corners)>1 else 1.
            after = (contour.knots[corners[(j+1)%len(corners)]]-pos)%1 if len(corners)>1 else 1.
            reach = min(radius*math.tan(angle/2)/contour.length, .44*before, .44*after)
            if reach*contour.length < .05 or angle > math.radians(176):
                continue
            bounds = np.array([pos-reach, pos+reach])
            p, q = contour.eval(bounds)
            v, w = contour.eval(bounds, tangent=True)
            theta = abs(np.angle(v.conjugate()*w))
            handle = abs(q-p)/(3*math.cos(theta/4)**2)
            self.fillets.append((pos, reach, np.array([p,p+handle*v,q-handle*w,q])))
            stops.extend(bounds%1)
        self.stops = np.interp(stops,self.target,self.ref)

    def eval(self, positions):
        u = np.interp(positions,self.ref,self.target)
        points = self.contour.eval(u)
        for center, reach, fillet in self.fillets:
            local = (u-center+.5)%1-.5
            use = np.abs(local)<reach
            if np.any(use):
                points[use] = cubic(fillet,(local[use]/reach+1)/2)
        return points


def ordered_contours(reference, other):
    if len(reference) != len(other):
        raise ValueError(f"Contour topology differs: {len(reference)} vs {len(other)}")
    if len(reference) <= 1:
        return other
    # Normalize shape positions within the glyph, independently of width and weight.
    def positions(cs):
        centers = np.array([c.center for c in cs])
        return ((centers.real-centers.real.mean())/max(np.ptp(centers.real),1)
                +1j*(centers.imag-centers.imag.mean())/max(np.ptp(centers.imag),1))
    pos = abs(positions(reference)[:,None]-positions(other)[None,:])
    areas = [np.array([abs(c.area) for c in cs]) for cs in (reference, other)]
    a,b = [np.log(np.maximum(v/v.sum(),1e-8)) for v in areas]
    cost = pos + .24*abs(a[:,None]-b[None,:])
    # An expanding counter can be closer in area and position to the outer
    # bowl than to its own source. Exterior and counter must correspond even
    # when all windings in one master have been reversed.
    roles = [np.sign([c.area for c in rings]) * np.sign(rings[int(sizes.argmax())].area)
             for rings,sizes in zip((reference, other),areas)]
    if np.array_equal(np.sort(roles[0]), np.sort(roles[1])):
        cost = np.where(roles[0][:,None] == roles[1][None,:], cost, np.inf)
    _, order = linear_sum_assignment(cost)
    return [other[i] for i in order]


def compact_quadratics(tracks,marks,tolerance,protected=()):
    """Remove shared subdivisions while bounding the entire curve in every master."""
    pts=np.array(tracks)
    starts,handles=pts[:,::2],pts[:,1::2]
    ends=np.roll(starts,-1,axis=1)
    def join(i,j):
        t=(marks[i:j+1]-marks[i])/(marks[j]-marks[i])
        a=starts[:,i,None]
        b=ends[:,j-1,None]
        mid=(t[:-1]+t[1:])/2
        true=(starts[:,i:j]+2*handles[:,i:j]+ends[:,i:j])/4
        coeff=2*mid*(1-mid)
        q=((true-a*(1-mid)**2-b*mid**2)@coeff)/sum(coeff**2)
        q=q[:,None]
        def at(u):
            return a*(1-u)**2+2*q*u*(1-u)+b*u**2
        lo,hi=t[:-1],t[1:]
        p0,p1=at(lo),at(hi)
        control=p0+(hi-lo)*((1-lo)*(q-a)+lo*(b-q))
        # The difference of two quadratic Béziers stays inside the convex
        # hull of its three control vectors, including between sample points.
        if (np.max(abs(p0-starts[:,i:j]))<=tolerance and
                np.max(abs(p1-ends[:,i:j]))<=tolerance and
                np.max(abs(control-handles[:,i:j]))<=tolerance):
            return q[:,0]
        return None
    points=[]
    boundaries=np.searchsorted(marks,np.r_[protected,1.])
    i=0
    while i<starts.shape[1]:
        best=i+1
        handle=handles[:,i]
        step=2
        limit=boundaries[np.searchsorted(boundaries,i,side="right")]
        while best<limit:
            j=min(i+step,limit)
            test=join(i,j)
            if test is None:
                limit=j-1
                while best<limit:
                    j=(best+limit+1)//2
                    test=join(i,j)
                    if test is None:
                        limit=j-1
                    else:
                        best,handle=j,test
                break
            best,handle=j,test
            step*=2
        points.extend((starts[:,i],handle))
        i=best
    return np.array(points).T


def compatible_points(profiles, tolerance=.25, compact=0, protected=()):
    """Fit corresponding quadratic spans, checking seven interior positions against every master."""
    marks = np.unique(np.r_[0., 1., protected, np.concatenate([p.stops for p in profiles])])
    # Only merge stops separated by less than a thousandth of a design unit.
    marks = marks[np.r_[True,np.diff(marks)>1e-8]]
    marks[-1] = 1.
    frac = np.arange(9)/8
    for _ in range(16):
        u = marks[:-1,None] + np.diff(marks)[:,None]*frac
        bad = np.zeros(len(u),dtype=bool)
        results = []
        for p in profiles:
            samples = p.eval(u.ravel()).reshape(u.shape)
            a,m,b = samples[:,0],samples[:,4],samples[:,-1]
            control = 2*m-(a+b)/2
            fitted = (1-frac)**2*a[:,None]+2*frac*(1-frac)*control[:,None]+frac**2*b[:,None]
            bad |= np.max(abs(fitted-samples),axis=1)>tolerance
            results.append(np.column_stack([a,control]).ravel())
        if not np.any(bad):
            return compact_quadratics(results,marks,compact,protected) if compact else results
        marks = np.sort(np.r_[marks,(marks[:-1]+marks[1:])[bad]/2])
    raise ValueError("Quadratic fit did not converge")


def e_points(profiles):
    # Sub-unit moves on a narrow wall turn into a staircase when rounded to
    # the production font's 1000-unit em. Fit longer quadratic arcs, keeping
    # the exact stations for the crossbar and the cut on the lower lip.
    base = profiles[0].contour
    stations = base.knots[base.terminals(bar=True)]
    tracks = compatible_points(profiles, tolerance=.19, compact=.9, protected=stations)
    # The upper counter has two stations on its horizontal bar. The outer
    # contour has two more on the diagonal lip cut, the shortest station span.
    if len(stations) == 4:
        span = np.diff(np.r_[stations, 1.])
        j = int(np.argmin(span))
        endpoints = base.eval(stations[[j, (j+1) % len(stations)]])
        a, b = [int(np.argmin(abs(tracks[0, ::2]-z))) for z in endpoints]
        # With square corners, encode the cut as one straight segment. Short
        # subdivisions used by the rounded cuts would each round to a slightly
        # different slope on the integer grid. Keep their points at the ends
        # so both radius masters still have the same topology.
        if a < b:
            mid = (a+b-1)//2
            for sharp in tracks[::2]:
                sharp[2*a:2*mid+2] = sharp[2*a]
                sharp[2*mid+2:2*b] = sharp[2*b]
    return tracks


def grid_slanted_walls(points, ends, slant):
    """Keep interior samples on a straight italic stem after integer rounding."""
    out = points.copy()
    first = 0
    for last in ends:
        ring = out[first:last+1]
        upright_x = ring.real - slant * ring.imag
        x, control = upright_x[::2], upright_x[1::2]
        straight = (abs(x-np.roll(x, -1)) < .075) & (abs(x-control) < .075)
        starts = np.flatnonzero(straight & ~np.roll(straight, 1))
        stops = np.flatnonzero(~straight & np.roll(straight, 1))
        for start in starts:
            stop = stops[np.searchsorted(stops, start) % len(stops)]
            count = (stop-start) % len(x)
            y0, y1 = ring[2*start].imag, ring[2*stop].imag
            if count < 2 or abs(y1-y0) < 25:
                continue
            # Move along the stroke to a point that lands on the integer
            # x grid. Its sides and both junctions keep the authored position.
            inside = (2*start + np.arange(1, 2*count)) % len(ring)
            z = ring[inside]
            y = np.rint(z.imag + (np.rint(z.real)-z.real)/slant)
            y = np.clip(y, min(y0,y1), max(y0,y1))
            ring[inside] = z + (slant+1j)*(y-z.imag)
        first = last + 1
    return out
