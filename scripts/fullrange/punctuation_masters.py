"""Optical sizes for isolated dots, quote heads, narrow tails and solid geometric signs."""
import numpy as np
from punctuation_scope import dot_contours

PUNCT = {"colon","colon.case","semicolon","semicolon.case","comma","periodcentered","divide",
         "periodcentered.case","ellipsis","quoteleft","quoteright","quotedblleft","quotedblright",
         "quotesinglbase","quotedblbase","bullet","filledbox","triagup","triagdn","uni25AA",
         "uni25B4","uni25B6","uni25B8","uni25BE","uni25C0","uni25C2","uni25C6","uni25CF"}


def circle(x, y, radius):
    # Eight tangent quadratics. Implied midpoints give smooth joins and
    # cardinal extrema; mirrored integer controls ensure fourfold symmetry.
    t = round(radius * np.tan(np.pi / 8))
    offsets = [(-t, -radius), (-radius, -t), (-radius, t), (-t, radius),
               (t, radius), (radius, t), (radius, -t), (t, -radius)]
    return np.asarray(offsets, dtype=int) + [x, y]


def quadratic_circle(radius, flags):
    # The source starts each quadrant on its cardinal extremum, followed by
    # two or three quadratic controls. Intersect consecutive circle tangents
    # at the new radius to avoid magnifying the source's coordinate rounding.
    per_quarter = len(flags) // 4 - 1
    assert list(flags & 1) == ([1] + [0] * per_quarter) * 4
    step = np.pi / (2 * per_quarter)
    intersections = -1j * np.exp(-1j * (np.arange(per_quarter) + .5) * step) / np.cos(step / 2)
    quarter = np.r_[-1j, intersections]
    points = radius * np.concatenate([quarter * (-1j)**i for i in range(4)])
    return np.rint(np.column_stack((points.real, points.imag))).astype(int)


def round_dots(name, points, ends, flags, regular, weight):
    rings = np.split(points, np.asarray(ends[:-1], dtype=int) + 1)
    ring_flags = np.split(np.asarray(flags), np.asarray(ends[:-1], dtype=int) + 1)
    bounds = [(*ring.min(axis=0), *ring.max(axis=0)) for ring in rings]
    splits = np.asarray(regular.endPtsOfContours[:-1], dtype=int) + 1
    reference = np.split(np.asarray(regular.coordinates), splits)
    ref_flags = np.split(np.asarray(regular.flags), splits)
    ref_bounds = [(*ring.min(axis=0), *ring.max(axis=0)) for ring in reference]
    # The upright source already has circular dots. Keep the same contour and
    # point correspondence in every master, including alongside a comma tail.
    for i, j in zip(dot_contours(name, bounds), dot_contours(name, ref_bounds), strict=True):
        left, bottom, right, top = bounds[i]
        radius = round(np.sqrt((right - left) * (top - bottom)) / 2)
        if weight == 400:
            rings[i] = reference[j]
        else:
            offset = np.array([round((left + right) / 2), round((bottom + top) / 2)])
            rings[i] = quadratic_circle(radius, ref_flags[j]) + offset
        ring_flags[i] = ref_flags[j]
    return np.vstack(rings), (np.cumsum([len(r) for r in rings])-1).tolist(), np.concatenate(ring_flags)


def period_coords(regular, slant, weight, scale, shift):
    """Keep the period circular in page coordinates, even in a stretched italic."""
    regular_radius = (regular.yMax - regular.yMin) / 2
    radius = {100: 20, 400: round(regular_radius), 900: round(1.19 * regular_radius)}[weight]
    y = regular.yMin + radius
    upright_x = (regular.xMin + regular.xMax) / 2 - slant * (regular.yMin + regular_radius)
    x = round(upright_x * scale + shift + slant * y)
    return circle(x, y, radius)


def punctuation_coords(optical,name,w,d,scale,shift):
    z=optical.base
    out=z.copy()
    geometric=name.startswith(("uni25","triag")) or name in ("bullet","filledbox")
    for ring in optical.rings:
        ids=np.flatnonzero(ring.segments.sum(axis=(0,1)))
        pts=z[ids]
        center=(pts.real.min()+pts.real.max())/2+1j*(pts.imag.min()+pts.imag.max())/2
        span=max(np.ptp(pts.real),1)
        height=max(np.ptp(pts.imag),1)
        if name=='divide':
            if w==400 and d==100:
                continue
            # The two dots sit above and below the midpoint of the division
            # bar. Set their diameter and the bar's pen weight independently.
            bar=span>2.5*height
            thickness={100:24 if bar else 40,400:height,900:height*1.25}[w]
            xscale=scale if bar else thickness/height
            out[ids]=(center.real*scale+shift+(pts.real-center.real)*xscale
                      +1j*(center.imag+(pts.imag-center.imag)*thickness/height))
            continue
        curved_tail=height>1.46*span and not geometric
        if geometric:
            factor={100:.59 if name=="bullet" else .90,400:1.,900:1.13}[w]
        else:
            factor={100:min(1,40/min(span,height)),400:1.,900:1.19}[w]
        horizontal=1 if w==100 and not curved_tail and not geometric else 1+.22*(d/100-1)
        if w==400 and d==100:
            continue
        # A quote loses weight across its principal direction. This keeps
        # its lower taper visible while its dot-sized head can become thin.
        if curved_tail:
            factor=max(factor,.37)
            v=pts-center
            cov=np.cov(np.column_stack([v.real,v.imag]),rowvar=False)
            _,axes=np.linalg.eigh(cov)
            principal=complex(*axes[:,-1])
            local=v*principal.conjugate()
            delta=principal*(local.real*({100:.83,400:1.,900:1.04}[w])+1j*local.imag*factor)
        else:
            delta=(pts-center)*factor
        cy=center.imag
        if not geometric and not curved_tail and abs(pts.imag.min())<14:
            cy=pts.imag.min()+(cy-pts.imag.min())*factor
        out[ids]=center.real*scale+shift+delta.real*horizontal + 1j*(cy+delta.imag)
    return out+optical.slant*out.imag
