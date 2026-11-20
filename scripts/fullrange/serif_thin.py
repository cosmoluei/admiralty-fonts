"""Thin Serif drawings. Set the skeleton in design space and the pen in font units."""
from functools import lru_cache
import math

import numpy as np

import pathops

from compatible import Contour, OutlinePen
from serif_thin_stations import STATIONS

LETTERS = frozenset('ACGJKQRXYacfdkmuxy')


class ThinPen:
    def __init__(self, scale):
        self.scale = scale
        self.shape = pathops.Path()

    def add(self, path):
        self.shape = pathops.op(self.shape, path, pathops.PathOp.UNION)

    def stroke(self, start, *segments, width=24, aspect=.75, closed=False):
        # Width changes move the stations of the skeleton. Stamp the pen
        # after that move so the two sides of a curve turn together.
        path = pathops.Path()
        path.moveTo(start[0]*self.scale, start[1]/aspect)
        for seg in segments:
            coords = [v*self.scale if i % 2 == 0 else v/aspect for i, v in enumerate(seg)]
            if len(coords) == 2:
                path.lineTo(*coords)
            else:
                path.cubicTo(*coords)
        if closed:
            path.close()
        path.stroke(width, pathops.LineCap.BUTT_CAP, pathops.LineJoin.ROUND_JOIN, 4)
        path.convertConicsToQuads(.04)
        self.add(path.transform(scaleY=aspect))

    def ribbon(self, start, end, width, head=False, foot=False, start_cut=None, end_cut=None):
        x, y = start
        xx, yy = end
        slope = (xx-x)*self.scale/(yy-y)
        half = width*math.hypot(1, slope)/2
        a, b = x*self.scale, xx*self.scale
        p = pathops.Path()
        # At a branch the end cut lies on the receiving stroke's axis.
        # A horizontal butt would protrude beyond a shallow diagonal.
        def cut(x, h, offset, direction):
            delta = 0 if direction is None else offset/(direction-slope)
            return x+offset+slope*delta, h+delta
        p.moveTo(*cut(a, y, -half, start_cut))
        p.lineTo(*cut(a, y, half, start_cut))
        p.lineTo(*cut(b, yy, half, end_cut))
        p.lineTo(*cut(b, yy, -half, end_cut))
        p.close()
        self.add(p)
        for on, top in ((head, True), (foot, False)):
            if on:
                at, h = max((start, end), key=lambda z: z[1]) if top else min((start, end), key=lambda z: z[1])
                self.serif(at, h, half, slope, top)

    def serif(self, x, y, half=12, slope=0, top=False, left=1., right=1.):
        # The curve leaves each rail tangentially and flattens into the pad.
        sign = -1 if top else 1
        ext = 24*self.scale**.32
        def pt(offset, depth):
            return x*self.scale+offset+slope*depth*sign, y+depth*sign
        l = -half-left*ext
        r = half+right*ext
        p = pathops.Path()
        p.moveTo(*pt(l, 0))
        p.lineTo(*pt(r, 0))
        p.lineTo(pt(r, 0)[0], pt(r, 9)[1])
        p.cubicTo(*pt(half+.27*right*ext, 9), *pt(half, 15), *pt(half, 26))
        p.lineTo(*pt(-half, 26))
        p.cubicTo(*pt(-half, 15), *pt(-half-.27*left*ext, 9), pt(l, 0)[0], pt(l, 9)[1])
        p.close()
        self.add(p)

    def entry(self, x, y):
        # Asymmetric ascender / x-height flag, ending flush with the right rail.
        a = x*self.scale
        e = 29*self.scale**.35
        p = pathops.Path()
        p.moveTo(a+12, y)
        p.lineTo(a-12-e, y-12)
        p.lineTo(a-12-e, y-20)
        p.cubicTo(a-18, y-18, a-12, y-23, a-12, y-39)
        p.lineTo(a+12, y-39)
        p.close()
        self.add(p)

    def drop(self, x, y, rx=17, ry=18):
        # Small rounded terminal with its own optical size across wdth.
        x *= self.scale
        k = .552285
        p = pathops.Path()
        p.moveTo(x+rx, y)
        p.cubicTo(x+rx, y+k*ry, x+k*rx, y+ry, x, y+ry)
        p.cubicTo(x-k*rx, y+ry, x-rx, y+k*ry, x-rx, y)
        p.cubicTo(x-rx, y-k*ry, x-k*rx, y-ry, x, y-ry)
        p.cubicTo(x+k*rx, y-ry, x+rx, y-k*ry, x+rx, y)
        p.close()
        self.add(p)

    def exit(self, x, reach):
        self.stroke((x, 105), (x, 37, x+9, 0, x+reach*.43, 0),
                    (x+reach*.66, 0, x+reach*.86, 24, x+reach, 55))

    def rings(self):
        self.shape.simplify(clockwise=True)
        p = OutlinePen(None)
        self.shape.draw(p)
        return [ring for ring in p.contours if abs(ring.area) > .25]


def diagonals(p, name, italic):
    cap = name.isupper()
    h = 700 if cap else 520
    if name == 'A':
        # Clip the two rails to one small flat apex. The physical width of its
        # tip and the crossbar are independent of the angle between the legs.
        lx, peak, rx = 68, 320, 555
        al, ar = (peak-lx)*p.scale/h, (rx-peak)*p.scale/h
        cut = (18*math.hypot(1, al)/2+24*math.hypot(1, ar)/2-7)/(al+ar)
        # A single silhouette prevents a spur where the two strokes meet.
        l, r = lx*p.scale, rx*p.scale
        slope_l, slope_r = (peak*p.scale-l)/(h-cut), (peak*p.scale-r)/(h-cut)
        hl, hr = 9*math.hypot(1, slope_l), 12*math.hypot(1, slope_r)
        eye = (r-l-hr-hl)/(slope_l-slope_r)
        t = pathops.Path()
        t.moveTo(l-hl, 0)
        t.lineTo(l+slope_l*h-hl, h)
        t.lineTo(r+slope_r*h+hr, h)
        t.lineTo(r+hr, 0)
        t.lineTo(r-hr, 0)
        t.lineTo(l+hl+slope_l*eye, eye)
        t.lineTo(l+hl, 0)
        t.close()
        p.add(t)
        p.serif(lx, 0, hl, slope_l)
        p.serif(rx, 0, hr, slope_r)
        y = 237
        p.stroke((lx+(peak-lx)*y/(h-cut), y), (rx+(peak-rx)*y/(h-cut), y), width=18, aspect=1)
    elif name in 'Xx':
        l, r, bl, br = (95, 523, 77, 507) if cap else (85, 423, 73, 411)
        p.ribbon((l, h), (br, 0), 24, head=True, foot=True)
        p.ribbon((r, h), (bl, 0), 18, head=True, foot=True)
    elif name in 'Kk':
        stem, arm, leg, join = (131, 514, 531, 334) if cap else (109 if italic else 120, 422, 445, 225)
        p.ribbon((stem, 0), (stem, 700 if cap else 720), 24, head=cap, foot=True)
        if not cap:
            p.entry(stem, 740)
        p.ribbon((stem, join), (arm, h), 18, head=True, start_cut=0)
        arm_slope = (arm-stem)*p.scale/(h-join)
        branch = .29
        x = stem+(arm-stem)*branch
        y = join+(h-join)*branch
        if italic and not cap:
            # Keep one tangent down the leg and ease into a shallow upturned exit.
            ankle = (351, 97)
            p.stroke((x, y), ankle,
                     (ankle[0]+(ankle[0]-x)*.27, ankle[1]+(ankle[1]-y)*.27, 403, 3, 429, 3),
                     (448, 3, 465, 20, 481, 45), width=24, aspect=1)
        else:
            p.ribbon((x, y), (leg, 0), 24, foot=True, start_cut=arm_slope)
    elif name == 'Y':
        x = 292*p.scale
        junction = 318
        left, right = (82*p.scale-x)/(h-junction), (522*p.scale-x)/(h-junction)
        l, r = 12*math.hypot(1, left), 9*math.hypot(1, right)
        inside = (l+r)/(right-left)
        yleft, yright = junction+(l-12)/left, junction+(12-r)/right
        fork = pathops.Path()
        fork.moveTo(x-12, 0)
        for xy in ((x-12, yleft), (82*p.scale-l, h), (82*p.scale+l, h),
                   (x+left*inside+l, junction+inside), (522*p.scale-r, h),
                   (522*p.scale+r, h), (x+12, yright), (x+12, 0)):
            fork.lineTo(*xy)
        fork.close()
        p.add(fork)
        p.serif(82, h, l, left, top=True)
        p.serif(522, h, r, right, top=True)
        p.serif(292, 0)
    else:
        # The right rail and descender are one curve with one normal width.
        slope = 208*p.scale/585
        p.stroke((427+8*208/585, 528), (219, -65), (187, -155, 149, -215, 99, -215),
                 (64, -215, 47, -193, 48, -167), width=18, aspect=1)
        crop = pathops.Path()
        crop.moveTo(-1500, -500)
        crop.lineTo(2000, -500)
        crop.lineTo(2000, 520)
        crop.lineTo(-1500, 520)
        crop.close()
        p.shape = pathops.op(p.shape, crop, pathops.PathOp.INTERSECTION)
        p.serif(427, 520, 9*math.hypot(1, slope), slope, top=True)
        meet = 4
        x = 219+(427-219)*(meet+65)/585
        p.ribbon((82, h), (x, meet), 24, head=True, end_cut=slope)
        p.drop(48, -167, 15, 17)


def open_bowls(p, name):
    if name == 'c':
        p.stroke((445, 420), (445, 476, 378, 521, 290, 521),
                 (155, 521, 63, 413, 63, 260), (63, 106, 152, -1, 286, -1),
                 (366, -1, 423, 37, 464, 102))
        p.drop(443, 416, 17, 20)
        return
    # The cap beak grows from the upper arc. Both C and G use the same
    # crown, high point and left wall, right through the lower turn.
    lower = [(455, -3, 531, 40, 579, 111)] if name == 'C' else [(434, -3, 507, 22, 556, 72), (556, 346)]
    p.stroke((359, 703), (184, 703, 66, 558, 66, 350), (66, 145, 176, -3, 360, -3), *lower)
    b = pathops.Path()
    x, crown = 563*p.scale, 359*p.scale
    b.moveTo(crown, 694)
    b.cubicTo(456*p.scale, 694, x-29*p.scale, 644, x-9, 592)
    b.lineTo(x+8, 592)
    b.lineTo(x+13, 689)
    b.lineTo(x+4, 689)
    b.cubicTo(x+2, 664, x-1, 651, x-12, 647)
    b.cubicTo(501*p.scale, 685, 430*p.scale, 712, crown, 712)
    b.close()
    p.add(b)
    if name == 'G':
        p.serif(556, 356, 12, top=True, left=3.25, right=1.0)


def caps(p, name):
    if name == 'J':
        p.stroke((371, 700), (371, 216), (371, 81, 310, -3, 211, -3),
                 (127, -3, 72, 35, 72, 91))
        p.serif(371, 700, top=True, left=1.15, right=1.15)
        p.drop(72, 92, 18, 20)
    elif name == 'Q':
        # Give the tail its own turn; it starts in the lower rim of the oval.
        s = p.scale
        l, r = 54+12/s, 630-12/s
        cx = 342
        kx = (cx-l)*.575
        ky = 353*.595
        p.stroke((cx, 703), (cx+kx, 703, r, 350+ky, r, 350), (r, 350-ky, cx+kx, -3, cx, -3),
                 (cx-kx, -3, l, 350-ky, l, 350), (l, 350+ky, cx-kx, 703, cx, 703), closed=True)
        p.stroke((402, 4), (453, -42, 515, -102, 594, -102), (614, -102, 632, -99, 646, -93),
                 width=21, aspect=.84)
    elif name == 'R':
        p.ribbon((133, 0), (133, 700), 24, foot=True)
        p.serif(133, 700, top=True, left=1.25, right=0)
        p.stroke((133, 691), (305, 691), (430, 691, 510, 630, 510, 518),
                 (510, 417, 429, 352, 308, 352), (133, 352))
        p.ribbon((305, 352), (517, 0), 24, foot=True)


def lowercase(p, name, it):
    if name == 'a' and not it:
        x = 433
        p.stroke((110, 419), (110, 479, 173, 521, 263, 521), (365, 521, x, 456, x, 352),
                 (x, 107), (x, 33, 452, 0, 483, 0), (500, 0, 516, 11, 527, 22))
        p.drop(110, 418, 17, 19)
        p.stroke((x, 286), (289, 282, 85, 236, 85, 126), (85, 50, 138, -1, 220, -1),
                 (315, -1, 397, 52, x, 137))
    elif name in 'ad':
        a = name == 'a'
        x = 410 if a else (440 if it else 458)
        c = 229 if a else 250
        l = 60
        p.stroke((x, 361), (x-21, 455, c+81, 521, c, 521), (c-100, 521, l, 412, l, 258),
                 (l, 104, c-100, -1, c, -1), (c+83, -1, x-24, 70, x, 166))
        p.ribbon((x, 90 if it else 0), (x, 500 if a else 720), 24)
        if a:
            p.entry(x, 520)
        else:
            p.entry(x, 740)
        if it:
            p.exit(x, 98 if a else 92)
        else:
            p.serif(x, 0, left=.18, right=1.25)
    elif name == 'f':
        x = 149
        p.stroke((x, -6 if it else 0), (x, 609), (x, 697, 198, 745, 260, 745),
                 (299, 745, 328, 722, 328, 686))
        p.drop(328, 685, 17, 19)
        p.stroke((35, 511), (311, 511), width=18, aspect=1)
        if it:
            p.stroke((x, 0), (x, -131, 111, -205, 48, -205), (16, -205, -2, -184, -1, -158))
            p.drop(-1, -158, 15, 17)
        else:
            p.serif(x, 0, left=1.15, right=1.35)
    elif name == 'm':
        a, b, c = (105, 420, 726) if it else (116, 440, 762)
        p.ribbon((a, 0), (a, 500), 24, foot=True)
        p.entry(a, 520)
        for i, (left, right) in enumerate(((a, b), (b, c))):
            peak = left+(right-left)*.54
            p.stroke((left, 344), (left+18, 441, peak-76, 521, peak, 521),
                     (right-54, 521, right, 455, right, 333), (right, 95 if i and it else 0))
            if i and it:
                p.exit(right, 110)
            else:
                p.serif(right, 0, left=.88, right=.92)
    else:
        a, b = (111, 428) if it else (118, 458)
        p.stroke((a, 500), (a, 192), (a, 72, a+50, -1, a+146, -1),
                 (b-76, -1, b-20, 79, b, 178))
        p.ribbon((b, 92 if it else 0), (b, 500), 24)
        p.entry(a, 520)
        p.entry(b, 520)
        if it:
            p.exit(b, 96)
        else:
            p.serif(b, 0, left=.18, right=1.25)


@lru_cache(maxsize=128)
def draw(name, scale, italic):
    p = ThinPen(scale)
    if name in 'AKXYkxy':
        diagonals(p, name, italic)
    elif name in 'CGc':
        open_bowls(p, name)
    elif name in 'JQR':
        caps(p, name)
    else:
        lowercase(p, name, italic)
    return p.rings()


def station_positions(name, italic, counter):
    key = name+'.italic' if italic and name+'.italic' in STATIONS else name
    coords = np.asarray(STATIONS[key+('.counter' if counter else '')])
    return coords[:, 0]+1j*coords[:, 1], coords[:, 2]+1j*coords[:, 3]


def orient(contour, reference):
    return Contour(contour.pieces[::-1, ::-1]) if contour.area*reference.area < 0 else contour


def closest(z, points):
    return abs(z[:, None]-points).argmin(axis=0)


def match_cycle(cost):
    """Assign each station a distinct vertex, preserving winding and traversal."""
    rows, cols = cost.shape
    best = float('inf')
    for first in np.argsort(cost[0])[:min(4, cols)]:
        perm = (np.arange(cols)+first) % cols
        c = cost[:, perm]
        previous = np.full(cols, np.inf)
        previous[0] = c[0, 0]
        back = np.zeros((rows, cols), dtype=int)
        for row in range(1, rows):
            prefix = np.minimum.accumulate(previous)
            indices = np.maximum.accumulate(np.where(previous == prefix, np.arange(cols), 0))
            back[row, 1:] = indices[:-1]
            previous = np.r_[np.inf, prefix[:-1]]+c[row]
        end = previous.argmin()
        if previous[end] < best:
            best = previous[end]
            idx = [end]
            for row in range(rows-1, 0, -1):
                idx.append(back[row, idx[-1]])
            result = perm[idx[::-1]]
    if not math.isfinite(best):
        raise ValueError('Insufficient vertices for Thin design stations')
    return result


def reference_stations(ring, native, nominal, name, italic, counter):
    source, target = station_positions(name, italic, counter)
    ix = closest(ring.pieces[:, 0], source)
    order = np.argsort((ix-ix[0]) % len(ring.pieces))
    ring = ring.roll(ix[0])
    native = native.roll(closest(native.pieces[:, 0], source[:1])[0])
    ix = (ix[order]-ix[0]) % len(ring.pieces)
    nominal = orient(nominal, ring)
    iy = match_cycle(abs(target[order, None]-nominal.pieces[None, :, 0])**2)
    return (ring, native), (ring.knots[ix], nominal, iy)


def moving_stations(ring, ids, scale):
    z = ring.pieces[ids, 0]
    # Use a short physical span to see the direction past incidental vertices
    # introduced where a serif or a terminal meets its stroke.
    at = ring.knots[ids]
    directions = []
    for offset in (-2., 2.):
        v = (ring.eval(at+offset/ring.length)-z)*np.sign(offset)
        v = v.real/scale+1j*v.imag
        directions.append(v/np.maximum(abs(v), 1e-9))
    return z.real/scale+1j*z.imag, directions


def register_width(reference, scale, name, italic, counter):
    u, ring, ids = reference
    old_scale = 1.
    for step in np.linspace(1., scale, 1+max(1, math.ceil(abs(scale-1)/.13)))[1:]:
        paths = sorted(draw(name, float(step), italic), key=lambda c: -abs(c.area))
        shape = orient(paths[int(counter)], ring)
        z, dirs = moving_stations(ring, ids, old_scale)
        pts, angles = moving_stations(shape, np.arange(len(shape.pieces)), step)
        cost = abs(z[:, None]-pts)**2
        for d, a in zip(dirs, angles):
            cost += 36*abs(d[:, None]-a)**2
        ids = match_cycle(cost)
        ring, old_scale = shape, step
    shape = ring.roll(ids[0])
    v = shape.knots[(ids-ids[0]) % len(shape.pieces)]
    return shape, np.r_[u, 1.], np.r_[v, 1.]
