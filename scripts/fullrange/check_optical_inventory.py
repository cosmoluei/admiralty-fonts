"""Check small-size ink for every glyph and physical stroke sections in the exported fonts."""
import ctypes
import hashlib
import json
import math
from concurrent.futures import ProcessPoolExecutor
from itertools import product

import freetype as ft
import numpy as np
import uharfbuzz as hb
from fontTools.ttLib import TTFont

from build_text_family import OUTPUT, REVIEW, TEXT
from check_word_proof import Edges, section


# Record the weakest rendered instance at reading size, including between masters.
SAMPLES = list(product((100, 400, 900), (65, 100, 150), (0, 100))) + [
    (175, 73, 27), (350, 113, 73), (525, 142, 27), (775, 82.5, 73)]
DEFAULT = (400, 100, 0)
PPEM = 24


def glyph_ink(face, gid):
    face.load_glyph(gid, ft.FT_LOAD_RENDER | ft.FT_LOAD_NO_HINTING | ft.FT_LOAD_NO_BITMAP)
    bitmap = face.glyph.bitmap
    if not bitmap.width or not bitmap.rows:
        return 0, 0
    data = ctypes.string_at(bitmap._FT_Bitmap.buffer, bitmap.pitch * bitmap.rows)
    coverage = np.frombuffer(data, np.uint8).reshape(bitmap.rows, bitmap.pitch)[:, :bitmap.width]
    return round(float(coverage.sum()) / 255, 3), int(coverage.max())


def unsheared(font, gid, slope):
    pen = Edges(None, 1)
    font.draw_glyph_with_pen(gid, pen)
    edges = np.asarray(pen.edges)
    return edges - slope * edges.imag


def thin_sections(font, tt, family):
    slope = math.tan(math.radians(9.5)) if family.endswith('-Italic') else 0
    measurements = []
    for width, radius in product((65, 82.5, 100, 125, 150), (0, 50, 100)):
        font.set_variations(dict(wght=100, wdth=width, RADI=radius))
        for name in ('pi',) if 'Serif' in family else ('E', 'F', 'H', 'I', 'L', 'T', 'pi'):
            rails = unsheared(font, tt.getGlyphID(name), slope)
            for height in (137, 193, 247):
                cuts = section(rails, height)
                assert len(cuts) and np.max(abs(cuts[1::2]-cuts[::2]-24)) < 1.8, (
                    family, name, 'Thin upright', width, radius, height, cuts)
        if 'Serif' not in family:
            for name in ('Z', 'seven'):
                diag = unsheared(font, tt.getGlyphID(name), slope)
                bands = np.array([section(diag, h) for h in (182, 232, 282)])
                tilt = (bands[-1].mean()-bands[0].mean())/100
                pen = np.diff(bands, axis=1)/math.hypot(1, tilt)
                assert max(abs(pen.ravel()-24)) < 1.8, (family, name, 'Thin diagonal', width, radius, pen)
        curve = unsheared(font, tt.getGlyphID('S'), slope)
        xs = curve.real.min() + np.linspace(.36, .64, 13) * np.ptp(curve.real)
        slices = [section(curve, x, vertical=True) for x in xs]
        assert all(len(row) == 6 for row in slices), ('S spine crossings', width, radius)
        bands = np.array([row[2:4] for row in slices])
        slopes = np.gradient(bands.mean(axis=1), xs)
        normal = (bands[:, 1] - bands[:, 0]) / np.hypot(1, slopes)
        assert min(normal) > 18 and max(normal) < 33, ('S spine weight', width, radius, normal)
        assert max(slopes) < 0, ('S inflection', width, radius, slopes)
        upright = unsheared(font, tt.getGlyphID('germandbls'), slope)
        widths = [np.diff(section(upright, y)[:2])[0] for y in (120, 260, 460)]
        assert min(widths) > 19 and max(widths) < 30, ('Eszett shaft', width, radius, widths)
        dot = unsheared(font, tt.getGlyphID('period'), slope)
        diameter = np.ptp(dot.imag)
        assert 38 <= diameter <= 43, ('Thin period diameter', width, radius, diameter)
        # Division and minus are read together. Preserve the length of the
        # division bar when its two detached dots are reduced for Thin.
        divide = unsheared(font, tt.getGlyphID('divide'), slope)
        minus = unsheared(font, tt.getGlyphID('minus'), slope)
        assert np.ptp(divide.real) > .65*np.ptp(minus.real), ('short division bar', width, radius)
        assert np.ptp(divide.imag) > 280, ('division dot spacing', width, radius)
        amp = unsheared(font, tt.getGlyphID('ampersand'), slope)
        heights = np.arange(179, 272, 4)
        cuts = [section(amp, y) for y in heights]
        assert all(len(row) == 6 for row in cuts), ('ampersand exit', width, radius)
        amp_widths = []
        for start in (2, 4):
            pair = np.asarray(cuts)[:, start:start+2]
            inclination = np.gradient(pair.mean(axis=1), heights)
            amp_widths.extend((pair[:, 1] - pair[:, 0]) / np.hypot(1, inclination))
        assert min(amp_widths) >= 20 and max(amp_widths) <= 28, ('ampersand stroke', width, radius, amp_widths)
        record = [min(normal), max(normal), *widths, diameter, min(amp_widths), max(amp_widths)]
        measurements.append([width, radius, *np.round(record, 2)])
    return measurements


def inspect(family):
    path = OUTPUT / (family + '[wght,wdth,RADI].ttf')
    face = ft.Face(str(path))
    face.set_pixel_sizes(0, PPEM)
    with TTFont(path) as tt:
        order = tt.getGlyphOrder()
        face.set_var_design_coords(DEFAULT)
        baseline = [glyph_ink(face, i)[0] for i in range(len(order))]
        records = [[None, None, None] for name in order]
        for index, location in enumerate(SAMPLES):
            face.set_var_design_coords(location)
            for gid, name in enumerate(order):
                mass, peak = glyph_ink(face, gid)
                # Symbol alternates are inspected at every location, including
                # positions outside their active substitution interval.
                if baseline[gid] and '.design' not in name:
                    assert mass > .10 and peak >= 15, (family, name, location, mass, peak)
                if name.split('.')[0] in ('dotbelowcomb', 'dotaccentcomb', 'dotaccent'):
                    assert mass >= .48, (family, name, location, 'faint detached dot', mass)
                if records[gid][0] is None or mass < records[gid][0]:
                    records[gid] = [mass, peak, index]
        result = dict(sha256=hashlib.sha256(path.read_bytes()).hexdigest(), count=len(order),
                      glyphs=dict(zip(order, records)))
        if family in TEXT:
            font = hb.Font(hb.Face(path.read_bytes()))
            result['thin_sections'] = thin_sections(font, tt, family)
    return family, result


if __name__ == '__main__':
    families = [*TEXT, 'AdmiraltySymbols']
    with ProcessPoolExecutor(3) as pool:
        results = dict(pool.map(inspect, families))
    report = dict(ppem=PPEM, grid=SAMPLES, glyph_fields=['minimum ink in pixel equivalents',
                  'peak alpha at minimum ink', 'grid index'], section_fields=['width', 'radius',
                  'minimum normal S spine', 'maximum normal S spine', 'Eszett shaft at y=120',
                  'Eszett shaft at y=260', 'Eszett shaft at y=460', 'period diameter',
                  'minimum ampersand diagonal/exit', 'maximum ampersand diagonal/exit'], faces=results)
    (REVIEW / 'audits' / 'optical-inventory.json').write_text(json.dumps(report, separators=(',', ':')))
    count = sum(r['count'] for r in results.values())
    print(f'{count} glyph records at {PPEM}px across {len(SAMPLES)} locations: '
          f'{count*len(SAMPLES)} raster checks, 90 Thin section sets.')
