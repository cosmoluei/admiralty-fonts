"""Draw the bowls and shoulders that share the reviewed d/n proportions."""
from study_shapes import Drawing, letter_outline

RELATED = "bchopqr"


def related_outline(name, advance, weight, width):
    if name in "bpq":
        # d's upper/lower overshoots are 530 and -10; reflecting about
        # the x-height midpoint also places the descender at -220.
        flip_x, flip_y = name in "bp", name in "pq"
        return letter_outline("d", advance, weight, width).transform(
            -1 if flip_x else 1, 0, 0, -1 if flip_y else 1,
            advance if flip_x else 0, 520 if flip_y else 0)
    thick = 24 if weight == 100 else 128
    horizontal = 24 if weight == 100 else {"c": 106, "o": 106, "r": 110, "h": 128}[name]
    side = ({65: 40, 100: 59, 150: 82} if weight == 100 else {65: 30, 100: 46, 150: 57})[width]
    if name in "hr":
        side += 5
    if name == "r":
        # The open end has a smaller right sidebearing than a stem.
        span = max(thick*.80, advance-1.42*side-.5*thick)
    else:
        span = advance-2*side-thick
    g = Drawing(side+thick/2, span, thick, horizontal/thick)
    hi, lo = 530-horizontal/2, -10+horizontal/2
    h = hi-lo
    mid = (hi+lo)/2

    if name == "h":
        # The same shoulder as n, with a full-height left stem.
        g.add((0,0),(0,740))
        rise = {65: .38, 100: .40, 150: .44}[width]*h
        fall = (.42 if weight == 900 else .33)*h
        g.add((0,hi-rise),(.08,hi-.44*rise,.31,hi,.57,hi),
              (.87,hi,1,hi-.5*fall,1,hi-fall),(1,0))
    elif name == "r":
        g.add((0,0),(0,520))
        g.add((0,hi-.47*h),(.11,hi-.23*h,.43,hi,.77,hi),
              (.86,hi,.93,hi-.009*h,1,hi-.030*h))
    elif name == "c":
        g.add((.98,hi-.16*h),(.85,hi-.064*h,.69,hi,.53,hi),
              (.23,hi,0,hi-.21*h,0,mid),
              (0,lo+.21*h,.22,lo,.53,lo),
              (.71,lo,.89,lo+.078*h,1,lo+.174*h))
    elif name == "o":
        g.add((.51,hi),(.22,hi,0,hi-.207*h,0,mid),
              (0,lo+.207*h,.22,lo,.49,lo),
              (.78,lo,1,lo+.207*h,1,mid),
              (1,hi-.207*h,.78,hi,.51,hi))
    else:
        raise ValueError(name)
    g.path.simplify(clockwise=True)
    return g.path.transform(1,0,0,horizontal/thick)
