"""Monoline Sans word-study masters. All dimensions are in units of a 1000-unit em."""
import pathops

from stroke_geometry import emit, fair_curves, fit_edge, round_branches, stroke

LETTERS = "adegilmnsu"


class Drawing:
    def __init__(self, origin, span, thickness, vertical_ratio=1.0):
        self.origin = origin
        self.span = span
        self.thickness = thickness
        self.vertical_ratio = vertical_ratio
        self.path = pathops.Path()
        self.spines = []

    def add(self, start, *segments):
        """X spans the letter's centreline box; Y is an absolute design coordinate."""
        def point(x, y):
            return complex(self.origin + self.span*x, y / self.vertical_ratio)
        cursor = point(*start)
        pieces = []
        for coords in segments:
            controls = [point(x, y) for x, y in zip(coords[::2], coords[1::2])]
            pieces.append((cursor, *controls))
            cursor = controls[-1]
        self.spines.append(pieces)
        self.path.addPath(stroke(pieces, self.thickness))

    def dot(self, x, y):
        radius = self.thickness/2
        cx = self.origin + self.span*x
        pen = self.path.getPen()
        handle = .55228475 * radius
        pen.moveTo((cx+radius,y))
        pen.curveTo((cx+radius,y+handle),(cx+handle,y+radius),(cx,y+radius))
        pen.curveTo((cx-handle,y+radius),(cx-radius,y+handle),(cx-radius,y))
        pen.curveTo((cx-radius,y-handle),(cx-handle,y-radius),(cx,y-radius))
        pen.curveTo((cx+handle,y-radius),(cx+radius,y-handle),(cx+radius,y))
        pen.closePath()


def contour_sides(pen, x, y):
    """Start a contour and draw consecutive sides with curvature-matched segments."""
    pen.moveTo((x, y))
    cursor = complex(x, y)

    def side(*segments):
        nonlocal cursor
        pieces = []
        for points in segments:
            controls = tuple(complex(x, y) for x, y in zip(points[::2], points[1::2]))
            pieces.append((cursor, *controls))
            cursor = controls[-1]
        for curve in fair_curves(pieces):
            for cubic in fit_edge(curve, 0):
                emit(pen, cubic)
    return side


def draw_black_m(drawing, width):
    """Place the outer crotch and the two inner shoulders independently."""
    stem = drawing.thickness
    left = drawing.origin - stem/2
    right = drawing.origin + drawing.span + stem/2
    middle = drawing.origin + .494*drawing.span
    r1, l2 = middle + stem/2, middle - stem/2
    left_cap = left + .91*stem
    notch = middle + .34*stem
    first_peak = left + stem/2 + .573*(middle - drawing.origin)
    last_peak = middle + .564*(drawing.origin + drawing.span - middle)
    dip = {65: 415, 100: 420, 150: 426}[width]
    side_height = {65: 320, 100: 329, 150: 340}[width]
    pen = drawing.path.getPen()
    side = contour_sides(pen, left, 0)

    # Keep the cap, the central crotch, and the tops of the two counters
    # separately located. The right arch can then rise from the centre stem
    # without filling the wedge between the two shoulders.
    side((left, 520))
    side((left_cap, 520))
    side((left_cap + 2, dip + 7))
    side((left_cap+21, dip+52, first_peak-48, 530, first_peak, 530),
         (first_peak+.54*(notch-first_peak), 530, notch-18, dip+55, notch, dip))
    side((notch+21, dip+55, last_peak-.49*(last_peak-notch), 530, last_peak, 530),
         (last_peak+.60*(right-last_peak), 530, right, side_height+110, right, side_height),
         (right, 0))
    side((right-stem, 0))

    def counter(right_edge, left_edge, center, crown, entry, exit_height):
        side((right_edge, entry),
             (right_edge, entry+.58*(crown-entry), center+.55*(right_edge-center), crown, center, crown),
             (center-.50*(center-left_edge), crown, left_edge, exit_height+.54*(crown-exit_height), left_edge, exit_height),
             (left_edge, 0))

    counter(right-stem, r1, last_peak-15, 415, side_height-17, side_height+2)
    side((l2, 0))
    counter(l2, left+stem, first_peak-15, 414, side_height-18, side_height+1)
    pen.closePath()


def draw_black_a(drawing, width):
    # The Regular has a high right attachment and a bowl that opens diagonally
    # to the left. Shape the waist and the lower counter independently at Black.
    stem = drawing.thickness
    left = drawing.origin - stem/2
    extent = drawing.span + stem
    right = left + extent
    post = right - stem
    x = lambda fraction: left + extent*fraction
    upper_join = {65: 318, 100: 319, 150: 322}[width]
    counter_top = upper_join - 85
    arch = x(.510)
    upper_tip = x({65: .077, 100: .081, 150: .094}[width])
    lower_tip = upper_tip + 28
    bottom = x({65: .405, 100: .397, 150: .392}[width])
    flank = left + {65: 112, 100: 120, 150: 125}[width]
    inside_floor = 87
    pen = drawing.path.getPen()

    # Outer ink contour, from the foot up around the shoulder and into the waist.
    side = contour_sides(pen, right, 0)
    side((right, 346),
         (right, 452, arch+.282*extent, 530, arch, 530),
         (x(.329), 530, upper_tip+.078*extent, 510, upper_tip, 475))
    side((lower_tip, 389))
    side((lower_tip+.085*extent, 415, x(.376), 430, arch-7, 430),
         (arch+.15*extent, 430, post, 388, post, 342),
         (post, upper_join))
    side((post-.29*extent, upper_join-4, left, 253, left, 142),
         (left, 49, bottom-.19*extent, -10, bottom, -10),
         (bottom+.15*extent, -10, post-.061*extent, 20, post+7, 67))
    side((post+10, 0))
    pen.closePath()

    # Lower counter, with a vertical right wall and an oblique upper edge.
    side = contour_sides(pen, post, counter_top)
    side((post, 155),
         (post, 121, bottom+.19*extent, inside_floor, bottom+.035*extent, inside_floor),
         (bottom-.043*extent, inside_floor, flank, 112, flank, 144),
         (flank, 198, post-.24*extent, counter_top-5, post, counter_top))
    pen.closePath()


def draw_thin_a(drawing, high, low, width):
    tip = {65: .065, 100: .073, 150: .088}[width]
    reach = min(.13*drawing.span, 51)
    crown = .495
    tip_height = {65: 456, 100: 448, 150: 444}[width]
    slope = 1.72*(high-tip_height) / ((crown-tip)*drawing.span)
    drawing.add((tip, tip_height),
        (tip+reach/drawing.span, tip_height+slope*reach, .323, high, crown, high),
        (.789, high, 1, 441, 1, 348),
        (1, 0))
    foot = {65: .392, 100: .383, 150: .378}[width]
    # A single sweep climbs from the left flank to the stem at the waist.
    drawing.add((1, 285),
        (.616, 277, -.052, 231, -.052, 145),
        (-.052, 59, foot-.235, low, foot-.045, low),
        (.622, low, .922, 67, 1, 123))


def draw_thin_m(add, high, height, width):
    # The first arch comes out of a capped stem. The second one branches
    # from a curved shoulder, as it does in the Regular outline.
    add((0, 0), (0, 520))
    middle = .492
    departures = {65: (.32, .35), 100: (.32, .32), 150: (.31, .29)}[width]
    descents = (.35, .39)
    for start, end, apex, rise, fall in zip(
        (0, middle), (middle, 1), (.55, .53), departures, descents
    ):
        span = end - start
        add((start, high - rise * height),
            (start + .055*span, high - .55*rise*height,
             start + (apex-.28)*span, high, start + apex*span, high),
            (start + (apex+.275)*span, high,
             end, high - .44*fall*height, end, high - fall*height),
            (end, 0))


def draw_e(add, high, low, radius_y, weight, width, span):
    height = high - low
    bar = {65: 266, 100: 265, 150: 258}[width] if weight == 100 else {65: 258, 100: 253, 150: 246}[width]
    # Keep the cut angled and let the lower lip draw back from the crossbar.
    tip = {65: .91, 100: .93, 150: .94}[width] if weight == 100 else {65: .85, 100: .89, 150: .89}[width]
    lift = {65: 71, 100: 78, 150: 85}[width] if weight == 100 else {65: 48, 100: 55, 150: 59}[width]
    tip_slope = .83 if weight == 100 else .77
    end_handle = min(.11*span, .53*lift/tip_slope)
    add((0, bar), (1, bar))
    add((1, bar-radius_y), (1, bar+10),
        (1, high-.22*height, .77, high, .515, high),
        (.22, high, 0, high-.23*height, 0, low+.505*height),
        (0, low+.225*height, .212, low, .53, low),
        (.69, low, tip-end_handle/span, low+lift-tip_slope*end_handle, tip, low+lift))


def draw_g(add, high, low, radius_y, weight, width, span):
    height = high - low
    # Place the single-storey bowl left of the stem. Leave a short upper spur
    # and a straight side inside the counter before the lower bowl turns in.
    add((1, low+.635*height),
        (.90, low+.85*height, .70, high, .44, high),
        (.187, high, 0, low+.79*height, 0, low+.50*height),
        (0, low+.205*height, .176, low, .421, low),
        (.69, low, .897, low+.145*height, 1, low+.355*height))
    floor = -224 + radius_y
    tip = {65: .045, 100: .075, 150: .145}[width]
    lift = {65: 37, 100: 40, 150: 49}[width] + (3 if weight == 900 else 0)
    handle = min(.15*span, 49)
    add((1, 520), (1, -19),
        (1, -105, .755, floor, .463, floor),
        (.318, floor, tip+handle/span, floor+lift-.48*handle, tip, floor+lift))


def draw_d_bowl(add,high,low):
    h=high-low
    add((1,low+.72*h),
        (.87,low+.90*h,.73,high,.51,high),
        (.20,high,0,low+.80*h,0,low+.49*h),
        (0,low+.19*h,.19,low,.49,low),
        (.73,low,.89,low+.12*h,1,low+.29*h))


def draw_s(add, high, low, weight, width, span):
    height = high - low
    # Trace both lobes in order. The upper bowl sits farther right and is
    # smaller; the waist runs into a fuller lower bowl and a longer terminal.
    slope = {65: .57, 100: .42, 150: .32}[width]
    waist_in = .18
    if weight == 100:
        top_side, bottom_side = .755, .253
        top_drop, bottom_lift = .128, .126
        upper_in, upper_out, lower_in, lower_out = .137, .148, .144, .140
        if width==150:
            # Carry the waist into the lower bowl over a longer turning
            # distance. The terminals and the 24-unit physical pen stay put.
            slope,waist_in=.224,.175
            upper_in,upper_out,lower_in,lower_out=.138,.178,.176,.149
    else:
        top_side, bottom_side = .765, .255
        top_drop, bottom_lift = .101, .116
        upper_in, upper_out, lower_in, lower_out = {
            65:  (.129, .140, .137, .132),
            100: (.124, .150, .165, .120),
            150: (.122, .191, .204, .120),
        }[width]
    add((.918, high-top_drop*height),
        (.818, high-.047*height, .695, high, .525, high),
        (.279, high, .065, low+(top_side+upper_in)*height, .065, low+top_side*height),
        (.065, low+(top_side-upper_out)*height,
         .51-waist_in, low+.51*height+waist_in*span*slope, .51, low+.51*height),
        (.70, low+.51*height-.19*span*slope,
         .981, low+(bottom_side+lower_in)*height, .981, low+bottom_side*height),
        (.981, low+(bottom_side-lower_out)*height, .745, low, .463, low),
        (.275, low, .131, low+.047*height, .022, low+bottom_lift*height))


def draw_letter(name, advance, weight, width):
    thick = 24 if weight == 100 else 128
    r = thick / 2
    side = ({65: 40, 100: 59, 150: 82} if weight == 100 else {65: 30, 100: 46, 150: 57})[width]
    side += 5 if name in "mnu" else 0
    left = side+r
    span = advance-2*left
    if name == "i":
        left, span = advance/2, 1
    if name == "l":
        left, span = .30*advance if weight == 100 else side+r, 1
    # A Black cross-stroke is optically heavier at the same geometric width.
    # Values describe the vertical diameter of the pen; stems retain 128.
    horizontal = {"e": 101, "g": 109, "s": 106}.get(name, thick) if weight == 900 else thick
    g = Drawing(left, span, thick, horizontal / thick)
    add = g.add
    high, low = 530-horizontal/2, -10+horizontal/2
    h = high-low

    if name == "m" and weight == 900:
        draw_black_m(g, width)
    elif name == "m":
        draw_thin_m(add, high, h, width)
    elif name in "nu":
        add((0,0), (0,520))
        rise = {65: .38, 100: .40, 150: .44}[width] * h
        descent = .42 if weight == 900 else .33
        add((0,high-rise),
            (.08, high-.44*rise, .31,high, .57,high),
            (.87, high, 1, high-.5*descent*h, 1,high-descent*h),
            (1, 0))
    elif name == "g":
        draw_g(add, high, low, horizontal/2, weight, width, span)
    elif name == "d":
        add((1,740),(1,0))
        draw_d_bowl(add,high,low)
    elif name == "a" and weight == 900:
        draw_black_a(g, width)
    elif name == "a":
        draw_thin_a(g, high, low, width)
    elif name == "e":
        draw_e(add, high, low, horizontal/2, weight, width, span)
    elif name == "s":
        draw_s(add, high, low, weight, width, span)
    elif name == "l":
        foot = ({65: 39, 100: 56, 150: 69} if weight == 100 else {65: 100, 100: 133, 150: 150})[width]
        add((0,740),(0,low+foot*1.22),
            (0,low+.46*foot,.39*foot,low,foot,low))
    elif name == "i":
        add((0,0),(0,520))
        g.dot(0, 654 if weight == 100 else 666)
    else:
        raise ValueError(name)
    return g


def letter_outline(name, advance, weight, width):
    drawing = draw_letter(name, advance, weight, width)
    path = drawing.path
    path.simplify(clockwise=True)
    # The Black m already has an explicit crotch. Round only the last few
    # units at its floor, retaining the depth and direction of the two flanks.
    blend = {"m": 33, "a": 27}.get(name, drawing.thickness) if weight == 900 else drawing.thickness
    path = round_branches(path, blend)
    if name == "u":
        return path.transform(-1, 0, 0, -1, advance, 520)
    if drawing.vertical_ratio != 1:
        return path.transform(1, 0, 0, drawing.vertical_ratio)
    return path
