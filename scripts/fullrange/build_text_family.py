"""Compile complete three-axis text-family candidates, retaining OpenType layout and components."""
import argparse
import copy
import functools
import math
from array import array

import numpy as np
from fontTools.designspaceLib import DesignSpaceDocument, AxisDescriptor, SourceDescriptor, InstanceDescriptor
from fontTools.fontBuilder import FontBuilder
from fontTools.ttLib import TTFont
from fontTools.ttLib.tables import ttProgram
from fontTools.ttLib.tables.TupleVariation import TupleVariation
from fontTools.ttLib.tables._g_l_y_f import Glyph, GlyphCoordinates
from fontTools.pens.recordingPen import RecordingPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.ufoLib import UFOReader
from fontTools.varLib import build as merge_layout
from fontTools.varLib.instancer import instantiateVariableFont

from build_axis_study import AXES, CELLS, FILENAME, LETTERS, MODEL, REVIEW
from build_word_proof import RELEASE
from optical_curves import optical_tracks
from thin_figures import NAMES as THIN_FIGURES, replace_special_thin, replace_masters
import mono_heavy
import junction_drawings
import sign_masters
import member_masters
import reviewed_capitals
import reviewed_strokes
from operator_masters import operator_tracks
from optical_master import OpticalMaster
from accent_masters import accent_name, accent_tracks
from attachments import ATTACHED, Attachments
from capital_masters import DIAGONALS, SLASHED_ZEROS, capital_tracks, slashed_zero_tracks
from cross_masters import cross_tracks, multiply_tracks
from cursive_masters import MONO_BOWLS, cursive_tracks, inherited_italic_tracks
from punctuation_masters import PUNCT, period_coords, punctuation_coords, round_dots
from serif_letters import LETTERS as SERIF_LETTERS, letter_tracks
from serif_t import serif_t_tracks
from mark_interpolation import refine_marks
from punctuation_scope import DOT_ROLES, punctuation_names
from punctuation_spacing import apply_punctuation_spacing, remove_punctuation_spacing

ROOT = RELEASE.parents[2]
TEXT = [f"Admiralty{family}{style}" for family in ("Sans","Serif","Mono") for style in ("","-Italic")]
OUTPUT = REVIEW / "families"
AXIS_NAMES = {"wght":"Weight","wdth":"Width","RADI":"Corner radius"}
WEIGHTS = ("Thin","ExtraLight","Light","Regular","Medium","SemiBold","Bold","ExtraBold","Black")
# The widest of the duplexed Thin drawings plus 20 units between repeated dashes.
THIN_DASH_ADVANCES = {"endash": 599, "emdash": 918}


def fullrange_unique_id(font, postscript_name):
    version = font["head"].fontRevision
    vendor = font["OS/2"].achVendID.strip()
    return f"{version:.3f};{vendor};{postscript_name}"


def study_instances():
    font = TTFont(REVIEW / "fonts" / (FILENAME+".ttf"))
    return {(w,d,r):instantiateVariableFont(font,dict(wght=w,wdth=d,RADI=r),optimize=False,updateFontNames=False)
            for w,d in CELLS for r in (0,100)}


def ints(z):
    return np.rint(np.column_stack([z.real,z.imag])).astype(np.int32)


def var_tuples(coords):
    coords = [np.asarray(points, dtype=np.int32) for points in coords]
    deltas = MODEL.getDeltas(coords)
    return [TupleVariation(support,[tuple(p) for p in delta.tolist()])
            for support,delta in zip(MODEL.supports[1:],deltas[1:]) if np.any(delta)]


def simple(coords, ends, flags):
    glyph = Glyph()
    glyph.numberOfContours = len(ends)
    glyph.endPtsOfContours = ends
    glyph.coordinates = GlyphCoordinates(coords.tolist())
    glyph.flags = array("B", flags)
    glyph.program = ttProgram.Program()
    glyph.program.fromBytecode([])
    return glyph


class TextDesign:
    def __init__(self, family, study):
        self.family = family
        self.study = study
        release = TTFont(RELEASE.with_name(family+"[wght].ttf"),recalcTimestamp=False)
        # Reapply punctuation spacing once after varLib has merged the native
        # layout. A baked one-axis lookup would otherwise be scaled by width.
        remove_punctuation_spacing(release)
        self.regular = instantiateVariableFont(release,{"wght":400},optimize=False)
        self.bold = instantiateVariableFont(release,{"wght":700},optimize=False)
        self.mono = "Mono" in family
        self.serif = "Serif" in family
        self.slant = math.tan(math.radians(9.5)) if "Italic" in family else 0
        self.unicode = {n:cp for cp,n in self.regular.getBestCmap().items()}
        self.punctuation = punctuation_names(self.regular.getBestCmap(), self.regular.getGlyphOrder())
        self.advance0 = {n:x[0] for n,x in self.regular["hmtx"].metrics.items()}
        self.restore_accent_components()
        self.attachments = Attachments(self)

    @functools.cached_property
    def upright(self):
        return TextDesign(self.family.removesuffix("-Italic"), self.study) if self.slant else self

    def punctuation_advance(self, name, weight):
        dash = name.removesuffix(".case")
        if not self.mono and weight == 100 and dash in THIN_DASH_ADVANCES:
            return THIN_DASH_ADVANCES[dash]
        return self.upright.advance(name, weight, 100)

    def restore_accent_components(self):
        # The legacy one-axis compiler flattened some Vietnamese capitals
        # because the accent scale varied by master. Restore the actual UFO
        # recipe so those letters use this font's drawn base and accent too.
        source=self.family if self.slant else self.family+'-Regular'
        glyphs=UFOReader(ROOT/'sources'/(source+'.ufo')).getGlyphSet()
        glyf=self.regular['glyf']
        for name,cp in self.unicode.items():
            if not 0x1ea0<=cp<=0x1ef9 or glyf[name].isComposite():
                continue
            pen=RecordingPen()
            glyphs[name].draw(pen)
            if not pen.value or any(op!='addComponent' for op,_ in pen.value):
                continue
            target=TTGlyphPen(glyphs)
            pen.replay(target)
            restored=target.glyph()
            restored.recalcBounds(glyf)
            glyf[name]=restored

    @functools.lru_cache(maxsize=None)
    def advance(self, name, w, d):
        old = self.advance0[name]
        if self.mono or not old or (w,d)==(400,100):
            return old
        font = self.study[w,d,0]
        base = {"dotlessi":"i","dotlessj":"j","i.loclTRK":"i"}.get(name,name)
        if base in LETTERS and len(base)==1:
            return round(font["hmtx"][base][0]/4)
        glyph = self.regular["glyf"][name]
        if glyph.isComposite():
            child = glyph.components[0].glyphName
            if self.advance0[child] == old:
                return self.advance(child,w,d)
        if glyph.numberOfContours == 0:
            return round(old*d/100)
        # A shared advance registry keeps serif and sans duplexed, including
        # punctuation, tabular figures, alternates and precomposed accents.
        return round(old*(font["hmtx"]["n"][0]/4)/584)

    @functools.lru_cache(maxsize=None)
    def transform(self, name, w, d):
        old = self.advance0[name]
        new = self.advance(name,w,d)
        if not old:
            return 1+.36*(d/100-1),0.
        if self.mono:
            width = 1+(.70 if d<100 else .49)*(d/100-1)
            glyph = self.regular["glyf"][name]
            if glyph.isComposite() and self.advance0[glyph.components[0].glyphName]==old:
                return self.transform(glyph.components[0].glyphName,w,d)
            if glyph.numberOfContours and (w==900 or d>100):
                # Reserve real sidebearings *after* the extra black stroke
                # ink is fitted. Wide M/W and m otherwise cross the next cell.
                if glyph.numberOfContours>0:
                    points=np.asarray(glyph.coordinates)
                    span=max(np.ptp(points[:,0]-self.slant*points[:,1]),1)
                else:
                    span=max(glyph.xMax-glyph.xMin,1)
                if w==900:
                    # The pound's open bar and baseline can use more of the
                    # cell. An M-sized reservation makes its Black lighter
                    # than its ExtraBold at expanded widths.
                    allowance=34 if name=='sterling' else 64
                    limit=(old-60-allowance)/span
                    width=min(width,max(.67,limit*(1+.21*(d/100-1))/1.105))
                else:
                    width=min(width,max(1,(old-36)/span))
            return width,(old-width*old)/2
        return new/old,0.

    def anchor(self, name, x, y, w, d):
        scale,shift = self.transform(name,w,d)
        return round((x-self.slant*y)*scale+self.slant*y+shift)

    def set_layout(self, font, w, d):
        for name,(width,lsb) in font["hmtx"].metrics.items():
            advance = self.punctuation_advance(name, w) if name in self.punctuation else self.advance(name, w, d)
            font["hmtx"][name] = (advance, lsb)
        # Prevent tagged anchors shared by several glyphs in memory from
        # being transformed twice.
        def transform_anchor(anchor, name):
            if anchor is None:
                return None
            result = copy.copy(anchor)
            result.XCoordinate = self.anchor(name,anchor.XCoordinate,anchor.YCoordinate,w,d)
            return result
        for lookup in font["GPOS"].table.LookupList.Lookup:
            for st in lookup.SubTable:
                if lookup.LookupType == 2:
                    pair_records = ([r for ps in st.PairSet for r in ps.PairValueRecord] if st.Format==1
                                    else [r for a in st.Class1Record for r in a.Class2Record])
                    for record in pair_records:
                        value = record.Value1
                        if value and hasattr(value,"XAdvance"):
                            record.Value1 = copy.copy(value)
                            record.Value1.XAdvance = round(value.XAdvance*(.35+.65*d/100))
                elif lookup.LookupType in (4,6):
                    if lookup.LookupType==4:
                        marks,mark_names = st.MarkArray.MarkRecord,st.MarkCoverage.glyphs
                        bases,base_names,attr = st.BaseArray.BaseRecord,st.BaseCoverage.glyphs,"BaseAnchor"
                    else:
                        marks,mark_names = st.Mark1Array.MarkRecord,st.Mark1Coverage.glyphs
                        bases,base_names,attr = st.Mark2Array.Mark2Record,st.Mark2Coverage.glyphs,"Mark2Anchor"
                    # Each mark keeps its own attachment as the pen changes.
                    # In particular a wide circumflex and a narrow acute need
                    # different corrections over the same ascender.
                    old_classes=[mark.Class for mark in marks]
                    old_marks=[mark.MarkAnchor for mark in marks]
                    st.ClassCount=len(marks)
                    for i,(record,mark) in enumerate(zip(marks,mark_names)):
                        record.Class=i
                        record.MarkAnchor=transform_anchor(record.MarkAnchor,mark)
                    for br,n in zip(bases,base_names):
                        original=getattr(br,attr)
                        adjusted=[]
                        for i,mark in enumerate(mark_names):
                            a=original[old_classes[i]]
                            value=transform_anchor(a,n)
                            if value and (w,d)!=(400,100):
                                mx,my=old_marks[i].XCoordinate,old_marks[i].YCoordinate
                                x,y=a.XCoordinate-mx,a.YCoordinate-my
                                nmx,nmy=marks[i].MarkAnchor.XCoordinate,marks[i].MarkAnchor.YCoordinate
                                origin=(value.XCoordinate-nmx,value.YCoordinate-nmy)
                                if mark in ATTACHED:
                                    origin=self.attachments.offset(n,mark,x,y,w,d)
                                elif (n,mark,x,y) in self.attachments.detached:
                                    # Composite origins use the base's width
                                    # transform. A separate accent has a
                                    # different width transform of its own.
                                    origin=(self.anchor(n,x,y,w,d)-self.anchor(mark,0,0,w,d),y)
                                    origin=self.attachments.separate(n,mark,origin,(w,d))
                                elif lookup.LookupType==6:
                                    origin=self.attachments.separate(n,mark,origin,(w,d))
                                value.XCoordinate,value.YCoordinate=origin[0]+nmx,origin[1]+nmy
                            adjusted.append(value)
                        setattr(br,attr,adjusted)

    def layout_font(self):
        ds = DesignSpaceDocument()
        for tag,(low,default,high) in AXES.items():
            ds.addAxis(AxisDescriptor(tag=tag,name=AXIS_NAMES[tag],minimum=low,default=default,maximum=high))
        for w,d in CELLS:
            # Static copies carry identical GSUB/GPOS lookup topology. varLib
            # builds GDEF's variation store, including mark/mkmk and kern, from these.
            f = copy.deepcopy(self.regular)
            self.set_layout(f,w,d)
            ds.addSource(SourceDescriptor(name=f"{w}-{d}",font=f,
                         location={"Weight":w,"Width":d,"Corner radius":0}))
        for i,name in enumerate(WEIGHTS,1):
            ds.addInstance(InstanceDescriptor(name=name,styleName=name,location={"Weight":100*i,"Width":100,"Corner radius":0}))
        font,_,_ = merge_layout(ds,exclude=["gvar","STAT"],optimize=True)
        builder = FontBuilder(font=font)
        builder.setupStat([{"tag":k,"name":v} for k,v in AXIS_NAMES.items()])
        return font

    def design_glyph(self,name):
        if name in self.punctuation:
            return self.design_punctuation(name)
        return self.native_glyph(name)

    def design_punctuation(self, name):
        # At normal width and zero radius only the pure weight tuples are active.
        glyph, variations = self.upright.native_glyph(name)
        by_peak = {v.axes["wght"][1]: v for v in variations if set(v.axes) == {"wght"}}
        masters = {}
        for weight, peak in ((100, -1), (400, 0), (900, 1)):
            points = np.asarray(glyph.coordinates, dtype=int)
            if peak in by_peak:
                points = points + np.asarray(by_peak[peak].coordinates[:-4])
            ends, flags = glyph.endPtsOfContours, glyph.flags
            if name != "period" and name.removesuffix(".case") in DOT_ROLES:
                regular = self.upright.regular["glyf"][name]
                points, ends, flags = round_dots(name, points, ends, flags, regular, weight)
            advance = self.punctuation_advance(name, weight)
            extra = advance - self.upright.advance(name, weight, 100)
            points = points + [round(extra / 2), 0]
            masters[weight] = np.vstack([points, [[0, 0], [advance, 0], [0, 0], [0, 0]]])
        points = [masters[w] for w, d in CELLS for _ in (0, 100)]
        return simple(masters[400][:-4], ends, flags), var_tuples(points)

    def native_glyph(self,name):
        rg = self.regular["glyf"][name]
        coords = []
        if name == "period":
            for w, d in CELLS:
                points = period_coords(rg, self.slant, w, *self.transform(name, w, d))
                advance = self.advance(name, w, d)
                master = np.vstack([points, [[0, 0], [advance, 0], [0, 0], [0, 0]]])
                coords.extend([master, master])  # Roundness already has its full value at both ends.
            return simple(coords[0][:-4], [7], [0] * 8), var_tuples(coords)
        case = self.family=="AdmiraltySans" and (name in LETTERS and len(name)==1 or name in ("dotlessi","dotlessj"))
        cp = self.unicode.get(name,-1)
        grid = self.mono and 0x2500<=cp<=0x259f
        varying_grid = grid and cp<0x2580
        accent = accent_name(name) if rg.numberOfContours>0 else None
        cap = name in DIAGONALS and not self.serif and not self.mono
        cursive = (name in ("integral","uni2113") or (name=="a" and (self.slant or self.serif))
                   or (name=="g" and self.mono and not self.slant) or (self.mono and name in MONO_BOWLS)
                   or (name=="thorn" and not self.serif))
        inherited = (self.family=="AdmiraltySans-Italic" and
                     ((len(name)==1 and name in LETTERS and name not in "afi") or name=="dotlessj"))
        serif_t = self.serif and name in ("t", "tbar")
        serif_letter = self.serif and name in SERIF_LETTERS
        constructed = (name in sign_masters.SIGNS or name in sign_masters.NUMERALS
                       or member_masters.handles(self, name))
        reviewed_polygon = (name=="X" and not self.serif or self.mono and name in ("K","W","Y"))
        registered_cut = (not self.serif and (name in ("seven","seven.tnum")
                          or not self.mono and name in ("N","k")))
        if reviewed_polygon or registered_cut:
            constructed = True
        if constructed:
            case = False
        special = constructed or name in ("ae","oe","uni20BA") or accent or cap or cursive or inherited or serif_t or serif_letter or name in SLASHED_ZEROS
        # Purpose-drawn studies and modular technical glyphs have their own
        # variation recipes. The remaining outlines share a continuous curve fit.
        curved = rg.numberOfContours > 0 and any(not (f & 1) for f in rg.flags)
        polygon = rg.numberOfContours > 0 and len(rg.coordinates) >= 6
        touching_foot = self.family == 'AdmiraltyMono' and name == 'IJ'
        # Coding ligatures are complementary slices on adjacent Mono cells.
        # Keep their existing shared cell-edge construction.
        fragment = self.mono and '.lig_' in name
        special = special or fragment
        fitted = (curved or polygon) and not (grid or fragment or touching_foot or name in PUNCT or special or case)
        if fitted:
            special, case = True, False
        if special:
            if name=='multiply':
                drawer=multiply_tracks
            elif registered_cut:
                drawer=reviewed_strokes.polygon_tracks
            elif reviewed_polygon:
                drawer = capital_tracks if name=="Y" else reviewed_capitals.tracks
            elif fragment:
                drawer=operator_tracks
            elif name=="lslash" and not self.serif:
                drawer=member_masters.slashed_l_tracks
            elif name=="uni20AD" and not self.serif:
                drawer=reviewed_capitals.kip_tracks
            elif name=="uni20AB" or name in ("ij","IJ") and not self.mono:
                drawer=member_masters.assembled_tracks
            elif constructed:
                drawer=sign_masters.master_tracks
            elif name == "uni20BA":
                drawer=junction_drawings.lira_tracks
            elif name in ("ae","oe"):
                drawer=junction_drawings.ae_tracks
            elif fitted:
                drawer=optical_tracks
            elif accent:
                drawer=accent_tracks
            elif cap:
                drawer=capital_tracks
            elif serif_t:
                drawer=serif_t_tracks
            elif serif_letter:
                drawer=letter_tracks
            elif inherited:
                drawer=inherited_italic_tracks
            else:
                drawer=slashed_zero_tracks if name in SLASHED_ZEROS else cursive_tracks
            designed_points, ends = drawer(self,name,CELLS)
            if (name in THIN_FIGURES or name in junction_drawings.NAMES
                    and not (self.serif and name in ('Germandbls','germandbls'))) and not (fitted or constructed):
                designed_points, ends = replace_special_thin(self, name, CELLS, designed_points, ends)
            if self.mono and name in mono_heavy.NAMES and not constructed:
                designed_points, ends = replace_masters(self, name, CELLS, designed_points, ends,
                                                        900, mono_heavy.draw, 14)
            if (self.mono or self.serif) and name in ('X','x') and not reviewed_polygon:
                designed_points = cross_tracks(self, name, CELLS, designed_points)
            if (self.mono and name=="b") or (self.family=="AdmiraltySans-Italic" and name=="l"):
                designed_points, ends = reviewed_strokes.register_ascender(designed_points, ends, CELLS, self.slant)
            flags = [1,0]*(len(designed_points[0])//2)
        # The thin shoulder/serif junctions of r and the b bowl contain
        # tight reversals between ordinary sample sites. Resolve the mesh
        # there at a fraction of a hairline, including inside pi's foot.
        spacing=4 if self.serif and not self.slant and name in ('r','b','thorn') else 7 if self.serif and name in ('pi','yen') else 17
        optical = OpticalMaster(rg,self.slant,spacing) if rg.numberOfContours>0 and not (case or grid or special) else None
        if case:
            letter = {"dotlessi":"i","dotlessj":"j"}.get(name,name)
            source = self.study[400,100,0]["glyf"][letter]
            mask = np.arange(len(source.coordinates))
            ends,flags = source.endPtsOfContours,source.flags
            if name.startswith("dotless"):
                parts = np.split(mask,np.asarray(ends)[:-1]+1)
                mask = min(parts,key=lambda ids:min(source.coordinates[i][1] for i in ids))
                ends,flags = [len(mask)-1],np.asarray(flags)[mask]
        for w,d in CELLS:
            adv = self.advance(name,w,d)
            sx,dx = self.transform(name,w,d)
            if optical:
                shaped = (punctuation_coords(optical,name,w,d,sx,dx) if name in PUNCT
                          else optical.fit(w,d,sx,dx,self.serif))
            for r in (0,100):
                if case:
                    g = self.study[w,d,r]["glyf"][letter]
                    xy = np.rint(np.asarray(g.coordinates)[mask]/4).astype(int)
                elif special:
                    xy = ints(designed_points[len(coords)])
                elif grid:
                    xy = np.asarray(rg.coordinates, dtype=float)
                    if varying_grid:
                        bold = np.asarray(self.bold["glyf"][name].coordinates,dtype=float)
                        # The terminal cell remains exactly 600 by 1300 at
                        # all widths, including dashed rules, corners and tees.
                        factor = {100:-1.65,400:0,900:1.36}[w]
                        xy = xy + factor*(bold-xy)
                    xy = np.rint(xy).astype(int)
                    ends,flags = rg.endPtsOfContours,rg.flags
                elif optical:
                    radius = {100:9,400:30,900:49}[w] if r else 0.
                    points,ends = optical.points(shaped,radius)
                    xy = ints(points)
                    flags = np.concatenate([ring.flags for ring in optical.rings])
                    if self.family=='AdmiraltyMono' and name=='IJ' and (w,d)!=(400,100):
                        # IJ is drawn as two letters in one cell. In 0.300
                        # their very tips overlap by four units at the foot.
                        left,right=xy[:ends[0]+1,0],xy[ends[0]+1:,0]
                        missing=max(0,30+left.max()-right.min())
                        left-=missing//2
                        right+=missing-missing//2
                elif rg.isComposite():
                    xy=self.attachments.position_marks(name,rg,(w,d))
                else:
                    xy = np.empty((0,2),dtype=int)
                if rg.numberOfContours>0 and name in self.attachments.bases:
                    self.attachments.record(name,(w,d),simple(xy,ends,flags),r)
                if not coords:
                    result = simple(xy,ends,flags) if rg.numberOfContours>0 else copy.deepcopy(rg)
                coords.append(np.vstack([xy,[[0,0],[adv,0],[0,0],[0,0]]]))
        return result,var_tuples(coords)

    def build(self):
        glyphs,variations = {},{}
        order=self.regular.getGlyphOrder()
        for n in sorted(order,key=lambda n:self.regular["glyf"][n].isComposite()):
            try:
                glyphs[n],variations[n] = self.design_glyph(n)
            except Exception as exc:
                raise RuntimeError(f"{self.family} {n}") from exc
        font = self.layout_font()
        font["glyf"].glyphs = glyphs
        # getGlyphSet and FreeType use the phantom origin xMin - LSB. Reset
        # it after de Casteljau splits have tightened control-point bounds.
        for n,g in glyphs.items():
            g.recalcBounds(font["glyf"])
            font["hmtx"][n] = (self.advance0[n],getattr(g,"xMin",0))
        builder = FontBuilder(font=font)
        builder.setupGvar(variations)
        refine_marks(font)
        apply_punctuation_spacing(font)
        title = self.family.replace("Admiralty","Admiralty ").replace("-Italic","")
        italic = "Italic" in self.family
        family_name = title+" Fullrange"
        style = "Italic" if italic else "Regular"
        postscript_name = self.family+"-Fullrange"
        unique_id = fullrange_unique_id(font,postscript_name)
        names = font["name"]
        for rec in list(names.names):
            value = {1:family_name,2:style,3:unique_id,4:family_name+" "+style,
                     6:postscript_name,16:family_name,17:style}.get(rec.nameID)
            if value:
                names.setName(value,rec.nameID,rec.platformID,rec.platEncID,rec.langID)
        font.recalcTimestamp=False
        font["head"].modified = self.regular["head"].modified
        OUTPUT.mkdir(exist_ok=True)
        dest = OUTPUT / (self.family+"[wght,wdth,RADI].ttf")
        font.save(dest)
        font.flavor = "woff2"
        font.save(dest.with_suffix(".woff2"))
        print(self.family,len(glyphs),"glyphs",dest.stat().st_size,"bytes",flush=True)


if __name__=="__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("families",nargs="*",metavar="FAMILY")
    args = parser.parse_args()
    if any(f not in TEXT for f in args.families):
        parser.error("Choose a family from " + ", ".join(TEXT))
    study = study_instances()
    for family in args.families or TEXT:
        TextDesign(family,study).build()
