"""Material landmarks at the ends of the F arms and the kip's diagonals."""

import numpy as np

from compatible import Contour


def stations(reference, anchors):
    points = reference.pieces[:, 0]
    distances = abs(points[:, None] - np.array([complex(x, y) for x, y in anchors]))
    indices = distances.argmin(axis=0)
    if indices[0] != 0 or np.any(np.diff(indices) <= 0) or distances.min(axis=0).max() > 2:
        raise ValueError("Serif outline no longer matches its design landmarks")
    return np.r_[reference.knots[indices], 1.]


def italic_f(reference, scale, shift):
    stem = 89.5 * scale + shift
    left, right = stem - 12, stem + 12
    reach = min(77, stem - (-9 * scale + shift))
    top = 476 * scale + shift
    middle = top - 45 * scale
    bracket = min(32, 31 * scale**0.5)
    segments = []
    start = complex(stem + reach, 0)
    def line(x, y):
        a = segments[-1][-1] if segments else start
        b = complex(x, y)
        segments.append([a, (2*a+b)/3, (a+2*b)/3, b])
    def curve(x1, y1, x2, y2, x, y):
        segments.append([segments[-1][-1], complex(x1,y1), complex(x2,y2), complex(x,y)])
    # The stem and the two arms have distinct thicknesses. Brackets leave
    # the bar horizontally and meet the terminal vertically on both sides.
    line(stem-reach, 0)
    line(stem-reach, 9)
    curve(left-9, 9, left, 15, left, 30)
    line(left, 670)
    curve(left, 685, left-9, 691, stem-reach, 691)
    line(stem-reach, 700)
    line(top-2, 700)
    line(top, 647)
    line(top-12, 647)
    curve(top-12, 674, top-12-.42*bracket, 683, top-12-bracket, 683)
    line(right, 683)
    line(right, 377)
    line(middle-12-bracket, 377)
    curve(middle-12-.40*bracket, 377, middle-12, 387, middle-12, 403)
    line(middle, 403)
    line(middle, 335)
    line(middle-12, 335)
    curve(middle-12, 351, middle-12-.40*bracket, 361, middle-12-bracket, 361)
    line(right, 361)
    line(right, 30)
    curve(right, 15, right+9, 9, stem+reach, 9)
    line(start.real, 0)
    ring = Contour(segments)
    anchors = [(197,0),(-9,0),(-9,30),(38,64),(39,636),(-9,670),(-9,700),
               (469,700),(476,542),(440,542),(357,650),(141,650),(140,375),
               (340,375),(397,438),(431,438),(431,262),(397,262),(341,325),
               (141,325),(140,64),(197,30)]
    return ring, stations(reference, anchors), ring.knots


def kip(reference, ring):
    if ring.area * reference.area < 0:
        ring = Contour(ring.pieces[::-1, ::-1])
    nodes = ring.pieces[:, 0]
    if len(nodes) == 3:
        ring = ring.roll(np.argmin(nodes.real))
        return ring, reference.knots, ring.knots
    # Start at the right edge of the stem foot. Match the straight-to-curve
    # tangencies on BOTH diagonals before sampling the fillets or widths.
    feet = np.flatnonzero(abs(nodes.imag) < .01)
    ring = ring.roll(feet[np.argsort(nodes[feet].real)[1]])
    nodes = ring.pieces[:, 0]
    material = abs(nodes - np.roll(nodes, 1)) > .1
    anchors = [(224,0),(36,0),(36,30),(80,64),(80,319),(6,319),(6,381),(80,381),
               (80,636),(36,670),(36,700),(224,700),(224,670),(182,636),(182,408),
               (398,622),(390,670),(390,700),(576,700),(576,670),(458,611),(296,456),
               (343,381),(594,381),(594,319),(381,319),(524,90),(604,30),(604,0),
               (412,0),(412,30),(420,84),(283,319),(182,319),(182,64),(224,30)]
    b = np.r_[ring.knots[:-1][material], 1.]
    a = stations(reference, anchors)
    if len(a) != len(b):
        raise ValueError("Kip ribbon has a different number of material stations")
    return ring, a, b
