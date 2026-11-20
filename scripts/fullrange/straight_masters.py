"""Stem and bar stations for rectilinear capitals and sloping figures."""
import math

import numpy as np

from compatible import Contour


RECTILINEAR = {'E', 'F', 'H', 'I', 'L', 'T'}
DIAGONAL = {'Z', 'z', 'seven', 'one'}


def physical(native, thin, weight, width):
    if weight == 100:
        return thin
    if weight == 900:
        return native + min(46, .48 * native)
    return native * (1 + .09 * (width / 100 - 1))


def rectilinear(z, scale, shift, weight, width):
    nxt = np.roll(z, -1)
    vertical = (abs(nxt.imag - z.imag) > 110) & (abs(nxt.real - z.real) < 2)
    sides = sorted((z.real[vertical] + nxt.real[vertical]) / 2)
    rails = []
    for x in sides:
        if not rails or x - rails[-1] > 2:
            rails.append(x)
    if len(rails) not in (2, 4):
        raise ValueError(f'Unpaired stem rails {rails}')
    point = z.real * scale + shift + 1j * z.imag
    for left, right in zip(rails[::2], rails[1::2]):
        center = (left + right) * scale / 2 + shift
        thickness = physical(right - left, 24, weight, width)
        for rail, sign in ((left, -1), (right, 1)):
            point.real[abs(z.real - rail) < 2] = center + sign * thickness / 2
    levels = np.unique(z.imag)
    for low, high in zip(levels[:-1], levels[1:]):
        if high - low > 110:
            continue
        bar = physical(high - low, 22, weight, width)
        bottom = low if low == levels[0] else high - bar if high == levels[-1] else (low + high - bar) / 2
        point.imag[z.imag == low] = bottom
        point.imag[z.imag == high] = bottom + bar
    return point


def sloping(z, name, scale, shift, weight, width):
    x = z.real * scale + shift
    height = z.imag.max()
    if name == 'one':
        stem = physical(z[7].real-z[2].real, 24, weight, width)
        mid = (x[2]+x[7])/2
        left, right = mid-stem/2, mid+stem/2
        bar = physical(z[1].imag, 22, weight, width)
        tip = (x[4]+x[5])/2 + 1j * (z[4].imag+z[5].imag)/2
        axis = left + 1j*height - tip
        normal = 1j*axis/abs(axis)
        flag = physical(abs(z[5]-z[4]), 22, weight, width)
        inner = height - flag*abs(axis)/axis.real
        return np.array([complex(x[0], 0), complex(x[1], bar), complex(left, bar), complex(left, inner),
                         tip-normal*flag/2, tip+normal*flag/2, complex(left, height), complex(right, height),
                         complex(right, bar), complex(x[9], bar), complex(x[10], 0)])
    seven = name == 'seven'
    bar = physical(height-z[1 if seven else 2].imag, 22, weight, width)
    top = x[4 if seven else 5]
    bottom = (x[0]+x[6])/2 if seven else x[0]
    # Project the pen measured normal to the diagonal onto a horizontal
    # slice. The end of each diagonal meets the underside of its own bar.
    original_run = ((z[1]-z[0]) if seven else (z[2]-z[1]))
    original_dx = original_run.real/original_run.imag
    normal = ((z[6].real-z[0].real) if seven else
              (z[7].real-z[1].real-original_dx*(z[7].imag-z[1].imag))) / math.hypot(1, original_dx)
    pen = physical(normal, 24, weight, width)
    span = height-bar if seven else height-2*bar
    projected = pen
    for _ in range(8):
        run = top-bottom-projected*(.5 if seven else 1.)
        projected = pen*math.hypot(1, run/span)
    if seven:
        vertices = [(bottom-projected/2, 0), (top-projected, height-bar), (x[2], height-bar),
                    (x[3], height), (top, height), (top, height-bar), (bottom+projected/2, 0)]
    else:
        vertices = [(bottom, 0), (bottom, bar), (top-projected, height-bar), (x[3], height-bar),
                    (x[4], height), (top, height), (top, height-bar), (bottom+projected, bar), (x[8], bar), (x[9], 0)]
    return np.array([complex(a, b) for a, b in vertices])


def straight_ring(ring, name, scale, shift, weight, width):
    z = ring.pieces[:, 0]
    base = name.split('.')[0]
    # The original vertices have the same contour start and order in upright,
    # sheared and tabular drawings. All reconstructed cuts stay exactly flat.
    pts = (rectilinear(z, scale, shift, weight, width) if base in RECTILINEAR
           else sloping(z, base, scale, shift, weight, width))
    ends = np.roll(pts, -1)
    return Contour(np.column_stack([pts, (2*pts+ends)/3, (pts+2*ends)/3, ends]))


def pi_stations(ring):
    # The six faces use the same construction, translated within the cell
    # and with distinct intermediates on the native italic quadratics.
    points = ring.pieces[:, 0]
    offset = points.real.min()-44
    template = [(44, 444), (44, 520), (540, 520), (540, 444), (436, 444), (436, 128),
                (472, 64), (520, 76), (532, 10), (458, -8), (356, 122), (356, 444),
                (226, 444), (226, 0), (146, 0), (146, 444)]
    landmarks = np.array([complex(x+offset, y) for x, y in template])
    ids = abs(points[:, None]-landmarks).argmin(axis=0)
    ring = ring.roll(ids[0])
    ids = (ids-ids[0]) % len(points)
    if not np.all(np.diff(ids) > 0):
        raise ValueError('Unregistered pi stations')
    return ring, np.r_[ring.knots[ids], 1.], offset


def pi_curve(offset, scale, shift, weight, width):
    stem = physical(80, 24, weight, width)
    hair = physical(72, 22, weight, width)
    top = 520
    bar = top-physical(76, 22, weight, width)
    left = (186+offset)*scale+shift
    right = (396+offset)*scale+shift
    end = right+max(94,140*scale)
    bend = right+.54*(end-right)
    turn = 125
    bottom = -8
    rise = 33 if weight==100 else 29
    slope = 1.55*rise/(end-bend)
    h = hair/(2*math.hypot(1, slope))
    t = bottom+hair/2+rise
    vertices = [((44+offset)*scale+shift, bar), ((44+offset)*scale+shift, top),
                ((540+offset)*scale+shift, top), ((540+offset)*scale+shift, bar),
                (right+stem/2, bar), (right+stem/2, turn), (bend, bottom+hair),
                (end-h*slope, t+h), (end+h*slope, t-h), (bend, bottom),
                (right-stem/2, turn), (right-stem/2, bar), (left+stem/2, bar),
                (left+stem/2, 0), (left-stem/2, 0), (left-stem/2, bar)]
    z = np.array([complex(x, y) for x, y in vertices])
    ends = np.roll(z, -1)
    pieces = np.column_stack([z, (2*z+ends)/3, (z+2*ends)/3, ends])
    # Both sides enter the turn vertically and leave it horizontally. The
    # short exit curves share their cut angle and retain a visible end.
    for i in (5, 9):
        a, b = z[i], ends[i]
        dx, dy = (b-a).real, (b-a).imag
        if i == 5:
            pieces[i, 1:3] = [a+.57j*dy, b-.56*dx]
        else:
            pieces[i, 1:3] = [a+.56*dx, b-.57j*dy]
    for i in (6, 8):
        a, b = z[i], ends[i]
        run = (b-a).real
        pieces[i, 1:3] = ([a+.40*run, b-.32*run*(1+1j*slope)] if i == 6 else
                       [a+.32*run*(1+1j*slope), b-.40*run])
    return Contour(pieces)


COMPARISONS = {'equal', 'less', 'greater', 'lessequal', 'greaterequal'}


def comparison_ring(ring, name, scale, shift, weight, width):
    z = ring.pieces[:, 0]
    if len(z) == 4:
        # An equals bar has two flat cuts and sits on its own centreline.
        y = (z.imag.max()+z.imag.min())/2
        pen = physical(np.ptp(z.imag), 22, weight, width)
        points = z.real*scale+shift+1j*(y+np.sign(z.imag-y)*pen/2)
    else:
        # Match the three material stations of each chevron by height,
        # independent of the contour start chosen by the boolean union.
        tip_left = name.startswith('less')
        sign = 1 if tip_left else -1
        x = z.real*sign
        tip = x.min()
        end = x.max()
        nose = abs(x-tip) < 2
        outer = abs(x-end) < 2
        ys = sorted(z.imag[outer])
        if len(ys) != 4 or nose.sum() != 2:
            raise ValueError(f'Unregistered {name} comparison sign')
        center = z.imag[nose].mean()
        top = (ys[2]+ys[3])/2
        bottom = (ys[0]+ys[1])/2
        span = (end-tip)*scale
        slope = (top-center)/(end-tip)
        native = (ys[3]-ys[2])/math.hypot(1, slope)
        pen = physical(native, 24, weight, width)
        bevel = pen*.80
        normal = pen
        for _ in range(6):
            slope = (top-center+(normal-bevel)/2)/span
            normal = pen*math.hypot(1, slope)
        tip = sign*shift+tip*scale
        end = tip+span
        notch = tip+(normal-bevel/2)/slope
        original = [(x[nose].mean(), v) for v in sorted(z.imag[nose])]
        original.extend((x[outer].mean(), v) for v in ys)
        original.append((x[~(nose | outer)].item(), center))
        ref = np.array([complex(a, b) for a, b in original])
        positions = [(tip, center-bevel/2), (tip, center+bevel/2), (end, bottom-normal/2),
                   (end, bottom+normal/2), (end, top-normal/2), (end, top+normal/2), (notch, center)]
        indices = abs((x+1j*z.imag)[:, None]-ref).argmin(axis=1)
        points = np.array([complex(sign*a, b) for a, b in positions])[indices]
    ends = np.roll(points, -1)
    return Contour(np.column_stack([points, (2*points+ends)/3, (points+2*ends)/3, ends]))
