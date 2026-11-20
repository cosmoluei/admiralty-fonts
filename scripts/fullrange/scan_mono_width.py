"""Find reversals in Mono ink width, starting from a versioned glyph review."""
import argparse
import ctypes
import hashlib
import json
import math
from itertools import product
from pathlib import Path

import freetype as ft
import numpy as np
from fontTools.ttLib import TTFont

from build_text_family import OUTPUT
from scan_family_candidates import FRAME, RADII, WEIGHTS, WIDTHS

CELL = 600
# Triage threshold in font units, relative to the narrower endpoint.
# One eighth of a Mono cell is large enough to see at typical proof sizes.
MIN_DIP = CELL / 8
AXES = tuple(product(WEIGHTS, WIDTHS, RADII))


def measure(font_path, gids, slope):
    face = ft.Face(str(font_path))
    matrix = ft.Matrix(65536, -round(slope * 65536), 0, 65536)
    slot = face.glyph
    widths = np.zeros((len(WEIGHTS), len(WIDTHS), len(RADII), len(gids)), dtype=int)
    for (wi, di, ri), axes in zip(np.ndindex(widths.shape[:3]), AXES):
        face.set_var_design_coords(axes)
        for index, gid in enumerate(gids):
            face.load_glyph(gid, ft.FT_LOAD_NO_SCALE | ft.FT_LOAD_NO_HINTING | ft.FT_LOAD_NO_BITMAP)
            if slot.metrics.horiAdvance != CELL:
                raise ValueError(f"{font_path.name} gid {gid} changed advance at {axes}")
            outline = slot.outline
            if outline.n_points:
                if slope:
                    ft.FT_Outline_Transform(ctypes.byref(outline._FT_Outline), ctypes.byref(matrix))
                box = outline.get_bbox()
                widths[wi, di, ri, index] = box.xMax - box.xMin
    return widths


def scan(report_path, directory):
    raw = report_path.read_bytes()
    source = json.loads(raw)
    families = ('AdmiraltyMono', 'AdmiraltyMono-Italic')
    if (source['schema'] != 'admiralty-glyph-review/1' or not source['issues']
            or source['issueCount'] != len(source['issues']) or source['annotationFrame'] != FRAME):
        raise ValueError('Expected a nonempty review export in the glyph proof coordinate system')
    marks = {}
    for issue in source['issues']:
        axes = tuple(issue[a] for a in ('wght', 'wdth', 'RADI'))
        if issue['family'] not in families or axes not in AXES:
            raise ValueError('This scan covers the published Mono design grid')
        marks[issue['family'], issue['glyph'], axes] = issue
    requested = {key[1] for key in marks}
    grid = dict(wght=WEIGHTS, wdth=WIDTHS, RADI=RADII)
    fonts, rows = {}, []
    for family in families:
        path = directory / (family + '[wght,wdth,RADI].ttf')
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        with TTFont(path) as font:
            names = font.getGlyphOrder()
            gids = [i for i, n in enumerate(names) if font['hmtx'][n][0] == CELL]
            slope = math.tan(math.radians(-font['post'].italicAngle))
            if font['head'].unitsPerEm != FRAME['fontSize'] or [a.axisTag for a in font['fvar'].axes] != list(grid):
                raise ValueError(f'Unexpected units or axes in {family}')
            for (f, n, _), record in marks.items():
                if f == family and (record['fontSha256'] != digest or record['fontFile'] != path.name
                                    or record['glyphID'] not in gids or names[record['glyphID']] != n):
                    raise ValueError(f'Review and font differ for {f} {n}')
        widths = measure(path, gids, slope)
        dips = np.minimum(widths[0], widths[-1]) - widths
        percent = gids.index(names.index('percent'))
        fonts[family] = dict(file=path.name, sha256=digest, glyphs=len(gids),
                             inkGlyphs=int(widths.any(axis=(0, 1, 2)).sum()))
        for i, gid in enumerate(gids):
            name = names[gid]
            for (wi, di, ri), axes in zip(np.ndindex(widths.shape[:3]), AXES):
                dip = int(dips[wi, di, ri, i])
                hit = dip >= MIN_DIP
                if not hit and name not in requested:
                    continue
                mark = marks.get((family, name, axes))
                rule = 'cell-width-dip' if hit else 'cell-width-context'
                series = widths[:, di, ri, i].tolist()
                finding = dict(rule=rule, scope='glyph', score=dip,
                               metrics=dict(inkWidth=series[wi], cell=CELL, widths=series, dip=dip))
                if name == 'perthousand':
                    finding['metrics']['percentInk'] = int(widths[wi, di, ri, percent])
                if mark:
                    finding['sourceMark'] = dict(note=mark['note'], regions=mark['regions'])
                rows.append(dict(family=family, glyph=name, base=name, glyphID=gid,
                                 wght=axes[0], wdth=axes[1], RADI=axes[2], findings=[finding]))
    return dict(schema='admiralty-mono-width-scan/1', sourceExport=source['exportedAt'],
                sourceSha256=hashlib.sha256(raw).hexdigest(), annotationFrame=FRAME, grid=grid,
                minDip=MIN_DIP, fonts=fonts, rows=rows)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('review', type=Path)
    parser.add_argument('--fonts', type=Path, default=OUTPUT)
    parser.add_argument('--out', required=True, type=Path)
    args = parser.parse_args()
    report = scan(args.review, args.fonts)
    args.out.write_text(json.dumps(report, ensure_ascii=False, separators=(',', ':')) + '\n')
    print(f"{len(report['rows'])} review cells in {args.out}")
