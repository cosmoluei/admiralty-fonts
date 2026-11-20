"""Draw the paired bowls, their link, the double-storey a and the cursive a/g."""
import math

import pathops

from compatible import Contour, OutlinePen, mapped_landmarks, ordered_contours
from accent_masters import tracks_for
from design_system import humanist_oval_contour
from stroke_geometry import stroke


def oval(cx, cy, rx, ry):
    p = pathops.Path()
    humanist_oval_contour(cx, cy, rx, ry, .565, .575, clockwise=True).draw_to_pen(p.getPen())
    return p


def two_storey_g(scale, weight):
    stem = {100: 24, 400: 90, 900: 128}[weight]
    hair = {100: 18, 400: 48, 900: 66}[weight]
    top = (264*scale, 363, 188*scale, 167)
    loop = (288*scale, -66, 230*scale, 158)
    def bowl(outer, side, crown):
        x, y, rx, ry = outer
        inner = oval(x, y, rx-side, ry-crown)
        return pathops.op(oval(*outer), inner, pathops.PathOp.DIFFERENCE)
    side = min(stem, top[2]*.61)
    lower_side = min(stem*.92, loop[2]*.60)
    upper = bowl(top, side, hair)
    lower = bowl(loop, lower_side, hair)
    def middle(outer, side, angle):
        x, y, rx, ry = outer
        a = math.radians(angle)
        return complex(x+(rx-side/2)*math.cos(a), y+(ry-hair/2)*math.sin(a))
    start = middle(top, side, 234)
    end = middle(loop, lower_side, 125)
    reach = min(72, max(27, .26*top[2]))
    fall = start.imag-end.imag
    link = stroke([[start, start+complex(-reach, -.29*fall), end+complex(-reach, .29*fall), end]],
                {100: 19, 400: 58, 900: 84}[weight])
    path = pathops.op(pathops.op(upper, link, pathops.PathOp.UNION), lower, pathops.PathOp.UNION)
    # A level top, one small pear at the tip, and a short return inside
    # the upper bowl. The two-storey g keeps its independent ear at Thin.
    ear = pathops.Path()
    cx, cy, rx, ry = top
    tip = 500*scale
    radius = {100: 14, 400: 35, 900: 43}[weight]
    cap = cy+ry
    ear.moveTo(cx, cap)
    ear.lineTo(tip, cap)
    ear.cubicTo(tip+.56*radius, cap, tip+radius, cap-.44*radius, tip+radius, cap-radius)
    ear.cubicTo(tip+radius, cap-1.57*radius, tip+.53*radius, cap-2*radius, tip, cap-2*radius)
    ear.cubicTo(tip-.58*radius, cap-2*radius, tip-.60*radius, cap-1.22*radius, tip-1.22*radius, cap-1.22*radius)
    ear.cubicTo(cx+.95*rx, cap-1.22*radius, cx+.76*rx, cap-1.44*radius, cx+.66*rx, cap-1.68*radius)
    ear.lineTo(cx, cap)
    ear.close()
    # Only the outside of the bowl receives the ear; leave the eye untouched.
    ear = pathops.op(ear, oval(cx, cy, rx, ry), pathops.PathOp.DIFFERENCE)
    return pathops.op(path, ear, pathops.PathOp.UNION)


def binocular_tracks(design, name, cells):
    ref = OutlinePen(None)
    design.regular.getGlyphSet()[name].draw(ref)
    shapes = []
    for w, d in cells:
        if (w, d) == (400, 100):
            shapes.append(ref.contours)
        else:
            sx, _ = design.transform(name, w, d)
            p = OutlinePen(None)
            for part in two_storey_g(sx, w).contours:
                if abs(part.area) > .05:
                    part.draw(p)
            shapes.append(ordered_contours(ref.contours, p.contours))
    return tracks_for(ref.contours, shapes, cells, {100: 4, 400: 12, 900: 18})


def a_landmarks(nodes, scale, w, italic, descender=False):
    stem = {100: 24, 400: 90, 900: 130}[w]
    hair = {100: 18, 400: 48, 900: 66}[w]
    if italic:
        left = 48*scale
        post = 403*scale
        l, r = post-stem/2, post+stem/2
        crown = 228*scale
        floor = 224*scale
        old = [(224, -10), (228, 530), (48, 256), (242, 42), (146, 258), (242, 480), (362, 394), (362, 125),
             (362, 520), (362, 464)]
        new = [(floor, -10), (crown, 530), (left, 256), (floor+8, -10+hair), (left+stem, 258),
             (crown+6, 530-hair), (l, 396), (l, 124), (l, 520), (l, 469)]
        if descender:
            toe = 104*scale
            t = {100: 13, 400: 40, 900: 57}[w]
            old += [(362, 48), (362, 6), (226, -172), (124, -120), (84, -162), (226, -222), (452, 8), (452, 520)]
            new += [(l, 48), (l, 4), (226*scale, -222+hair), (toe+t/2, -141+t/2),
                    (toe-t/2, -141-t/2), (226*scale, -222), (r, 8), (r, 520)]
        else:
            span = max(46, (522-446)*scale)
            toe = r+span
            t = {100: 12, 400: 26, 900: 42}[w]
            old += [(367, 53), (432, -10), (522, 62), (496, 80), (468, 50), (446, 128), (446, 520)]
            new += [(l, 52), (r+.18*span, -10), (toe, 59), (toe-t, 59+.68*t),
                    (r+.42*span, -10+hair), (r, 130), (r, 520)]
    else:
        lft = 48*scale
        right = 433*scale+stem/2; wall = right-stem
        floor = 204*scale
        crown = 264*scale
        bulb = 114*scale
        bead = {100: 17, 400: 43, 900: 55}[w]
        toe = right+max(35, 55*scale)
        old = [(204, -10), (390, 66), (464, -10), (532, 14), (526, 44), (516, 42), (478, 118), (478, 356),
             (268, 530), (70, 418), (114, 376), (156, 418), (260, 482), (388, 360), (388, 310), (48, 132),
             (220, 38), (140, 134), (388, 262), (388, 136)]
        new = [(floor, -10), (wall+2, 65), (right-.12*stem, -10), (toe, 14), (toe-.18*hair, 14+.73*hair),
             (right+.72*(toe-right), 12+.68*hair), (right, 118), (right, 356),
             (crown, 530), (bulb-bead, 418), (bulb, 418-bead), (bulb+bead, 418),
             (crown-3, 530-hair), (wall, 360), (wall, 286+hair/2), (lft, 132),
             (floor+.13*stem, -10+hair), (lft+stem, 134), (wall, 286-hair/2), (wall, 136)]
    return mapped_landmarks(nodes, old, new)


def joined_bowls(nodes, name, scale, weight, italic):
    """The two eyes of ae/oe share a wall. Size that wall before either eye."""
    a = name == 'ae'
    stem = {100: 24, 400: 90, 900: 126}[weight]
    hair = {100: 18, 400: 48, 900: 66}[weight]
    joint = (423 if a else 433)*scale
    left = 48*scale
    wall, back = joint-stem/2, joint+stem/2
    if italic:
        crown, right, tip = (600, 814, 788) if a else (624, 836, 810)
        bar0, bar1 = 235, 312
        lower = 74 if a else 68
        upper = 372 if a else 434
        old = [(224 if a else 260, -10), (382 if a else 426, lower), (410 if a else 442, lower),
             (602 if a else 626, -10), (804 if a else 826, 92), (772 if a else 794, 124),
             (610 if a else 634, 38), (462 if a else 488, 212), (right, 294), (right, 304), (crown, 530)]
    else:
        crown, right, tip = (610, 808, 784) if a else (618, 814, 790)
        bar0 = bar1 = 264
        lower, upper = 76, 444
        old = [(208 if a else 250, -10), (420 if a else 430, lower), (426 if a else 436, lower),
             (616 if a else 622, -10), (800 if a else 806, 94), (768 if a else 774, 124),
             (618 if a else 624, 38), (472 if a else 478, 240), (right, 240), (right, 276), (crown, 530)]
    floor = (211 if a else 256)*scale
    cx = crown*scale
    toe = {100: 10, 400: 32, 900: 45}[weight]
    gap = {100: 102, 400: 76, 900: 62}[weight]
    neck = {100: 395, 400: 444, 900: 445}[weight]
    new = [(floor, -10), (joint-2, gap), (joint+2, gap), (cx+5, -10),
         (tip*scale+toe/2, 109-toe/2), (tip*scale-toe/2, 109+toe/2),
         (cx+6, -10+hair), (back, bar0-hair/2), (right*scale, bar1-hair/2),
         (right*scale, bar1+(3 if italic else .25*hair)), (cx, 530)]
    if italic and a:
        old.extend([(466, upper), (466, 520), (380, 520)])
        new.extend([(back, neck-35), (back, 520), (wall, 520)])
    else:
        j0, j1 = (420, 426) if a else ((426, 442) if italic else (430, 436))
        old.extend([(j1, upper), (j0, upper)])
        new.extend([(joint+2, neck), (joint-2, neck)])
    if a and not italic:
        bead = {100: 17, 400: 43, 900: 55}[weight]
        bulb = 114*scale
        old.extend([(262, 530), (70, 418), (114, 376), (156, 418), (254, 482), (382, 356),
                    (382, 310), (48, 132), (222, 38), (140, 134), (382, 262), (382, 136)])
        new.extend([(260*scale, 530), (bulb-bead, 418), (bulb, 418-bead), (bulb+bead, 418),
                    (260*scale-3, 530-hair), (wall, 356), (wall, 286+hair/2), (left, 132),
                    (floor+5, -10+hair), (left+stem, 134), (wall, 286-hair/2), (wall, 141)])
    else:
        x, side = (228, 48) if a else ((260, 46) if italic else (250, 48))
        cy = 256 if a else 260
        ix, iy = (242, 42) if a else ((264, 38) if italic else (268, 38))
        inner_x = 362 if a else (388 if italic else 390)
        old.extend([(x, 530), (side, cy), (ix, iy), (146, 258 if a else 260),
                    (ix, 480 if a else 482), (inner_x, 338 if italic else 340),
                    (inner_x, 178 if a else (182 if italic else 180))])
        new.extend([(x*scale, 530), (left, cy), (floor+6, -10+hair), (left+stem, cy),
                    (x*scale+4, 530-hair), (wall, 357), (wall, 159)])
    if italic:
        eye_old = [(520, 272), (616, 476), (724, 326)] if a else [(494, 264), (628, 482), (748, 326)]
        eye_new = [(back+3, bar0+hair/2), (cx+3, 530-hair), (right*scale-.9*stem, bar1+hair/2-10)]
    else:
        eye = 472 if a else 478
        eye_old = [(eye, 288), (eye, 344), (604 if a else 612, 482), (726 if a else 734, 288)]
        eye_new = [(back, bar0+hair/2), (back, 344), (cx+2, 530-hair), (right*scale-.90*stem, bar1+hair/2)]
    return mapped_landmarks(nodes, old + eye_old, new + eye_new)


def joint_curves(ring, curve, name):
    """Match the tangent of each eye and the adjoining arch at their shared upright."""
    joint = (423 if name == 'ae' else 433)
    original = ring.pieces
    pieces = curve.pieces.copy()
    for i, (a, _, _, b) in enumerate(original):
        # A quadrant has one horizontal extremum and another end on
        # the central shaft. A cut, beak, or bar remains a separate segment.
        def apex(p, q):
            return (min(abs(p.imag-y) for y in (-10, 38, 42, 476, 480, 482, 530)) < 1
                    and abs(p.real-joint) > 92 and abs(q.real-joint) < 110
                    and abs(q.imag-p.imag) > 38 and abs(q.real-p.real) > 45)
        if apex(a, b):
            start, end = pieces[i, 0], pieces[i, 3]
            step = end-start
            pieces[i, 1] = start+.56*step.real
            pieces[i, 2] = end-.56j*step.imag
        elif apex(b, a):
            start, end = pieces[i, 0], pieces[i, 3]
            step = end-start
            pieces[i, 1] = start+.56j*step.imag
            pieces[i, 2] = end-.56*step.real
    return Contour(pieces)


def thin_bowl(nodes, targets, name, scale, italic):
    # Locate both rims of b/d/p/q from their shared shaft. The open side of
    # the bowl gets 24 units and the crowns 18, as on o. At the junction
    # the outer branch starts higher than its mate, leaving a clear notch.
    forward = name in ('b', 'p')
    inner, outer = ((164, 72) if forward else
                    (396, 484) if italic and name == 'd' else (412, 504))
    sign = 1 if forward else -1
    shaft = (inner + outer) / 2 * scale
    wall = shaft + sign * 12
    belly = (528 if forward else 46 if italic and name == 'd' else 48) * scale
    middle = (326 if forward else 242 if italic and name == 'd' else 250) * scale
    for i, z in enumerate(nodes):
        x, y = z.real, z.imag
        if abs(x-inner) < 1:
            targets.real[i] = wall
        if abs(x-outer) < 1:
            targets.real[i] = shaft - sign * 12
        if 310 < y < 352 and abs(x-inner) < 2:
            targets[i] = wall + 340j
        elif 160 < y < 200 and abs(x-inner) < 2:
            targets[i] = wall + 180j
        elif 33 < y < 55 and abs(x-inner) < 14:
            targets[i] = wall + 117j
        elif 435 < y < 485 and abs(x-inner) < 4:
            targets[i] = wall + 403j
        elif abs(y-260) < 1:
            flank = abs(x-(528 if forward else 46 if italic and name == 'd' else 48)) < 3
            targets[i] = (belly if flank else belly-sign*24) + 260j
        elif abs(x-inner) > 34 and abs(x-outer) > 27 and abs(x-middle/scale) < 40:
            heights = {-10: -10, 38: 8, 482: 512, 530: 530}
            for old, new in heights.items():
                if abs(y-old) < 1:
                    inset = sign*4 if old in (38, 482) else 0
                    targets[i] = middle-inset + 1j*new
    return targets


def shoulder_curves(source, drawing):
    # Flat tangent at the apex, vertical tangent at the shaft. Pairing
    # those directions on both sides prevents a hairline from disappearing
    # halfway through an arch, even when its span doubles.
    pieces = drawing.pieces.copy()
    for index, (a, _, _, b) in enumerate(source.pieces):
        def crown_to_joint(p, q):
            return (min(abs(p.imag-y) for y in (-10, 38, 482, 530)) < 1
                    and (32 < q.imag < 205 or 310 < q.imag < 490)
                    and abs(q.real-p.real) > 70)
        if crown_to_joint(a, b):
            start, end = pieces[index, 0], pieces[index, 3]
            delta = end-start
            pieces[index, 1] = start+.56*delta.real
            pieces[index, 2] = end-.56j*delta.imag
        elif crown_to_joint(b, a):
            start, end = pieces[index, 0], pieces[index, 3]
            delta = end-start
            pieces[index, 1] = start+.56j*delta.imag
            pieces[index, 2] = end-.56*delta.real
    return Contour(pieces)


def thin_head(nodes, targets, left, right, top, scale):
    """Keep the cap, flag and its bracket on the same side of the shaft."""
    middle = (left+right)*scale/2
    for i, z in enumerate(nodes):
        x, y = z.real, z.imag
        if abs(x-right) < 1 and abs(y-top) < 1:
            targets[i] = middle+12+1j*top
        elif top+8 < y < top+16 and abs(x-right) < 22:
            targets[i] = middle+6+1j*(top+12)
        elif x < left-3 and top-65 < y < top:
            targets[i] = middle-12-(left-x)*.64*scale**.4+1j*(top-10-(top-22-y)*.47)
        elif abs(x-left) < 1 and top-85 < y < top-60:
            targets[i] = middle-12+1j*(top-51)
    return targets


def thin_arch(nodes, targets, name, scale, italic):
    if name == 'm':
        spans = ((62, 148), (378, 462), (690, 760)) if italic else ((72, 160), (396, 484), (720, 808))
    else:
        spans = ((64, 154), (388, 462)) if italic else ((74, 166), (418, 510))
    for left, right in spans:
        mid = (left+right)*scale/2
        targets.real[abs(nodes.real-left) < .6] = mid-12
        targets.real[abs(nodes.real-right) < .6] = mid+12
    left, right = spans[0]
    # The first arch departs from the right edge just below the head flag.
    join = (abs(nodes.real-right) < 3) & (nodes.imag > 450) & (nodes.imag < 475)
    targets.real[join] = (left+right)*scale/2+12
    targets.imag[join] = 398
    if name == 'm':
        valley = abs(nodes.imag-434) < 1
        targets.real[valley] = sum(spans[1])*scale/2
    return thin_head(nodes, targets, left, right, 740 if name == 'h' else 520, scale)


def thin_italic_exit(nodes, targets, name, scale):
    # The cursive exit turns on the baseline before rising to its angled cut.
    # Both edges of that cut are drawn together to keep a wide italic from
    # developing a flat wedge or a backwards-pointing foot.
    spans = {'h': (388, 462), 'n': (388, 462), 'm': (690, 760), 'u': (384, 472),
           'd': (396, 484), 'r': (66, 152), 'i': (66, 152), 'l': (66, 154)}
    left, right = spans[name]
    mid = (left+right)*scale/2
    l, r = mid-12, mid+12
    span = max(50, (80 if name in 'hnm' else 72)*scale**.65)
    for i, z in enumerate(nodes):
        x, y = z.real, z.imag
        if x < left-1 or y > 145: continue
        if abs(x-right) < 1 and abs(y-128) < 2:
            targets[i] = r+118j
        elif abs(x-left) < 1 and 90 < y < 113:
            targets[i] = l+108j
        elif x > right-17 and abs(y+10) < 1:
            targets[i] = r+.24*span-10j
        elif x > right+58 and 53 < y < 65:
            targets[i] = r+span+41j
        elif x > right+30 and 68 < y < 81:
            targets[i] = r+span-9+55j
        elif x > right+10 and 36 < y < 53:
            targets[i] = r+.34*span+8j
    return targets
