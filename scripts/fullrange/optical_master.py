"""Fit compatible masters to local stroke measurements in the original quadratic outlines."""
from dataclasses import dataclass
from functools import cached_property

import numpy as np
from scipy.linalg import cho_factor, cho_solve
from scipy.spatial import Delaunay, QhullError
from scipy import sparse
import osqp


def direction(z):
    return z/np.maximum(abs(z),1e-9)


def quadratic(a, b, c, t):
    return (1-t)**2*a + 2*t*(1-t)*b + t*t*c


@dataclass
class Ring:
    segments: np.ndarray
    # Each row maps an on-curve or control point to the original TrueType nodes.

    @classmethod
    def read(cls, ids, flags, size):
        nodes = np.eye(size)[ids]
        on = np.asarray(flags, dtype=int) & 1
        if np.any(on):
            pivot = int(np.flatnonzero(on)[0])
            nodes, on = np.roll(nodes, -pivot, axis=0), np.roll(on, -pivot)
        else:
            nodes = np.vstack([(nodes[-1]+nodes[0])/2, nodes])
            on = np.r_[1,on]
        cursor = nodes[0]
        control = None
        segments = []
        for point, flag in zip(np.vstack([nodes[1:],nodes[:1]]),np.r_[on[1:],1]):
            if flag:
                segments.append((cursor, (cursor+point)/2 if control is None else control, point))
                cursor, control = point, None
            elif control is None:
                control = point
            else:
                mid = (control+point)/2
                segments.append((cursor,control,mid))
                cursor, control = mid,point
        return cls(np.asarray(segments))

    def set_corners(self, base):
        a,b,c = (self.segments @ base).T
        u, v = direction(c-np.where(abs(c-b)>1e-6,b,a)), direction(np.roll(np.where(abs(b-a)>1e-6,b,c)-a,-1))
        angle = np.arccos(np.clip((u.conj()*v).real,-1,1))
        self.after = (angle > np.deg2rad(14)) & (angle < np.deg2rad(174))
        # Preserve fractional implied on-curves and native straight line
        # segments exactly at the default 1000-unit grid.
        start, ctrl, end = self.segments.transpose(1,0,2)
        straight = np.all(abs(ctrl-(start+end)/2)<1e-9,axis=1)
        implied = (np.count_nonzero(start,axis=1)==2) & ~np.roll(self.after,1)
        self.keep = np.column_stack([~implied,~straight,self.after,self.after])
        self.flags = np.broadcast_to([1,0,1,0], self.keep.shape)[self.keep]

    def rounded(self, coords, radius):
        """Exact subdivision of each quadratic leaves the rest of the curve intact."""
        a,b,c = (self.segments @ coords).T
        u, v = direction(c-np.where(abs(c-b)>1e-6,b,a)),direction(np.roll(np.where(abs(b-a)>1e-6,b,c)-a,-1))
        angle = np.arccos(np.clip((u.conj()*v).real,-1,1))
        # Do not shorten a side by more than 40%; opposing fillets cannot overlap.
        reach = np.where(self.after,radius*np.tan(np.minimum(angle,2.95)/2),0.)
        lo = np.minimum(.4,np.roll(reach,1)/np.maximum(2*abs(b-a),1.))
        hi = 1-np.minimum(.4,reach/np.maximum(2*abs(c-b),1.))
        start = quadratic(a,b,c,lo)
        end = quadratic(a,b,c,hi)
        ctrl = start+(hi-lo)*((1-lo)*(b-a)+lo*(c-b))
        # Intersect endpoint tangents of the trimmed curves.
        vin = direction((1-hi)*(b-a)+hi*(c-b))
        vout = np.roll(direction((1-lo)*(b-a)+lo*(c-b)),-1)
        gap = np.roll(start,-1)-end
        den = (vin.conj()*vout).imag
        h = np.divide((gap.conj()*vout).imag,den,out=np.zeros_like(den),where=abs(den)>1e-7)
        handle = np.where((h>=0)&(h<2*abs(gap)),end+vin*h,c)
        # Original sharp corners have a collapsed fillet at radius zero.
        all_pts = np.column_stack([start,ctrl,end,handle])
        return all_pts[self.keep]

    def sampling(self, coords, spacing):
        samples, tangents, ends = [], [], []
        for mat in self.segments:
            a,b,c = mat@coords
            count = max(1,int(np.ceil((abs(a-b)+abs(b-c))/spacing)))
            if spacing<10 and abs(a-2*b+c)>1:
                count=max(count,4)
            ts = np.arange(count)/count
            t = ts[:,None]
            samples.extend(quadratic(*mat,t))
            tangents.extend(direction((1-ts)*(b-a)+ts*(c-b)))
            ends.extend(quadratic(*mat,(ts+1/count)[:,None]))
        return np.asarray(samples),np.asarray(tangents),np.asarray(ends)


class OpticalMaster:
    def __init__(self, glyph, slant=0, spacing=17):
        xy = np.asarray(glyph.coordinates, dtype=float)
        self.base = xy[:,0]-slant*xy[:,1]+1j*xy[:,1]
        self.slant = slant
        self.spacing = spacing
        self.rings = []
        start = 0
        for end in glyph.endPtsOfContours:
            ring = Ring.read(np.arange(start,end+1),glyph.flags[start:end+1],len(xy))
            self.rings.append(ring)
            ring.set_corners(self.base)
            start = end+1

    @cached_property
    def constraints(self):
        n = len(self.base)
        data = [r.sampling(self.base,self.spacing) for r in self.rings]
        source, tangent, end = [np.concatenate(v) for v in zip(*data)]
        a = source@self.base
        b = end@self.base
        centers = (a+b)/2
        origin = (source+end)/2
        tangents = direction(b-a)
        normals = -1j*tangents
        # First entry back into the white region across the stroke. Only
        # sufficiently opposed edges can constrain a physical pen thickness.
        dy = ((a[None,:]-centers[:,None])*normals[:,None].conj()).imag
        ey = ((b[None,:]-centers[:,None])*normals[:,None].conj()).imag
        hits = (dy>0)!=(ey>0)
        alpha = np.divide(dy,dy-ey,out=np.zeros_like(dy),where=hits)
        hit_pts = a+(b-a)*alpha
        dist = ((hit_pts-centers[:,None])*normals[:,None].conj()).real
        dist = np.where(hits&(dist>1),dist,np.inf)
        near = dist.argmin(axis=1)
        i = np.arange(len(near))
        distance = dist[i,near]
        use = (distance<174) & ((tangents.conj()*tangents[near]).real<-.64) & (abs(b-a)>1)
        i,j = i[use],near[use]
        other = source[j]+alpha[i,j,None]*(end[j]-source[j])
        pairs = other-origin[i]
        measured = distance[i]
        normal = normals[i]
        # Keep the midpoint of measured strokes near the designed skeleton,
        # while allowing connected contours to redistribute at thick joins.
        center = (other+origin[i])/2
        rows = [np.eye(n)*.19,center*.44,pairs*1.9]
        # Preserve the relative tangent handles at native smooth on-curve joins.
        # Flat spans need their border orientation preserved at both ends.
        straight_x, straight_y = [], []
        for r in self.rings:
            for seg, nxt in zip(r.segments,np.roll(r.segments,-1,axis=0)):
                v = (seg[2]-seg[1]) @ self.base
                w = (nxt[1]-nxt[0]) @ self.base
                if min(abs(v),abs(w))>1e-4 and (direction(v).conjugate()*direction(w)).real>.997:
                    rows.append((4*((seg[2]-seg[1])*abs(w)-(nxt[1]-nxt[0])*abs(v))/(abs(v)+abs(w)))[None,:])
                span = seg[-1]-seg[0]
                p,q,u = seg @ self.base
                if abs(p.real-u.real)<.2 and abs(q.real-u.real)<.2:
                    straight_x.append(span)
                if abs(p.imag-u.imag)<.2 and abs(q.imag-u.imag)<.2:
                    straight_y.append(span)
        common = np.vstack(rows)
        pinned_y = np.min(abs(self.base.imag[:,None]-np.array([-224,-220,-12,-10,0,520,530,700,712,740,752])),axis=1)<.51
        mx = np.vstack([common, np.asarray(straight_x).reshape(-1,n)*7])
        my = np.vstack([common, np.asarray(straight_y).reshape(-1,n)*7, np.eye(n)[pinned_y]*7])
        fit_start = n+len(center)
        def factor(mat):
            return cho_solve(cho_factor(mat.T@mat), mat[fit_start:fit_start+len(pairs)].T)*1.9
        self.penalty = sparse.block_diag((mx.T@mx,my.T@my),format="csc")
        # Triangulate boundary samples. In every non-flat triangle preserve
        # a fraction of its three signed altitudes. These linear inequalities
        # keep small counters and hairline junctions open during the fitting.
        _,ix = np.unique(np.rint(np.column_stack([a.real,a.imag])*100),axis=0,return_index=True)
        coords = np.column_stack([a[ix].real,a[ix].imag])
        guards,tangent_edges = [],[]
        try:
            triangles=ix[Delaunay(coords).simplices]
        except QhullError:
            triangles=np.empty((0,3),dtype=int)
        # A piecewise-affine map covers the entire glyph, including the
        # counters. It must remain locally one-to-one throughout a change in
        # weight. Distances across the ink alone cannot enforce this at an
        # oblique join, where both sides can slip past one another.
        bm=np.stack([a[triangles[:,1]]-a[triangles[:,0]],a[triangles[:,2]]-a[triangles[:,0]]],axis=1)
        bv=np.stack([bm.real,bm.imag],axis=1)
        keep=np.abs(np.linalg.det(bv))>.045
        self.mesh=(source,triangles[keep],np.linalg.inv(bv[keep]))
        for ids in triangles:
            for j in range(3):
                i,k,l=map(int,np.roll(ids,j))
                edge=a[l]-a[k]
                if abs(edge)<2:
                    continue
                at=((a[i]-a[k])/edge).real
                altitude=abs(((a[i]-a[k])/edge).imag)*abs(edge)
                if -.001<=at<=1.001 and altitude>.63:
                    row=source[i]-((1-at)*source[k]+at*source[l])
                    guards.append(row)
                    tangent_edges.append(edge)
        self.guard_rows=np.asarray(guards).reshape(-1,n)
        self.guard_tangents=np.asarray(tangent_edges)
        # A quadratic's derivative interpolates its two handle vectors.
        # Triangulating points on the ink does not constrain a short handle
        # between samples, which can flip and form a loop at Thin.
        handles=np.concatenate([np.diff(r.segments,axis=1).reshape(-1,n) for r in self.rings])
        self.handle_rows=handles[abs(handles@self.base)>.04]
        return measured,normal,factor(mx),factor(my)

    def retain_clearances(self, result, scaffold, scale):
        rows=self.guard_rows
        v=self.guard_tangents
        normals=1j*direction(scale*v.real+1j*v.imag)
        signed=((rows@scaffold)*normals.conj()).real
        normals*=np.sign(signed)
        available=abs(signed)
        minimum=np.minimum(available*.85,np.maximum(available*.18, np.minimum(7,available*.70)))
        handles=self.handle_rows
        reference=handles@scaffold
        rows=np.vstack([rows,handles])
        normals=np.r_[normals,direction(reference)]
        minimum=np.r_[minimum,np.minimum(abs(reference)*.60, np.maximum(1.1,abs(reference)*.14))]
        lower=minimum-((rows@result)*normals.conj()).real
        matrix=sparse.csc_matrix(np.hstack([rows*normals.real[:,None],rows*normals.imag[:,None]]))
        sample,tri,inv=self.mesh
        candidate=result
        for iteration in range(10):
            coords=(sample@candidate)[tri]
            sides=coords[:,1:]-coords[:,:1]
            jac=np.stack([sides.real,sides.imag],axis=1)@inv
            eigen,vectors=np.linalg.eigh((jac+jac.transpose(0,2,1))/2)
            weak=eigen[:,0]<.055
            if not np.any(weak) and (iteration or lower.max(initial=0)<.01):
                return candidate
            if np.any(weak):
                # For every direction v, vᵀJv is linear in the outline
                # coordinates. Add the most compressed direction of each
                # failing triangle. Positive symmetric part rules out both
                # local foldovers and overlaps of distant parts of the mesh.
                u=vectors[weak,:,0]
                pair=(inv[weak]@u[:,:,None])[:,:,0]
                ids=tri[weak]
                diff=sample[ids[:,1:]]-sample[ids[:,:1]]
                direction_rows=np.einsum('ij,ijk->ik',pair,diff)
                norm=1/np.maximum(np.linalg.norm(direction_rows,axis=1),1e-6)
                direction_rows*=norm[:,None]
                projected=(direction_rows@result)*(u[:,0]-1j*u[:,1])
                extra=sparse.csc_matrix(np.hstack([direction_rows*u[:,:1],direction_rows*u[:,1:]]))
                matrix=sparse.vstack([matrix,extra],format="csc")
                lower=np.r_[lower,.065*norm-projected.real]
            solver=osqp.OSQP()
            solver.setup(P=self.penalty,q=np.zeros(self.penalty.shape[0]),A=matrix,
                         l=lower,u=np.full(len(lower),np.inf),verbose=False,
                         eps_abs=.009,eps_rel=.00015,max_iter=12000)
            update=solver.solve(raise_error=False)
            if update.info.status_val not in (1,2):
                raise ArithmeticError(f"Clearance fit: {update.info.status}")
            x,y=np.split(update.x,2)
            candidate=result+x+1j*y
        return candidate

    def fit(self, weight, width, scale, shift, serif=False):
        if weight==400 and abs(scale-1)<1e-8 and abs(shift)<1e-8:
            return self.base+self.slant*self.base.imag
        size,normal,xfit,yfit = self.constraints
        tangent = 1j*normal
        new_tangent = direction(tangent.real*scale+1j*tangent.imag)
        nn = -1j*new_tangent
        effective = size*scale/np.maximum(abs(tangent.real*scale+1j*tangent.imag),1e-6)
        optical_width = 1 + .11*(width/100-1)
        if weight==100:
            # Hairlines, shoulder joints and serif wedges can be narrower than a full stem.
            goal = np.clip(24*(size/80)**(.48 if serif else .18),6,29)
        elif weight==900:
            goal = size + np.minimum(48,size*(.42 if serif else .55))
        else:
            goal = size*optical_width
        displacement = nn*(goal-effective)
        z = self.base.real*scale+shift+1j*self.base.imag
        result = z+(xfit@displacement.real)+1j*(yfit@displacement.imag)
        result=self.retain_clearances(result,z,scale)
        return result+self.slant*result.imag

    def points(self, coords, radius):
        tracks = [r.rounded(coords,radius) for r in self.rings]
        ends = (np.cumsum([len(t) for t in tracks])-1).tolist()
        return np.concatenate(tracks), ends
