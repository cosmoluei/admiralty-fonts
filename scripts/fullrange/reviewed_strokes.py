"""Register straight cuts and branches by their construction points across masters."""
import numpy as np

from reviewed_capitals import rounded
from straight_masters import sloping


def polygon_tracks(design, name, cells):
    g = design.regular["glyf"][name]
    xy = np.asarray(g.coordinates)
    native = xy[:, 0] - design.slant * xy[:, 1] + 1j * xy[:, 1]
    tracks = []
    for w, d in cells:
        scale, shift = design.transform(name, w, d)
        z = native.real * scale + shift + 1j * native.imag
        if w != 400:
            if name == "N":
                z = capital_n(z, w)
            elif name == "k":
                z = lowercase_k(z, w)
            else:
                z = sloping(native, "seven", scale, shift, w, d)
        for radius in (0, {100: 8, 400: 26, 900: 39}[w]):
            p = rounded(z, radius)
            tracks.append(p + design.slant * p.imag)
    return tracks, [len(tracks[0])-1]


def capital_n(z, weight):
    left, right = z.real.min(), z.real.max()
    h = z.imag.max()
    stem = 24 if weight == 100 else min(129, .27*(right-left))
    slope = (right-left-stem)/h
    half = stem*np.hypot(1, slope)/2
    cap = stem/2+half
    # Intersections of the diagonal rails with the inner sides of the uprights.
    flat = 1 if weight == 100 else 4
    depth = (cap+flat)/slope
    points = [(left+stem,0),(left,0),(left,h),(left+cap,h),
              (right-stem-flat,depth),(right-stem,depth),(right-stem,h),(right,h),
              (right,0),(right-cap,0),(left+stem+flat,h-depth),(left+stem,h-depth)]
    return np.array([complex(x,y) for x,y in points])


def lowercase_k(z, weight):
    left = z[0].real
    cap, xh = z[1].imag, z[4].imag
    stem = 24 if weight == 100 else min(128, .31*np.ptp(z.real))
    right = left+stem
    # Fit the two rails of the rising arm and descending leg to their original
    # terminals. Their intersection defines the knee even in narrow Black.
    top = (z[4].real+z[5].real)/2
    foot = (z[7].real+z[8].real)/2
    split = .43*xh
    knee = .61*xh
    slope = (top-(left+.58*stem))/(xh-split)
    intercept = top-slope*xh
    knee_x = slope*knee+intercept
    leg_slope = (knee_x-foot)/knee
    arm = stem*.46*np.hypot(1,slope)
    leg = stem*.47*np.hypot(1,leg_slope)
    # Both re-entrant corners lie on the lower (right-hand) arm edge.
    def junction(side):
        y = (foot+side*leg-intercept-arm)/(slope-leg_slope)
        return complex(slope*y+intercept+arm,y)
    return np.array([left,left+1j*cap,right+1j*cap,right+1j*((right-intercept+arm)/slope),
                     top-arm+1j*xh,top+arm+1j*xh,junction(1),foot+leg,foot-leg,
                     junction(-1),right+1j*((right-intercept-arm)/slope),right])


def register_ascender(tracks, ends, cells, slant):
    """Replace the common upper shaft span, preserving the original bowl or hook."""
    cut = 645
    profiles = [z - slant*z.imag for z in tracks]
    tops = np.stack([z[:ends[0]+1:2].imag for z in profiles])
    shared = np.flatnonzero(tops.min(axis=0) > cut)
    if len(shared)<4 or np.any(np.diff(shared)!=1):
        raise ValueError("Missing continuous upper shaft")
    first,last = 2*shared[0],2*shared[-1]
    result = []
    for i, z in enumerate(profiles):
        ring = z[:ends[0]+1]
        # Sample the quadratics along the stem sides. The cutoff
        # sits above the bowl, the slash and the hook at every width.
        knots = ring[::2]
        handles = ring[1::2]
        t = np.linspace(0,1,17)[:,None]
        q = ((1-t)**2*knots + 2*t*(1-t)*handles+t*t*np.roll(knots,-1)).T.ravel()
        after = np.roll(q,-1)
        hits = []
        for ascending in (True, False):
            ix = np.where((q.imag<=cut)&(after.imag>cut) if ascending else
                          (q.imag>cut)&(after.imag<=cut))[0]
            if len(ix)!=1:
                raise ValueError("Ambiguous ascender sides")
            a,b = q[ix[0]],after[ix[0]]
            hits.append(a.real+(cut-a.imag)*(b.real-a.real)/(b.imag-a.imag))
        left,right = hits
        h = knots.imag.max()
        if right<=left:
            raise ValueError("Reversed ascender")
        weight = cells[i//2][0]
        rad = min(.43*(right-left),{100:9,400:27,900:39}[weight]) if i%2 else 0
        a,b = left+1j*cut,right+1j*cut
        p0,p1 = left+1j*(h-rad),left+rad+1j*h
        p2,p3 = right-rad+1j*h,right+1j*(h-rad)
        cap = [a,(a+p0)/2,p0,left+1j*h,p1,(p1+p2)/2,p2,right+1j*h,p3,(p3+b)/2,b]
        start = np.where(ring[:first].imag>cut,a,ring[:first])
        finish = np.where(ring[last+1:].imag>cut,b,ring[last+1:])
        revised = np.r_[start,cap,finish,z[ends[0]+1:]]
        result.append(revised+slant*revised.imag)
    delta = len(result[0])-len(tracks[0])
    return result,[e+delta for e in ends]
