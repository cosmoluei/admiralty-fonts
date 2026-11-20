"""Ascenders, descenders and diagonal lowercase masters on the 0.300 metrics."""
import math

import pathops

from study_shapes import Drawing
from stroke_geometry import round_branches

LETTERS = "fjktvwxyz"


def remaining_outline(name, advance, weight, width):
    stem = {100: 24, 400: {65: 78, 100: 86, 150: 92}[width], 900: 128}[weight]
    bar = {100: 24, 400: 74, 900: 105}[weight]
    if name in "fjt":
        return hook(name, advance, stem, bar, weight)
    return diagonal(name, advance, stem, bar, width)


def hook(name, advance, stem, bar, weight):
    # Draw in physical glyph space. Only the counters and the length of the
    # arms follow width; horizontal and vertical pen diameters stay independent.
    top = 520-bar/2
    if name == "j":
        axis = .55*advance
        g = Drawing(axis, 1, stem, bar/stem)
        low = -224+bar/2
        reach = max(.48*advance, .8*stem)
        g.add((0,520),(0,-58),(0,low+55,-.31*reach,low,-.71*reach,low),
              (-.83*reach,low,-.92*reach,low+2,-reach,low+6))
    else:
        axis = max(.41*advance, .55*stem)
        g = Drawing(axis, 1, stem, bar/stem)
        reach = advance-axis-.18*stem
        if name == "f":
            hi = 752-bar/2
            g.add((0,0),(0,599),(0,hi-55,.31*reach,hi,.65*reach,hi),
                  (.78*reach,hi,.89*reach,hi-3,reach,hi-12))
        else:
            low = -10+bar/2
            g.add((0,648),(0,150),(0,low+58,.22*reach,low,.63*reach,low),
                  (.75*reach,low,.88*reach,low+3,reach,low+11))
        g.add((-.77*axis,top),(.89*reach,top))
    g.path.simplify(clockwise=True)
    result = round_branches(g.path, stem*.5)
    result = result.transform(1,0,0,bar/stem)
    if name == "j":
        dot = Drawing(axis, 1, stem, 1)
        dot.dot(0, {100: 654, 400: 656, 900: 666}[weight])
        dot.path.simplify(clockwise=True)
        result.addPath(dot.path)
    return result


def diagonal(name, advance, stem, bar, width):
    path = pathops.Path()
    def polygon(points):
        pen = path.getPen()
        pen.moveTo(points[0])
        for p in points[1:]:
            pen.lineTo(p)
        pen.closePath()

    def slash(x0,y0,x1,y1,thickness):
        half = thickness*math.hypot(x1-x0,y1-y0)/(2*abs(y1-y0))
        polygon([(x0-half,y0),(x1-half,y1),(x1+half,y1),(x0+half,y0)])

    margin = max(12, min(.067*advance, .25*advance-.35*stem))
    left, right = margin+stem*.53, advance-margin-stem*.53
    mid = advance/2
    # A small easing at heavy diagonals avoids black piles at the vertices.
    diag = stem*(1 if stem==24 else .92)
    if name == "v":
        # Use shared flat terminals at the cap and baseline; the union makes
        # a shallow flat foot rather than a miter beyond the baseline.
        slash(left,520,mid,0,diag)
        slash(mid,0,right,520,diag*.97)
    elif name == "w":
        a, b = left+.235*(right-left), left+.765*(right-left)
        slash(left,520,a,0,diag)
        slash(a,0,mid,508,diag*.95)
        slash(mid,508,b,0,diag)
        slash(b,0,right,520,diag*.95)
    elif name == "x":
        slash(left,520,right,0,diag)
        slash(left,0,right,520,diag*.95)
    elif name == "k":
        # Intersect the *edges* of both diagonals analytically. Unioning
        # three truncated rectangles leaves sub-unit spurs around the crotch.
        stem_edge = margin+stem
        upper_tip = right-.03*advance
        rise = (upper_tip-stem_edge)/270
        upper_half = .435*diag*math.hypot(1,rise)
        upper_left = upper_tip-upper_half
        upper_right = upper_tip+upper_half
        upper_lower_intercept = stem_edge - 250*rise + upper_half
        leg_join = upper_lower_intercept+295*rise
        drop = (right-leg_join)/295
        lower_half = .5*diag*math.hypot(1,drop)
        def join(offset):
            y = (right+offset-upper_lower_intercept)/(drop+rise)
            return (upper_lower_intercept+rise*y,y)
        polygon([(margin,0),(margin,740),(stem_edge,740),
                 (stem_edge,250+upper_half/rise),(upper_left,520),(upper_right,520),
                 join(lower_half),(right+lower_half,0),(right-lower_half,0),
                 join(-lower_half),(stem_edge,250-upper_half/rise),(stem_edge,0)])
    elif name == "z":
        polygon([(margin,0),(margin,bar),(advance-margin,bar),(advance-margin,0)])
        polygon([(margin,520-bar),(margin,520),(advance-margin,520),(advance-margin,520-bar)])
        half = diag*math.hypot(advance-2*margin,520)/(2*520)
        slash(margin+half,bar*.63,advance-margin-half,520-bar*.63,diag)
    elif name == "y":
        junction = left+.46*(right-left)
        slash(left,520,junction,13,diag)
        # The lower exit has the same hook direction as the release y and j.
        g = Drawing(0,1,stem,bar/stem)
        tail = margin+stem*.20
        foot = -224+bar/2
        g.add((right+(right-junction)*stem/510,520+stem),(junction,10),
              (junction-(right-junction)*.33,-160,tail+66,foot,tail+16,foot),
              (tail+9,foot,tail+3,foot+1,tail,foot+2))
        path.addPath(g.path.transform(1,0,0,bar/stem))
    else:
        raise ValueError(name)
    # Each independent segment must be positive ink before adding it:
    # in a crossing, reversed polygon winding would remove the overlap.
    filled = pathops.Path()
    for c in path.contours:
        filled = pathops.op(filled,c,pathops.PathOp.UNION)
    if name == "y":
        limit = pathops.Path()
        pen = limit.getPen()
        pen.moveTo((-advance,-300))
        pen.lineTo((advance*2,-300))
        pen.lineTo((advance*2,520))
        pen.lineTo((-advance,520))
        pen.closePath()
        filled = pathops.op(filled, limit, pathops.PathOp.INTERSECTION)
    filled.simplify(clockwise=True)
    return filled
