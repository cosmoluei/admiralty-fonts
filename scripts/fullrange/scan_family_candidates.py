"""Look for optical defects in the shipped text fonts, retaining exact review coordinates."""
import argparse
import ctypes
import hashlib
import json
from concurrent.futures import ProcessPoolExecutor
from itertools import product
from pathlib import Path
import unicodedata

import freetype as ft
import numpy as np
from fontTools.ttLib import TTFont

from build_text_family import OUTPUT, TEXT
from scan_review_geometry import scan as scan_known
from check_optical_inventory import unsheared
import uharfbuzz as hb
import review_strokes

WEIGHTS = tuple(range(100, 901, 100))
WIDTHS = (65, 82.5, 100, 125, 150)
RADII = (0, 50, 100)
DOTS = {'i','j','ij','ldot','period','periodcentered','colon','ellipsis','exclam','exclamdown',
        'question','questiondown','divide','uni0307','dotaccent','dotaccentcomb'}
FRAME = dict(units="normalized", origin="top left", viewBox=[0,0,1440,1440],
             fontSize=1000, baseline=1030, textAnchor="middle", textX=720)


def read_outline(face, gid):
    face.load_glyph(gid, ft.FT_LOAD_NO_SCALE | ft.FT_LOAD_NO_HINTING | ft.FT_LOAD_NO_BITMAP)
    slot = face.glyph
    outline = slot._FT_GlyphSlot.contents.outline
    if not outline.n_points:
        return [], slot.metrics.horiAdvance
    coords = np.ctypeslib.as_array(ctypes.cast(outline.points, ctypes.POINTER(ctypes.c_long)),
                                   shape=(2*outline.n_points,)).reshape(-1, 2)
    pts = coords[:, 0] + 1j*coords[:, 1]
    flags = np.frombuffer(ctypes.string_at(outline.tags, outline.n_points), np.uint8) & 1
    rings = []
    start = 0
    for end in outline.contours[:outline.n_contours]:
        z = pts[start:end+1]
        on = flags[start:end+1].astype(bool)
        # Sample the actual quadratic at its midpoint. Adjacent off-curve
        # controls have an implicit on-curve midpoint in TrueType.
        prev, nxt = np.roll(z, 1), np.roll(z, -1)
        a = np.where(np.roll(on, 1), prev, (prev+z)/2)
        b = np.where(np.roll(on, -1), nxt, (nxt+z)/2)
        mid = np.where(on, z, (a+2*z+b)/4)
        rings.append(mid)
        start = end+1
    return rings, slot.metrics.horiAdvance


def shape_frame(z):
    nxt = np.roll(z, -1)
    distances = np.r_[0., np.cumsum(abs(nxt-z))]
    area = np.sum(z.real*nxt.imag - z.imag*nxt.real)/2
    return distances, area


def turn_profile(z, arc):
    # Suppress single-unit quantization: compare chords on both sides of each
    # material station over two physical distances. Keep the smaller turn.
    knots = arc[:-1]
    closed = np.r_[z, z[:1]]
    def turn(reach):
        before = np.interp((knots-reach) % arc[-1], arc, closed)
        after = np.interp((knots+reach) % arc[-1], arc, closed)
        return np.degrees(abs(np.angle((after-z)*np.conj(z-before))))
    return np.minimum(turn(9), turn(17))


def neighborhood(turns, arc):
    # A moving corner is legitimate. Compare the local neighborhood of the
    # corresponding Regular station, including a bracket or a nearby end cut.
    knots = arc[:-1]
    closed = np.r_[turns, turns[:1]]
    return np.maximum.reduce([np.interp((knots+delta) % arc[-1], arc, closed)
                              for delta in (-22,-15,-8,0,8,15,22)])


def mark(point, advance, rule, score, **metrics):
    return dict(rule=rule, x=round(.5+(point.real-advance/2)/1440, 6),
                y=round((1030-point.imag)/1440, 6), score=round(float(score), 3),
                metrics={k:round(float(v), 2) for k,v in metrics.items()})


def ring_components(glyf, name):
    glyph = glyf[name]
    if glyph.isComposite():
        return [n for c in glyph.components for n in ring_components(glyf,c.glyphName)]
    return [name]*max(0,glyph.numberOfContours)


def compare_glyph(samples, advances, components, slant):
    findings = [[] for _ in samples]
    if not samples[3]:
        return findings
    for component, rings in zip(components, zip(*samples, strict=True), strict=True):
        regular = rings[3]
        ref_arc, ref_area = shape_frame(regular)
        if ref_arc[-1] < 1:
            continue
        # The shipped TrueType text outlines have clockwise outer contours.
        counter = ref_area > 1300
        dot = (component in DOTS and ref_area < -180 and np.ptp(regular.imag) < 160
               and max(np.ptp(regular.real), np.ptp(regular.imag)) < 240)
        smooth = ref_arc[-1] > 160 and len(regular) >= 10
        if smooth:
            native_turn = turn_profile(regular, ref_arc)
            ref_turn = neighborhood(native_turn, ref_arc)
            span = complex(max(1,np.ptp(regular.real)), max(1,np.ptp(regular.imag)))
            native_sharp = regular[native_turn > 34]
            round_body = component in {"O","o","zero","zero.tnum","eight","eight.tnum","six","nine",
                                       "C","c","G","S","s","Omega","ohm","at","ae","oe"}
        for i, z in enumerate(rings):
            if i == 3:
                continue
            arc, area = shape_frame(z)
            if arc[-1] < 1:
                continue
            if counter and i > 3 and area > 0:
                size = 4*area/arc[-1]
                ratio = area/ref_area
                if size < 21 and ratio < .14 and 4*ref_area/ref_arc[-1] > 45:
                    center = (z.real.max()+z.real.min())/2 + 1j*(z.imag.max()+z.imag.min())/2
                    findings[i].append(mark(center, advances[i], "counter", 1-ratio,
                                            effectiveWidth=size, areaRatio=ratio))
            if dot:
                def aspect(p):
                    x = np.ptp(p.real-slant*p.imag)
                    return x/max(1., np.ptp(p.imag))
                r, new = aspect(regular), aspect(z)
                deform = max(new/r, r/max(new, .01)) if r else 0
                if .67 < r < 1.55 and deform > 1.65 and (new > 1.55 or new < .65):
                    center = (z.real.max()+z.real.min())/2 + 1j*(z.imag.max()+z.imag.min())/2
                    findings[i].append(mark(center, advances[i], "dot", deform,
                                            aspect=new, regularAspect=r))
            if smooth and arc[-1] > 160 and len(z) == len(ref_turn):
                turn = turn_profile(z, arc)
                gain = turn-ref_turn
                # Design corners move when the counters and serifs change size.
                # Check their spatial positions as well as their material indices.
                eligible = ((gain > (27 if round_body else 56)) &
                            (turn > (39 if round_body else 73)) & (ref_turn < (16 if round_body else 27)))
                candidates = np.flatnonzero(eligible)
                if len(candidates) and len(native_sharp):
                    bounds = np.maximum((np.ptp(z.real),np.ptp(z.imag)),1)
                    rel_x = (z[candidates].real-z.real.min())/bounds[0]
                    rel_y = (z[candidates].imag-z.imag.min())/bounds[1]
                    dx = (regular.real.min()+rel_x[:,None]*span.real - native_sharp.real) / max(32,.14*span.real)
                    dy = (regular.imag.min()+rel_y[:,None]*span.imag - native_sharp.imag) / max(32,.14*span.imag)
                    candidates = candidates[(dx*dx+dy*dy).min(axis=1)>1.]
                if len(candidates):
                    index = candidates[np.argmax(gain[candidates])]
                    findings[i].append(mark(z[index], advances[i], "corner", gain[index],
                                            turn=turn[index], regularTurn=ref_turn[index]))
            for finding in findings[i]:
                finding.setdefault("component", component)
    return findings


def scan_face(args):
    directory, family = args
    path = directory/(family+'[wght,wdth,RADI].ttf')
    face = ft.Face(str(path))
    with TTFont(path) as tt:
        if tt['head'].unitsPerEm != 1000:
            raise ValueError(f"{family}: expected units in 1000/em")
        names = tt.getGlyphOrder()
        cmap = tt.getBestCmap()
        base = {}
        for cp, name in cmap.items():
            decomposition = unicodedata.normalize('NFD', chr(cp))
            if len(decomposition)>1 and all(unicodedata.combining(c) for c in decomposition[1:]):
                base[name] = cmap.get(ord(decomposition[0]), name)
        components = [ring_components(tt['glyf'],n) for n in names]
        slant = np.tan(np.deg2rad(-tt['post'].italicAngle))
    hbfont = hb.Font(hb.Face(path.read_bytes()))
    rows = []
    for d, r in product(WIDTHS, RADII):
        grids = []
        for w in WEIGHTS:
            face.set_var_design_coords((w,d,r))
            grids.append([read_outline(face, gid) for gid in range(len(names))])
        for gid, name in enumerate(names):
            samples, advances = zip(*(grid[gid] for grid in grids))
            results = compare_glyph(samples, advances, components[gid], slant)
            cuts = name in review_strokes.FLAT and name != 'k' and r == 0
            bars = review_strokes.BARS.get(name)
            if cuts or bars:
                hbfont.set_variations(dict(wght=400,wdth=d,RADI=r))
                regular = unsheared(hbfont,gid,slant)
                for index,w in enumerate(WEIGHTS):
                    if w == 400:
                        continue
                    hbfont.set_variations(dict(wght=w,wdth=d,RADI=r))
                    edges = unsheared(hbfont,gid,slant)
                    tests = []
                    if cuts:
                        tests.extend(review_strokes.straight_cuts(edges,regular,0,0,1,'flat-foot'))
                        tests.extend(review_strokes.straight_cuts(edges,regular,edges.imag.max(),
                                                                  regular.imag.max(),-1,'flat-head'))
                    if bars:
                        tests.extend(review_strokes.through_bars(edges,regular,bars))
                    for rule,z,score,metrics in tests:
                        finding = mark(z+slant*z.imag, hbfont.get_glyph_h_advance(gid),rule,score,**metrics)
                        results[index].append(dict(finding,component=name))
            for w, points in zip(WEIGHTS, results):
                if points:
                    rows.append(dict(glyph=name, glyphID=gid, base=base.get(name,name), family=family,
                                     wght=w, wdth=d, RADI=r, findings=points))
    print(f"{family}: {len(names)} glyphs, {len(rows)} candidate cells", flush=True)
    info = dict(file=path.name, sha256=hashlib.sha256(path.read_bytes()).hexdigest(), glyphs=len(names))
    return family, info, rows


def include_composites(directory, rows):
    """Follow measured pen landmarks into unscaled components at the exact instance."""
    targeted = {'flat-head','flat-foot','stem-head','stem-foot','leg-foot','arm-end','arm-junction','rail','bowl-waist'}
    by_family = {}
    for row in list(rows.values()):
        points = [p for p in row['findings'] if p['rule'] in targeted]
        if points:
            by_family.setdefault(row['family'], []).append((row,points))
    for family, seeds in by_family.items():
        path = directory/(family+'[wght,wdth,RADI].ttf')
        face = ft.Face(str(path))
        with TTFont(path) as tt:
            glyf = tt['glyf']
            order = tt.getGlyphOrder()
            children = {}
            for index,name in enumerate(order):
                if not glyf[name].isComposite():
                    continue
                rings = ring_components(glyf,name)
                for child in set(rings):
                    indexes = [i for i,n in enumerate(rings) if n==child]
                    children.setdefault(child,[]).append((index,name,indexes))
        for row,points in seeds:
            name = row['glyph']
            if name not in children:
                continue
            w,d,r = row['wght'],row['wdth'],row['RADI']
            face.set_var_design_coords((w,d,r))
            base, advance = read_outline(face,row['glyphID'])
            for gid,parent,indices in children[name]:
                rings, parent_advance = read_outline(face,gid)
                if len(indices)!=len(base) or any(len(rings[j])!=len(z) for j,z in zip(indices,base)):
                    continue
                deltas = np.concatenate([rings[j]-z for j,z in zip(indices,base)])
                translation = np.median(deltas.real)+1j*np.median(deltas.imag)
                if abs(deltas-translation).max()>1.6:
                    continue
                key=(family,parent,w,d,r)
                target=rows.setdefault(key,dict(family=family,glyph=parent,glyphID=gid,
                        base=name,wght=w,wdth=d,RADI=r,findings=[]))
                for point in points:
                    target['findings'].append(dict(point, component=name, inheritedFrom=name,
                        x=round(point['x']+(translation.real+(advance-parent_advance)/2)/1440,6),
                        y=round(point['y']-translation.imag/1440,6)))


def build(directory, workers):
    with ProcessPoolExecutor(workers) as pool:
        faces = list(pool.map(scan_face, [(directory, family) for family in TEXT]))
    fonts = {family: info for family,info,_ in faces}
    rows = {(r['family'], r['glyph'], r['wght'], r['wdth'], r['RADI']):r
            for _,_,found in faces for r in found}
    for cell in scan_known(directory, WIDTHS, RADII):
        if not cell['findings']:
            continue
        key = tuple(cell[k] for k in ('family','glyph','wght','wdth','RADI'))
        row = rows.setdefault(key, {**{k:cell[k] for k in ('family','glyph','glyphID','wght','wdth','RADI')},
                                    'base':cell['glyph'], 'findings':[]})
        for p in cell['findings']:
            rule = p['rule']
            metrics = {k:v for k,v in p.items() if k not in ('rule','x','y')}
            score = metrics.get('fractionMissing',metrics.get('normalOffset',1))
            row['findings'].append(dict(rule=rule,x=p['x'],y=p['y'],score=score,metrics=metrics))
    include_composites(directory, rows)
    from scan_icon_candidates import scan_icons
    family,info,icons = scan_icons(directory, WIDTHS, RADII, WEIGHTS)
    fonts[family] = info
    for r in icons:
        key = tuple(r[k] for k in ('family','glyph','wght','wdth','RADI'))
        rows[key] = r
    print(f"{family}: {info['directionalForms']} directional forms, {len(icons)} candidate cells", flush=True)
    return dict(schema='admiralty-optical-candidates/1', annotationFrame=FRAME, fonts=fonts,
                grid=dict(wght=WEIGHTS,wdth=WIDTHS,RADI=RADII), rows=list(rows.values()))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--fonts', type=Path, default=OUTPUT)
    parser.add_argument('--workers', type=int, default=3)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    report = build(args.fonts, args.workers)
    args.out.write_text(json.dumps(report, ensure_ascii=False, separators=(',',':')))
