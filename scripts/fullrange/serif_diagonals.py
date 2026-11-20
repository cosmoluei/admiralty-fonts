"""Measure the sloping strokes normal to their own axes; bracket their four cuts."""
import math

import numpy as np

from compatible import mapped_landmarks


def diagonal_landmarks(nodes, name, scale, weight):
    t = {100: 24, 400: 96, 900: 132}[weight]
    hair = {100: 18, 400: 55, 900: 78}[weight]
    serif = {100: 10, 400: 29, 900: 39}[weight]
    if name in ('z', 'Z'):
        cap = name == 'Z'
        h = 700 if cap else 520
        l, r = (40, 532) if cap else (38, 432)
        left, right = l*scale, r*scale
        bar = {100: 18, 400: 50 if cap else 48, 900: 68}[weight]
        cut = t*math.hypot(1, (right-left)/h)
        beak = {100: 11, 400: 35, 900: 44}[weight]
        reach = (164 if cap else 134)*{100: .66, 400: 1, 900: 1.0}[weight]
        # The four diagonal endpoints have the same horizontal offset from
        # their opposing edge, even when width grows faster than height.
        points = [(left, 0), (right+4*scale, 0), (right+14*scale, reach), (right+14*scale-beak, reach),
                (right-(116 if cap else 100)*scale, bar), (left+cut, bar), (right, h-bar), (right, h),
                (left+9*scale, h), (left-2*scale, h-reach), (left-2*scale+beak, h-reach),
                (left+(130 if cap else 112)*scale, h-bar), (right-cut, h-bar), (left, bar)]
        old = ([(40, 0), (536, 0), (546, 164), (510, 164), (416, 50), (156, 50), (532, 652), (532, 700),
                (50, 700), (40, 540), (76, 540), (170, 650), (420, 650), (40, 48)] if cap else
               [(38, 0), (436, 0), (446, 134), (412, 134), (332, 48), (144, 48), (432, 472), (432, 520),
                (46, 520), (36, 390), (70, 390), (150, 472), (326, 472), (38, 48)])
    elif name == 'N':
        left, right = 116*scale, 576*scale
        slope = (right-left)/700
        diag = t*math.hypot(1, slope)
        meet = (diag+hair)/(2*slope)
        ext = {100: 28, 400: 44, 900: 48}[weight]*scale**.45
        a, b = left-hair/2, left+hair/2
        c, d = right-hair/2, right+hair/2
        depth = serif+{100: 14, 400: 34, 900: 40}[weight]
        old = [(42, 0), (192, 0), (192, 30), (146, 64), (146, 620), (516, 0), (606, 0), (606, 636), (650, 670), (650, 700),
             (500, 700), (500, 670), (546, 636), (546, 188), (192, 700), (42, 700), (42, 670), (86, 636), (86, 64), (42, 30)]
        points = [(a-ext, 0), (b+ext, 0), (b+ext, serif), (b, depth), (b, 700-meet), (right-diag/2, 0),
                (d, 0), (d, 700-depth), (d+ext, 700-serif), (d+ext, 700), (c-ext, 700), (c-ext, 700-serif),
                (c, 700-depth), (c, meet), (left+diag/2, 700), (a-ext, 700), (a-ext, 700-serif),
                (a, 700-depth), (a, depth), (a-ext, serif)]
    elif name == 'M':
        left, mid, right = 112*scale, 400*scale, 687*scale
        heavy = t
        a, b = left-hair/2, left+hair/2
        c, d = right-heavy/2, right+heavy/2
        ext = {100: 23, 400: 43, 900: 47}[weight]*scale**.4
        down, up = (mid-left)/700, (right-mid)/700
        dl = t*math.hypot(1, down)/2
        dr = hair*math.hypot(1, up)/2
        tip = {100: 3, 400: 8, 900: 10}[weight]
        eye = (dl+dr+tip)/(down+up)
        depth = serif+{100: 14, 400: 34, 900: 40}[weight]
        old = [(594, 0), (780, 0), (780, 30), (738, 64), (738, 636), (780, 670), (780, 700), (608, 700),
             (422, 148), (414, 148), (202, 700), (38, 700), (38, 670), (82, 636), (82, 64), (38, 30),
             (38, 0), (186, 0), (186, 30), (142, 64), (142, 588), (372, 0), (428, 0), (636, 606), (636, 64), (594, 30)]
        points = [(c-ext, 0), (d+ext, 0), (d+ext, serif), (d, depth), (d, 700-depth), (d+ext, 700-serif),
                (d+ext, 700), (right-dr, 700), (mid+up*eye-dr, eye), (mid-down*eye+dl, eye),
                (left+dl, 700), (a-ext, 700), (a-ext, 700-serif), (a, 700-depth), (a, depth),
                (a-ext, serif), (a-ext, 0), (b+ext, 0), (b+ext, serif), (b, depth),
                (b, (mid-dl-b)/down), (mid-dl, 0), (mid+dr, 0), (c, (c-mid-dr)/up),
                (c, depth), (c-ext, serif)]
    else:
        raise ValueError(name)
    return mapped_landmarks(nodes, old, points)


def zigzag_landmarks(nodes, name, scale, weight):
    """Hold each V/W rail parallel to its mate through both internal turnarounds."""
    cap = name.isupper()
    double = name.lower() == 'w'
    h = 700 if cap else 520
    # Pairs of centerline junctions and original stations at either cap.
    if double:
        centers = ([86, 236, 446, 644, 810] if cap else [81, 204, 379, 550, 680])
        high = 686 if cap else 510
    else:
        centers = ([102, 306, 530] if cap else [85, 250, 434])
        high = h
    ys = np.array([h, 0, high, 0, h] if double else [h, 0, h], dtype=float)
    xs = np.array(centers)*scale
    thick = {100: 24, 400: 100 if cap else 89, 900: 132 if cap else 124}[weight]
    hair = {100: 18, 400: 62 if cap else 56, 900: 87 if cap else 80}[weight]
    widths = np.resize([thick, hair], len(xs)-1)
    slopes = np.diff(xs)/np.diff(ys)
    half = widths*np.hypot(1, slopes)/2
    intercept = xs[:-1]-slopes*ys[:-1]
    width_at_tip = {100: 9, 400: 62, 900: 83}[weight]
    if not double:
        width_at_tip = {100: 10, 400: 69, 900: 87}[weight]
    # Move the skeleton apex until the clipped outer rails leave the
    # intended flat on the baseline (or at the interior crown).
    for j in range(1, len(xs)-1):
        ys[j] += (half[j-1]+half[j]-width_at_tip)/abs(slopes[j]-slopes[j-1])*(1 if j % 2 else -1)
    slopes = np.diff(xs)/np.diff(ys)
    intercept = xs[:-1]-slopes*ys[:-1]
    half = widths*np.hypot(1, slopes)/2
    target = []
    source = []
    def add(old, x, y):
        source.append(complex(*old)); target.append(complex(x, y))
    for j in range(1, len(xs)-1):
        floor = j % 2 == 1
        cut = 0 if floor else high
        small = {100: 2, 400: 8, 900: 10}[weight]
        inner_y = (intercept[j]-intercept[j-1]+-(half[j]+half[j-1])-small)/(slopes[j-1]-slopes[j])
        left_out = intercept[j-1]+slopes[j-1]*cut-half[j-1]
        right_out = intercept[j]+slopes[j]*cut+half[j]
        left_in = intercept[j-1]+slopes[j-1]*inner_y+half[j-1]
        right_in = intercept[j]+slopes[j]*inner_y-half[j]
        if double:
            outer = ([(198, 0), (274, 0)], [(412, 686), (480, 686)], [(606, 0), (682, 0)]) if cap else ([(170, 0), (238, 0)], [(342, 510), (416, 510)], [(514, 0), (586, 0)])
            inner = ([(244, 138), (252, 138)], [(434, 540), (442, 540)], [(650, 138), (658, 138)]) if cap else ([(208, 100), (216, 100)], [(372, 408), (380, 408)], [(546, 100), (554, 100)])
        else:
            outer = ([(268, 0), (344, 0)] if cap else [(212, 0), (288, 0)],)
            inner = ([(318, 126), (326, 126)] if cap else [(260, 92), (268, 92)],)
        # At a central peak the outer edge still spreads to the left/right.
        for pt, x in zip(outer[j-1], [left_out, right_out]): add(pt, x, cut)
        for pt, x in zip(inner[j-1], [left_in, right_in]): add(pt, x, inner_y)
    # Map each bracket from its original two shoulders to the physical stem
    # edges. Preserve the bracket shape and its straight, horizontal serif.
    for z in nodes:
        if min(abs(z-u) for u in source) < 2: continue
        x, y = z.real, z.imag
        left = x < centers[1]
        j = 0 if left else len(slopes)-1
        if double:
            at, span = ((86, 96) if cap else (81, 89)) if left else ((810, 61) if cap else (680, 57))
        else:
            at, span = ((96, 103) if cap else (85, 96)) if left else ((530, 63) if cap else (431, 59))
        old_y = h-y
        y1 = h-old_y*({100: .43, 400: 1, 900: 1.16}[weight])
        native_slope = (centers[j+1]-centers[j])/([h, 0, high, 0, h][j+1]-[h, 0, high, 0, h][j])
        rel = x-at-native_slope*(y-h)
        factor = widths[j]/span
        # Serifs extend beyond both ends of the section even at Thin.
        excess = max(0, abs(rel)-span/2)
        offset = np.sign(rel)*(min(abs(rel), span/2)*factor+excess*(.62 if weight == 100 else 1)*scale**.4)
        add((x, y), intercept[j]+slopes[j]*y1+offset, y1)
    index = abs(nodes[:, None]-np.array(source)).argmin(axis=1)
    return np.array(target)[index]
