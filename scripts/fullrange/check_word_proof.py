"""Measure the outlines decoded from the word proof, in units of a 1000-unit em."""
import base64
from io import BytesIO
from pathlib import Path
import re

import numpy as np
import pathops
from fontTools.pens.basePen import BasePen
from fontTools.ttLib import TTFont

from stroke_geometry import bezier, curvature, fair_curves, unit
from study_shapes import LETTERS, draw_letter, letter_outline

PROOF = Path(__file__).parent / "review/word-proof.html"
CONTOURS = {letter: (2 if letter in "adegi" else 1) for letter in LETTERS}


class Edges(BasePen):
    """Flatten the exported outlines for ray intersections, retaining endpoint tangents."""
    def __init__(self, glyphset, scale):
        super().__init__(glyphset)
        self.scale = scale
        self.edges = []
        self.turns = []
        self.directions = []
        self.contours = 0

    def _moveTo(self, pt):
        self.current = self.start = complex(*pt)/self.scale
        self.directions = []

    def _lineTo(self, pt):
        end = complex(*pt)/self.scale
        if abs(end-self.current) > 1e-8:
            self.edges.append((self.current,end))
            self.directions.append((end-self.current,end-self.current))
        self.current = end

    def _qCurveToOne(self, control, pt):
        a = self.current
        b, c = complex(*control)/self.scale, complex(*pt)/self.scale
        # Quadratic chord deviation is bounded by |a - 2b + c| / (4n²).
        count = max(2,int(np.ceil(np.sqrt(abs(a-2*b+c)/.04))))
        ts = np.arange(count+1)/count
        points = (1-ts)**2*a + 2*ts*(1-ts)*b + ts**2*c
        self.edges.extend(zip(points,points[1:]))
        self.directions.append((b-a,c-b))
        self.current = c

    def _curveToOne(self, c1, c2, pt):
        a = self.current
        b,c,d = [complex(*p)/self.scale for p in (c1,c2,pt)]
        # Linear interpolation error is at most max |B″| / (8n²).
        second = 6*max(abs(a-2*b+c),abs(b-2*c+d))
        count = max(2,int(np.ceil(np.sqrt(second/.08))))
        ts = np.arange(count+1)/count
        points = (1-ts)**3*a + 3*ts*(1-ts)**2*b + 3*ts**2*(1-ts)*c + ts**3*d
        self.edges.extend(zip(points,points[1:]))
        self.directions.append((b-a,d-c))
        self.current = d

    def _closePath(self):
        self.contours += 1
        if abs(self.current-self.start) > .001:
            end = self.start*self.scale
            self._lineTo((end.real,end.imag))
        for i,(v,_) in enumerate(self.directions):
            u = self.directions[i-1][1]
            if abs(v) and abs(u):
                self.turns.append(np.angle(u.conjugate()*v,deg=True))


def section_limits(starts, vectors, center, normal):
    ends = starts+vectors
    projections = ((starts-center)*normal.conjugate()).imag
    others = ((ends-center)*normal.conjugate()).imag
    hit = (projections > 0) != (others > 0)
    t = projections[hit]/(projections[hit]-others[hit])
    hits = ((starts[hit]+t*vectors[hit]-center)*normal.conjugate()).real
    return max(hits[hits<0]), min(hits[hits>=0])


def crossings(starts, vectors, center, normal):
    lo,hi=section_limits(starts,vectors,center,normal)
    return hi-lo


def section(edges, coordinate, vertical=False):
    """Sorted crossings of a horizontal or vertical line through the exported ink."""
    points = edges if vertical else (edges.imag + 1j * edges.real)
    start, end = points[:, 0], points[:, 1]
    hit = (start.real > coordinate) != (end.real > coordinate)
    delta = end[hit] - start[hit]
    return np.sort((start[hit] + delta * (coordinate - start[hit].real) / delta.real).imag)


def check_focus(font, weight, width, outlines):
    # The lower bowl and the opening above its waist each need room. Measure
    # both in the exported ink, at the same fractional position at each width.
    a = outlines["a"]
    mid = (a.real.min() + a.real.max()) / 2
    hits = section(a, mid, vertical=True)
    assert len(hits) == 6, ("a counter or aperture closed", hits)
    lower, upper = hits[2]-hits[1], hits[4]-hits[3]
    assert min(lower, upper) > (115 if weight == 900 else 210), ("a clearances", lower, upper)
    stem = section(a, 12)
    assert abs(stem[-1]-stem[-2] - (119 if weight == 900 else 24)) < 2, ("a foot", stem)
    stems = section(outlines["m"], 90)
    assert len(stems) == 6
    target = 24 if weight == 100 else 128
    assert np.allclose(stems[1::2] - stems[::2], target, atol=.05)
    # Find the valley between the two peaks, including its rounded floor.
    mid = (stems[2] + stems[3]) / 2
    width_of_counter = stems[4] - stems[3]
    cuts = np.linspace(mid-15, stems[3]+width_of_counter/2, 101)
    valley = min(max(section(outlines["m"], x, vertical=True)) for x in cuts)
    depth = outlines["m"].imag.max() - valley
    assert 85 < depth < 140, ("m crotch", depth)

    eye = section(outlines["e"], font["hmtx"]["e"][0]/2, vertical=True)
    assert len(eye) == 6
    clear = eye[-2] - eye[-3]
    bar = eye[-3] - eye[-4]
    assert clear > (110 if weight == 900 else 210), ("e upper counter", clear)
    assert abs(bar - (101 if weight == 900 else 24)) < .05

    s = outlines["s"]
    upper = s[s.imag > 310].real
    lower = s[s.imag < 210].real
    assert 1.05 < np.ptp(lower)/np.ptp(upper) < 1.16, "s lobe balance"

    g = outlines["g"]
    bowl = g[g.imag > 0].real
    tail_inset = (g[g.imag < -90].real.min() - bowl.min()) / np.ptp(bowl)
    assert .04 < tail_inset < .19, ("g terminal", width, tail_inset)
    assert abs(g.imag.min() + 224) < .05, "g descender"
    return depth, clear


def check(font, weight, width):
    glyphs = font.getGlyphSet()
    scale = font['head'].unitsPerEm/1000
    errors, bends, turns = [], [], []
    outlines = {}
    tested = 0
    for name in LETTERS:
        advance = font['hmtx'][name][0]/scale
        geometry = draw_letter(name,advance,weight,width)
        thickness = geometry.thickness
        flat = Edges(glyphs,scale)
        glyphs[name].draw(flat)
        assert flat.contours == CONTOURS[name], (name, flat.contours)
        turns.extend(flat.turns)
        ends = np.asarray(flat.edges)
        if name in "amesg":
            outlines[name] = ends
        # Measure in the pen's circular coordinate system. A Black curve made
        # with an elliptical pen has different apparent widths by direction.
        ends = ends.real + 1j * ends.imag / geometry.vertical_ratio
        starts, vectors = ends[:,0], ends[:,1]-ends[:,0]
        shape = pathops.Path()
        glyphs[name].draw(shape.getPen())
        shape = shape.transform(1/scale,0,0,1/scale)
        ink = shape.area
        shape.simplify()
        assert abs(shape.area-ink) < .3, (name, shape.area-ink)
        # Classify intersections using the design, independently of the decoded
        # font. At a fork, a normal can legitimately enter a neighbouring stroke.
        design = letter_outline(name,advance,weight,width,blend_branches=True)
        for spine in geometry.spines:
            for curve in fair_curves(spine):
                for t in np.linspace(0,1,101):
                    v = bezier(curve.velocity,t)
                    bends.append(abs(curvature(v,bezier(curve.acceleration,t)))*thickness/2)
                for t in np.linspace(.08,.92,19):
                    p,v = curve.boundary(t,0)
                    normal = 1j*unit(v)
                    if name == 'u':
                        p,normal = complex(advance,520)-p,-normal
                    tested += 1
                    edges = [p+sign*normal*(thickness/2+.15) for sign in (-1,1)]
                    if any(design.contains((q.real,q.imag * geometry.vertical_ratio)) for q in edges):
                        continue
                    measured = crossings(starts,vectors,p,normal)
                    errors.append(abs(measured-thickness))
    assert max(bends) < .97, (weight, width, 'offset cusp', max(bends))
    assert len(errors) >= .60*tested, (len(errors), tested)
    assert max(errors) < .45, (weight,width,'width error',max(errors))
    assert max(turns) < .25, (weight,width,"re-entrant corner",max(turns))
    # Clockwise ink contours have negative turns at the intentional flat cuts.
    # Positive turns are re-entrant outline seams.
    depth, clear = check_focus(font, weight, width, outlines)
    return len(errors),tested,max(errors),max(bends),max(turns),depth,clear


def main():
    faces = dict(re.findall(r"@font-face\{font-family:(\w+);[^}]+?base64,([^)]*)\)",PROOF.read_text()))
    for name in ['Study100x65','Study100x100','Study100x150','Study900x65','Study900x100','Study900x150','StudyAllowance']:
        weight,width = (900,65) if name=='StudyAllowance' else map(int,name[5:].split('x'))
        font = TTFont(BytesIO(base64.b64decode(faces[name])))
        count,total,error,bend,turn,depth,clear = check(font,weight,width)
        print(f"{name}  {count}/{total} free strokes  max error {error:.3f}u  max radius × curvature {bend:.3f}  max re-entrant turn {turn:.2f}°  m crotch {depth:.0f}u  e eye {clear:.0f}u")


if __name__ == '__main__':
    main()
