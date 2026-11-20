"""Exercise native layout at both design masters and interpolated axis positions."""
import collections
import itertools
from io import BytesIO

import uharfbuzz as hb
from fontTools.ttLib import TTFont
from fontTools.ttLib.tables._c_m_a_p import CmapSubtable
from fontTools.pens.recordingPen import RecordingPen

from build_text_family import AXES, OUTPUT, RELEASE, TEXT


def shape(font,s,features=None):
    b=hb.Buffer()
    b.add_str(s)
    b.guess_segment_properties()
    hb.shape(font,b,features)
    return [(x.codepoint,p.x_advance,p.x_offset,p.y_offset) for x,p in zip(b.glyph_infos,b.glyph_positions)]


def check_mark_positions(path):
    # A private alias prevents NFC from composing the input before GPOS
    # runs. The real combining mark still has its normal Unicode category.
    font=TTFont(path)
    cmap=font.getBestCmap()
    unicode_for={n:cp for cp,n in cmap.items()}
    extra=CmapSubtable.newSubtable(12)
    extra.platformID,extra.platEncID,extra.language=3,10,0
    extra.cmap={**cmap,**{0xf0000+i:g for i,g in enumerate(font.getGlyphOrder())}}
    font['cmap'].tables=[t for t in font['cmap'].tables if (t.platformID,t.platEncID)!=(3,10)]+[extra]
    data=BytesIO()
    font.save(data)
    native=hb.Font(hb.Face(data.getvalue()))
    for w,d,r in [(400,100,0),(100,65,0),(175,113,27),(900,150,100)]:
        loc=dict(wght=w,wdth=d,RADI=r)
        native.set_variations(loc)
        glyphs=font.getGlyphSet(location=loc)
        for name in ('Aogonek','Uhorn','tcedilla','eacute'):
            pen=RecordingPen()
            glyphs[name].draw(pen)
            (_,base),(_,mark)=pen.value
            base,_=base
            mark,transform=mark
            buffer=hb.Buffer()
            buffer.add_codepoints([0xf0000+font.getGlyphID(base),unicode_for[mark]])
            buffer.direction,buffer.script='ltr','Latn'
            hb.shape(native,buffer)
            assert [g.codepoint for g in buffer.glyph_infos]==[font.getGlyphID(base),font.getGlyphID(mark)]
            a,b=buffer.glyph_positions
            error=max(abs(a.x_advance+b.x_offset-transform[4]),abs(b.y_offset-transform[5]))
            assert error<1.6,(path.name,name,loc,error)


def main():
    new={}
    for family in TEXT:
        path=OUTPUT/(family+"[wght,wdth,RADI].ttf")
        native=TTFont(path)
        web=TTFont(path.with_suffix(".woff2"))
        old=TTFont(RELEASE.with_name(family+"[wght].ttf"))
        assert native.getGlyphOrder()==old.getGlyphOrder()
        assert old.getBestCmap()==native.getBestCmap()==web.getBestCmap()
        assert {a.axisTag:(a.minValue,a.defaultValue,a.maxValue) for a in native["fvar"].axes}==AXES
        for tag in ("GSUB","GPOS","GDEF","HVAR","gvar","fvar"):
            assert native.getTableData(tag)==web.getTableData(tag),(family,tag)
        assert {r.FeatureTag for r in native["GSUB"].table.FeatureList.FeatureRecord}=={r.FeatureTag for r in old["GSUB"].table.FeatureList.FeatureRecord}
        new[family]=native,hb.Font(hb.Face(path.read_bytes()))
        check_mark_positions(path)
    words=["The Admiralty office — AVATAR","Ångström Việt Nam ế ễ ử Ắ ậ",
           "o\u031b\u0302\u0301 A\u0328\u0308\u0301 ą e\u0328",
           "0123456789 100/150%", "ÁV To. Wî Fl", "minimum signals éèç"]
    checks=0
    for w,d,r in itertools.product((100,250,400,650,900),(65,82.5,100,125,150),(0,47,100)):
        loc=dict(wght=w,wdth=d,RADI=r)
        for _,font in new.values():
            font.set_variations(loc)
        for suffix in ("","-Italic"):
            st,sans=new["AdmiraltySans"+suffix]
            _,serif=new["AdmiraltySerif"+suffix]
            mt,mono=new["AdmiraltyMono"+suffix]
            for i,n in enumerate(st.getGlyphOrder()):
                assert sans.get_glyph_h_advance(i)==serif.get_glyph_h_advance(i),(n,loc)
            for i,n in enumerate(mt.getGlyphOrder()):
                assert mono.get_glyph_h_advance(i)==mt["hmtx"][n][0],(n,loc)
            for s in words:
                for f in ({},{"kern":False},{"tnum":True,"zero":True}):
                    one,two=shape(sans,s,f),shape(serif,s,f)
                    assert [v[1] for v in one]==[v[1] for v in two],(s,f,loc)
                    assert all(v[0] for v in one+two),(s,loc)
                    checks+=1
            assert sum(v[1] for v in shape(mono,"─"*80))==48000
    print("Six complete text fonts, both formats, 75 axis positions.")
    print(f"{checks} duplex shaping comparisons; all glyph advances checked at each position.")

if __name__=="__main__":
    main()
