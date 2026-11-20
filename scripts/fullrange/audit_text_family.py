"""Compare all encoded and unencoded text glyphs to the reference; audit shaped text across axes."""
import argparse
import collections
import itertools
import hashlib
import json
from pathlib import Path

import numpy as np
import pathops
import uharfbuzz as hb
from fontTools.ttLib import TTFont

from build_text_family import OUTPUT, RELEASE, TEXT, ints, simple
from junction_drawings import revised_default
from attachments import ATTACHED, is_mark
from sign_masters import mono_perthousand_tracks

LOCATIONS = list(itertools.product(range(100,901,100),(65,82.5,100,125,150),(0,50,100)))
BETWEEN_MASTERS = list(itertools.product((175,350,525,775),(73,113,142),(27,73)))


def pen_shape(font,gid):
    p = pathops.Path()
    font.draw_glyph_with_pen(gid,p.getPen())
    return p


def stats(path):
    # Tiny numerical self-intersections are recorded separately from closed
    # counters and main components large enough to change a printed letter.
    path.simplify()
    significant = [c for c in path.contours if abs(c.area)>4.]
    return len(significant),sum(p.clockwise for p in significant),abs(path.area)


def shaped(font,text):
    b = hb.Buffer()
    b.add_str(text)
    b.guess_segment_properties()
    hb.shape(font,b)
    return [(g.codepoint,p.x_advance,p.x_offset,p.y_offset) for g,p in zip(b.glyph_infos,b.glyph_positions)]


def mono_perthousand_fits(path, slant, width):
    # Measure in the writing direction: an italic shear adds to screen width
    # even when a ring is pinched. The merged outline must retain its holes.
    upright = path.transform(1, 0, -slant, 1, 0, 0)
    left, _, right, _ = upright.bounds
    holes = [c.bounds for c in upright.contours if c.clockwise]
    return (540 + .30 * (width - 65) <= right - left <= 600 and len(holes) == 3
            and all(x1 - x0 >= 60 and (x1 - x0) >= .45 * (y1 - y0)
                    for x0, y0, x1, y1 in holes))


def inspect(family, locations):
    dest = OUTPUT / (family+"[wght,wdth,RADI].ttf")
    reference = RELEASE.with_name(family+"[wght].ttf")
    tt = TTFont(dest)
    rt = TTFont(reference)
    assert rt.getBestCmap()==tt.getBestCmap() and rt.getGlyphOrder()==tt.getGlyphOrder()
    gids = tt.getGlyphOrder()
    face = hb.Font(hb.Face(dest.read_bytes()))
    mono_permille = tt.getGlyphID('perthousand') if 'Mono' in family else None
    slant = np.tan(np.deg2rad(-tt['post'].italicAngle))
    old = hb.Font(hb.Face(reference.read_bytes()))
    base = [stats(pen_shape(old,i)) for i in range(len(gids))]
    # These three glyphs have revised skeletons and retain their native advances.
    for name in ('ae','oe','uni20BA'):
        base[tt.getGlyphID(name)] = stats(revised_default(rt, family, name))
    if mono_permille is not None:
        # Compare the encoded default with the approved redrawn master using
        # the same ink-area tolerance as the other redesigned defaults.
        tracks, ends = mono_perthousand_tracks(slant, [(400, 100)])
        points = ints(tracks[0])
        reference_path = pathops.Path()
        simple(points, ends, [1, 0] * (len(points) // 2)).draw(reference_path.getPen(), None)
        base[mono_permille] = stats(reference_path)
    mark_targets={}
    # The source draws the Dutch IJ as two letters on the Mono cell. Only
    # their foot tips happen to touch in the released upright default.
    if family=='AdmiraltyMono':
        mark_targets[tt.getGlyphID('IJ')]=(2,0)
    source_contacts={}
    for i,name in enumerate(gids):
        drawing=tt['glyf'][name]
        if not drawing.isComposite():
            continue
        components=[c.glyphName for c in drawing.components]
        if len(components)<2 or not all(is_mark(c) for c in components[1:]):
            continue
        # A detached accent has its own boundary. A cedilla, horn or ogonek
        # shares one with the base. Derive the target independently of the
        # candidate's placement. Some released ascender accents touch at the
        # default, and one released horn traps a tiny counter at its joint.
        children=[base[tt.getGlyphID(n)] for n in components]
        count=sum(c[0] for c in children)-sum(n in ATTACHED for n in components[1:])
        holes=sum(c[1] for c in children)
        mark_targets[i]=(count,holes)
        if mark_targets[i]!=base[i][:2]:
            source_contacts[name]=[base[i][:2],mark_targets[i]]
    base_adv = [old.get_glyph_h_advance(i) for i in range(len(gids))]
    problems = collections.defaultdict(lambda:collections.defaultdict(list))
    defaults = {}
    for i,n in enumerate(gids):
        form = pen_shape(face,i)
        ncont,wind,area = stats(form)
        ref = base[i]
        if ((ncont,wind)!=ref[:2] or abs(area-ref[2])>max(70,.004*ref[2])
                or (i == mono_permille and not mono_perthousand_fits(form, slant, 100))
                or face.get_glyph_h_advance(i)!=base_adv[i]):
            defaults[n] = [ncont,wind,round(area,1),ref[:2],round(ref[2],1)]
    previous = {}
    for w,d,r in locations:
        face.set_variations(dict(wght=w,wdth=d,RADI=r))
        loc = f"{w}/{d}/{r}"
        for i,n in enumerate(gids):
            orig = base[i]
            path = pen_shape(face,i)
            count,wind,area = stats(path)
            if i == mono_permille and not mono_perthousand_fits(path, slant, d):
                problems["perthousand_proportions"][n].append(loc)
            target=mark_targets.get(i,orig[:2])
            release_position=(w,d)==(400,100) and (count,wind)==orig[:2]
            if (count,wind)!=target and not release_position:
                problems["topology"][n].append(loc)
            # Test a detached stop in absolute units. A percentage of a large
            # Regular Mono dot is a poor measure of its legibility in Thin.
            dots=n in {"period","periodcentered","periodcentered.case","colon","colon.case"}
            minimum=280*max(orig[0],1) if dots else max(2,.045*orig[2])
            if orig[2]>0 and area < minimum:
                problems["lost_ink"][n].append(loc)
            if area > 0 and (coords:=path.bounds) and (max(map(abs,coords))>4800):
                problems["bounds"][n].append(loc)
            if "Mono" in family and face.get_glyph_h_advance(i)!=base_adv[i]:
                problems["fixed_cell"][n].append(loc)
            key = i,d,r
            if key in previous and area < previous[key] - max(30, .008*area):
                problems["weight_reversal"][n].append(loc)
            previous[key]=area
    return dict(family=family,glyphs=len(gids),locations=len(locations),outlines=len(gids)*len(locations),
                default_differences=defaults,exceptions=problems,reference_accent_contacts=source_contacts,
                sha256=hashlib.sha256(dest.read_bytes()).hexdigest(),glyph_order=gids,
                sample_grid=[list(v) for v in locations])


if __name__=="__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("family",choices=TEXT)
    parser.add_argument("--out",type=Path,required=True)
    parser.add_argument("--corners",action="store_true")
    parser.add_argument("--strict",action="store_true",help="return nonzero for any unresolved difference")
    args = parser.parse_args()
    locs = [p for p in LOCATIONS if p[0] in (100,400,900) and p[1] in (65,100,150) and p[2] in (0,100)] if args.corners else sorted(LOCATIONS+BETWEEN_MASTERS)
    report=inspect(args.family,locs)
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(report,separators=(",",":")))
    print(report["family"],report["outlines"],"default differences",len(report["default_differences"]))
    for kind,values in report["exceptions"].items():
        print(kind,len(values),"glyphs",sum(map(len,values.values())),"instances")

    if args.strict and (report["default_differences"] or report["exceptions"]):
        raise SystemExit(1)
