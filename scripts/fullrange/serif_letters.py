"""Draw the Serif alphabet from its original cubic landmarks and the approved t pen."""
from functools import lru_cache
from string import ascii_letters

import numpy as np
from fontTools.pens.transformPen import TransformPen
from scipy.spatial import cKDTree

from compatible import Contour, OutlinePen, Profile, compatible_points, mapped_landmarks, ordered_contours
from optical_master import OpticalMaster, direction
from serif_bowls import a_landmarks, binocular_tracks, joined_bowls, joint_curves, shoulder_curves, thin_arch, thin_bowl, thin_head, thin_italic_exit
import serif_thin
from serif_diagonals import diagonal_landmarks, zigzag_landmarks
from glyphs_italic import ITALIC_PIVOT_Y, _build_400_upright_serif_italic
from glyphs_serif_figs_ext import SERIF_REGULAR, build_all_serif_glyphs


LETTERS = (set(ascii_letters) - {'t'}) | {
    'dotlessi', 'dotlessj', 'AE', 'ae', 'OE', 'oe', 'Eth', 'eth', 'Thorn', 'thorn',
    'Oslash', 'oslash', 'Dcroat', 'dcroat', 'Hbar', 'hbar', 'IJ', 'ij', 'Ldot',
    'ldot', 'Lslash', 'lslash', 'Eng', 'eng', 'Tbar', 'longs', 'Germandbls',
    'germandbls', 'kgreenlandic', 'napostrophe',
}
RADII = {100: 4, 400: 12, 900: 18}


@lru_cache(maxsize=2)
def sources(italic):
    return _build_400_upright_serif_italic() if italic else build_all_serif_glyphs(SERIF_REGULAR)


def dot(xy, scale, w):
    center = (xy.real.min() + xy.real.max()) / 2 + 1j * (xy.imag.min() + xy.imag.max()) / 2
    diameter = {100: 41, 400: 104, 900: 143}[w]
    return center.real * scale + 1j * center.imag + (xy - center) * (diameter / np.ptp(xy.imag))


def s_landmarks(nodes, name, scale, w):
    # Pair the two sides of the spine at its inflection, the north/south
    # hairlines and the two bowls. The shoulder and its beak share a joint.
    upper = name == 'S'
    stem = {100: 24, 400: 94 if upper else 80, 900: 136 if upper else 120}[w]
    hair = {100: 18, 400: 50 if upper else 48, 900: 70 if upper else 64}[w]
    top, bottom = (712, -12) if upper else (530, -10)
    xleft, xright = (113, 472) if upper else (94, 384)
    yleft, yright = (532, 183) if upper else (396, 137)
    waist_x, waist_y = (294, 357) if upper else (242, 266)
    waist_v = stem * (1.06 if upper else 1.10)
    flat = {100: 12, 400: 36 if upper else 32, 900: 45}[w]
    # Heights of the diagonal end cuts belong to the beak, independently
    # of the width of its flat edge.
    xb, xt = (78, 488) if upper else (68, 400)
    yb, yt = (148, 562) if upper else (122, 402)
    original = [(282, -12), (522, 188), (294, 412), (160, 538), (296, 662), (466, 562), (502, 562),
                (510, 704), (474, 704), (464, 676), (296, 712), (66, 526), (294, 302), (422, 178),
                (282, 38), (98, 148), (62, 148), (54, -2), (90, -2), (100, 26)] if upper else [
                (228, -10), (424, 142), (242, 310), (134, 400), (244, 482), (380, 402), (412, 402),
                (420, 522), (388, 522), (380, 498), (242, 530), (54, 392), (242, 222), (344, 132),
                (228, 38), (84, 122), (52, 122), (44, -2), (76, -2), (84, 22)]
    crown, floor = original[10][0]*scale, original[0][0]*scale
    reach = {100: .70, 400: 1., 900: 1.06}[w]
    low_beak, high_beak = yb*reach, top-(top-yt)*reach
    notch = {100: 46 if upper else 18, 400: 33, 900: 46}[w]
    new = [(floor, bottom), (xright*scale+stem/2, yright), (waist_x*scale, waist_y+waist_v/2),
           (xleft*scale+stem/2, yleft), (crown, top-hair), (xt*scale-flat/2, high_beak),
           (xt*scale+flat/2, high_beak), (xt*scale+flat/2+7, top-8), (xt*scale-flat/2+7, top-8),
           (xt*scale-flat/2, top-notch), (crown, top), (xleft*scale-stem/2, yleft),
           (waist_x*scale, waist_y-waist_v/2), (xright*scale-stem/2, yright),
           (floor, bottom+hair), (xb*scale+flat/2, low_beak), (xb*scale-flat/2, low_beak),
           (xb*scale-flat/2-7, bottom+8), (xb*scale+flat/2-7, bottom+8), (xb*scale+flat/2, bottom+notch)]
    return mapped_landmarks(nodes, original, new)


def eszett_landmarks(nodes, name, scale, w, italic):
    """Size the arch, spine, baseline turn and cut independently of the width axis."""
    lower = name == 'germandbls'
    stem = {100: 24, 400: 86 if lower else 102, 900: 124 if lower else 142}[w]
    hair = {100: 18, 400: 69 if lower else 50, 900: 88 if lower else 68}[w]
    left = (119 if lower else 133)*scale-stem/2
    right = left+stem
    bracket = {100: 26, 400: 60, 900: 74}[w]
    foot = {100: 9, 400: 28, 900: 37}[w]
    extension = {100: 25, 400: 44, 900: 52}[w]*scale**.3
    crown = (298 if lower else 351)*scale
    upper = (463 if lower else 482)*scale
    outer = (510 if lower else 549)*scale
    waist = (302 if lower else 315)*scale
    tip = {100: 20, 400: 62, 900: 82}[w]
    base = (334 if lower else 384)*scale
    if lower:
        end = max(right+27,201*scale)
        dx,dy = .22*hair,.445*hair
        old = [(32,0),(162,0),(162,536),(298,678),(418,562),(274,412),(254,348),
               (464,174),(332,62),(212,102),(176,36),(338,-10),(556,176),(394,380),
               (508,566),(298,750),(76,536),(76,60),(32,28)]
        new = [(left-extension,0),(right,0),(right,536),(crown,750-hair),(upper-stem/2,564),
               (waist+tip*.14,380+tip/2),(waist-tip*.14,380-tip/2),
               (outer-stem/2,175),(base,-10+hair),(end+dx,55+dy),(end-dx,55-dy),
               (base,-10),(outer+stem/2,175),(waist+tip*1.95*scale,380),
               (upper+stem/2,564),(crown,750),(left,536),(left,bracket),(left-extension,foot)]
    else:
        # The native capital has one enclosed counter. Its return stroke
        # meets the foot in a narrow, cut-back notch before rising into it.
        toe = right+(extension*.24 if w==100 else extension*.9)
        # The cut-back at the foot remains visible as the lower bowl turns
        # up to meet the thin stem. At wide widths a shallow return looks
        # like a straight baseline closing a B.
        lift = 60 if w==100 else 0
        old = [(36,0),(222,0),(222,12.5),(390,-10),(602,178),(424,366),(528,538),
               (354,700),(36,700),(36,670),(82,636),(82,64),(36,30),
               (184,650),(344,650),(436,530),(282,378),(282,326),(496,174),
               (378,38),(222,68),(210,31),(184,64)]
        new = [(left-extension,0),(toe,0),(toe,foot*.72+(lift*.70 if w==100 else lift)),(base,-10),
               (outer+stem/2,177),(waist+tip*1.96*scale,362),(upper+stem/2,536),
               (crown,700),(left-extension,700),(left-extension,700-foot),
               (left,700-bracket),(left,bracket),(left-extension,foot),
               (right,700-hair),(crown,700-hair),(upper-stem/2,536),
               (waist,357+tip/2),(waist,357-tip/2),(outer-stem/2,177),
               (base,-10+hair),(toe+(18 if w==100 else 3),foot+hair*.92+lift),(toe+(8 if w==100 else -5),foot+hair*.32+lift),(right,bracket+lift)]
        if italic and w == 100:
            # Both rails rise together into the stem. Place the native notch
            # stations on the inside rail, avoiding an extra wedge of ink.
            new[1:3] = [(right, 0), (right, 45)]
            new[20:23] = [(right+20, 59), (right+8, 63), (right, 66)]
    return mapped_landmarks(nodes, old, new)


def thin_eszett_return(ring, curve):
    # The inner and outer rails approach their baseline extrema with level
    # tangents. The split near the stem belongs to the native counter.
    pieces = curve.pieces.copy()
    nodes = ring.pieces[:, 0]
    def reshape(p, q, first, last):
        for i, (a, b) in enumerate(zip(nodes, np.roll(nodes, -1))):
            reverse = abs(a-q) < 1 and abs(b-p) < 1
            if not reverse and not (abs(a-p) < 1 and abs(b-q) < 1):
                continue
            row = pieces[i, ::-1] if reverse else pieces[i]
            x, y = row[0], row[3]
            dx = y.real-x.real
            row[1] = x + dx * first
            row[2] = y - dx * last
    reshape(222+12.5j, 390-10j, .32-.12j, .32)
    reshape(222+68j, 378+38j, .32-.1067j, .32)
    reshape(184+64j, 210+31j, (1-.375j)/3, (1-.35j)/3)
    reshape(210+31j, 222+68j, (1-.35j)/3, (1-1j/3)/3)
    return Contour(pieces)


def e_landmarks(nodes, scale, w, italic):
    stem = {100: 24, 400: 98, 900: 136}[w]
    hair = {100: 18, 400: 48, 900: 66}[w]
    left = 49*scale
    right = 499*scale
    mid = 284*scale
    terminal = 477*scale
    toe = {100: 10, 400: 31, 900: 43}[w]
    if italic:
        old = [(286, -10), (488, 92), (456, 124), (294, 38), (146, 212), (498, 294), (498, 304),
             (284, 530), (50, 260), (152, 264), (288, 482), (408, 326)]
        new = [(286*scale, -10), (terminal+toe/2, 108-toe/2), (terminal-toe/2, 108+toe/2),
             (294*scale, -10+hair), (left+stem, 235-hair/2), (right, 312-hair/2),
             (right, 316), (mid, 530), (left, 260), (left+stem+3, 235+hair/2), (mid+3, 530-hair),
             (right-stem*.91, 312+hair/2-10)]
    else:
        bar = 264
        old = [(288, -10), (492, 94), (460, 124), (296, 38), (148, 240), (500, 240), (500, 276),
             (282, 530), (48, 260), (150, 288), (284, 482), (412, 288)]
        new = [(288*scale, -10), (terminal+toe/2, 109-toe/2), (terminal-toe/2, 109+toe/2),
             (296*scale, -10+hair), (left+stem, bar-hair/2), (right, bar-hair/2),
             (right, bar+hair*.25), (mid, 530), (left, 260), (left+stem+2, bar+hair/2),
             (mid+2, 530-hair), (right-.90*stem, bar+hair/2)]
    return mapped_landmarks(nodes, old, new)


def oval_landmarks(ring, outer, scale, weight, cap):
    nodes = ring.pieces[:, 0]
    z = outer.pieces[:, 0]
    x = (z.real.max()+z.real.min())/2
    y = (z.imag.max()+z.imag.min())/2
    rx = np.ptp(z.real)*scale/2
    ry = np.ptp(z.imag)/2
    if ring is not outer:
        rx -= {100: 24, 400: 106 if cap else 98, 900: 143 if cap else 138}[weight]
        ry -= {100: 18, 400: 50 if cap else 48, 900: 70 if cap else 66}[weight]
    return x*scale+(nodes.real-x)*rx/(np.ptp(nodes.real)/2)+1j*(y+(nodes.imag-y)*ry/(np.ptp(nodes.imag)/2))


def shoulders(nodes, targets, name, weight, width, scale, italic):
    # Each arch has an independent high point and returns to its own shaft.
    # The white nick between the two shoulders of m deepens in narrow Black.
    hair = {100: 18, 400: 48, 900: 66}[weight]
    for y, new_y in ((530, 530), (482, 530-hair)):
        at = abs(nodes.imag-y) < 1
        targets.imag[at] = new_y
        targets.real[at] = nodes.real[at]*scale
    if name == 'm':
        valley = (abs(nodes.imag-434) < 1) & (nodes.real > 350)
        targets.imag[valley] = {100: 399, 400: 429, 900: 375 if width == 65 else 400}[weight]
        # Keep the valley on the middle shaft as the inner right wall moves.
        stem = 462 if italic else 484
        shaft = (abs(nodes.real-stem) < 1) & (abs(nodes.imag-344) < 1)
        if np.any(shaft):
            targets.real[valley] = targets.real[shaft][0]-.11*{100: 24, 400: 88, 900: 124}[weight]
    return targets


def retension(pieces, targets, scale):
    """Carry the tangents of the ink drawing to its new physical extrema."""
    a, b, c, d = pieces.T
    chord = d-a
    new_chord = np.roll(targets, -1)-targets
    u, v = b-a, d-c
    scale_x = lambda z: z.real*scale + 1j*z.imag
    k, l = direction(scale_x(u)), direction(scale_x(v))
    cross = lambda x, y: (x.conjugate()*y).imag
    determinant = cross(k, l)
    # Where two handles intersect, preserve their fraction of that tangent
    # triangle. For parallel tangents, use the change in projected chord.
    def arm(tangent, opposite, arm):
        old = scale_x(chord)
        den = cross(old, opposite)
        factor = np.divide(cross(new_chord, opposite), den, out=np.ones(len(den)), where=abs(den) > .0001)
        along = abs((new_chord*tangent.conj()).real)/np.maximum(abs((old*tangent.conj()).real), .001)
        fallback = np.where(abs((old*tangent.conj()).real) > .12*abs(old), along, abs(new_chord)/np.maximum(abs(old), .001))
        factor = np.where((abs(determinant) > .18) & (factor > .05), factor, fallback)
        return np.minimum(np.maximum(.03, factor)*abs(scale_x(arm)), 1.25*abs(new_chord))
    b1 = targets+k*arm(k, l, u)
    c1 = targets+new_chord-l*arm(l, k, v)
    linear = (abs(cross(u, chord))+abs(cross(v, chord))) < .0001
    b1[linear] = (targets+new_chord/3)[linear]
    c1[linear] = (targets+2*new_chord/3)[linear]
    return Contour(np.column_stack((targets, b1, c1, targets+new_chord)))


def letter_tracks(design, name, cells):
    italic = bool(design.slant)
    if name == "g" and not italic:
        return binocular_tracks(design, name, cells)
    base = {'dotlessi': 'i', 'dotlessj': 'j'}.get(name, name)
    original = OutlinePen(None)
    for cb in sources(italic)[base][2]:
        cb.draw_to_pen(original)
    source = original.contours
    if name.startswith('dotless'):
        source = [min(source, key=lambda c: c.center.imag)]
    release = OutlinePen(None)
    pivot = design.slant*ITALIC_PIVOT_Y
    design.regular.getGlyphSet()[name].draw(TransformPen(release, (1, 0, -design.slant, 1, pivot, 0)))
    source = ordered_contours(release.contours, source)
    # Use the same direction and starting landmark in all constructed masters.
    # The release has additional quadratic extrema; its default stays native.
    rings = []
    for native, ring in zip(release.contours, source):
        if ring.area*native.area < 0:
            ring = Contour(ring.pieces[::-1, ::-1])
        distances = abs(ring.pieces[:, 0, None]-native.pieces[:, 0])
        j, k = np.unravel_index(distances.argmin(), distances.shape)
        rings.append((ring.roll(j), native.roll(k)))
    if base in serif_thin.LETTERS:
        nominal = sorted(serif_thin.draw(base, 1., italic), key=lambda c: -abs(c.area))
        outer = max(range(len(rings)), key=lambda i: abs(rings[i][0].area))
        thin_refs = []
        for i, (ring, native) in enumerate(rings):
            rings[i], ref = serif_thin.reference_stations(
                ring, native, nominal[int(i != outer)], base, italic, i != outer)
            thin_refs.append(ref)
    needs_fit = base not in ('a', 'e', 'g', 'o', 's', 'v', 'w', 'z', 'M', 'N',
                             'O', 'S', 'V', 'W', 'Z', 'ae', 'oe', 'germandbls', 'Germandbls')
    if needs_fit:
        model = OpticalMaster(design.regular['glyf'][name], design.slant)
        samples = np.vstack([r.sampling(model.base, 2.5)[0] for r in model.rings])
        ref = samples@model.base+pivot
        lookup = cKDTree(np.column_stack((ref.real, ref.imag)))
        projections = []
        for ring, _ in rings:
            z = ring.pieces[:, 0]
            ix = lookup.query(np.column_stack((z.real, z.imag)))[1]
            projections.append(samples[ix])
    profiles = [[] for _ in rings]
    for w, d in cells:
        sx, dx = design.transform(name, w, d)
        native_cell = (w, d) == (400, 100)
        thin = w == 100 and base in serif_thin.LETTERS
        if not native_cell and needs_fit and not thin:
            fitted = model.fit(w, d, sx, dx, True)
            fitted = fitted.real-design.slant*fitted.imag+pivot+1j*fitted.imag
        for i, (ring, native) in enumerate(rings):
            if native_cell:
                curve = native
                u = v = np.array([0., 1.])
            elif thin:
                curve, u, v = serif_thin.register_width(thin_refs[i], sx, base, italic, i != outer)
            else:
                nodes = ring.pieces[:, 0]
                if base in ('s', 'S'):
                    targets = s_landmarks(nodes, base, sx, w)
                elif base in ('germandbls', 'Germandbls'):
                    targets = eszett_landmarks(nodes, base, sx, w, italic)
                elif base in ('ae', 'oe'):
                    targets = joined_bowls(nodes, base, sx, w, italic)
                elif base in ('a', 'g'):
                    targets = a_landmarks(nodes, sx, w, italic, descender=base == 'g')
                elif base in ('z', 'Z', 'N', 'M'):
                    targets = diagonal_landmarks(nodes, base, sx, w)
                elif base in ('v', 'V', 'w', 'W'):
                    targets = zigzag_landmarks(nodes, base, sx, w)
                elif base == 'e':
                    targets = e_landmarks(nodes, sx, w, italic)
                elif base in ('o', 'O'):
                    outer = max((r for r, _ in rings), key=lambda c: abs(c.area))
                    targets = oval_landmarks(ring, outer, sx, w, base == 'O')
                elif base in ('i', 'j', 'ij') and ring.center.imag > 590:
                    targets = dot(nodes, sx, w)
                else:
                    targets = projections[i]@fitted
                    targets += nodes-(projections[i]@model.base+pivot)
                    # Preserve the designed vertical alignment of flat cuts
                    # and overshoots; a curved cap keeps its original high point.
                    for y in (-226, -224, -222, -220, -12, -10, 0, 520, 530, 700, 712, 740, 752, 754):
                        at = abs(nodes.imag-y) < .3
                        targets.imag[at] = y
                    if base in ('b', 'd', 'p', 'q') and w == 100:
                        targets = thin_bowl(nodes, targets, base, sx, italic)
                        if base in ('b', 'p'):
                            targets = thin_head(nodes, targets, 72, 164, 740 if base == 'b' else 520, sx)
                    if base in ('n', 'h', 'm'):
                        targets = shoulders(nodes, targets, base, w, d, sx, italic)
                        if w == 100:
                            targets = thin_arch(nodes, targets, base, sx, italic)
                    if italic and w == 100 and base in ('h', 'n', 'm', 'u', 'd', 'r', 'i', 'l'):
                        targets = thin_italic_exit(nodes, targets, base, sx)
                curve = retension(ring.pieces, targets, sx)
                if italic and base == "Germandbls" and w == 100:
                    curve = thin_eszett_return(ring, curve)
                if w == 100 and base in ('b', 'd', 'p', 'q', 'h', 'm', 'n'):
                    curve = shoulder_curves(ring, curve)
                if base in ('ae', 'oe'):
                    curve = joint_curves(ring, curve, base)
                u, v = ring.knots, curve.knots
            for radius in (0, RADII[w]):
                profiles[i].append(Profile(curve, u, v, radius))
    tracks = [[] for _ in range(2*len(cells))]
    ends = []
    for group in profiles:
        for out, z in zip(tracks, compatible_points(group, .22, compact=.28)):
            out.extend(z+design.slant*(z.imag-ITALIC_PIVOT_Y))
        ends.append(len(tracks[0])-1)
    return list(map(np.asarray, tracks)), ends
