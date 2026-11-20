"""Build a portable optical review queue from a reproducible scan of packaged fonts."""
import argparse
import base64
from collections import defaultdict
import hashlib
from io import BytesIO
import json
from pathlib import Path

from fontTools import subset
from fontTools.ttLib import TTFont
from fontTools.ttLib.tables._c_m_a_p import CmapSubtable
import uharfbuzz as hb

from build_text_family import OUTPUT

HERE = Path(__file__).parent
FLAT = {'flat-head','flat-foot','stem-head','stem-foot','leg-foot','arm-end'}
# Representatives visually inspected in the November review. Other hits stay
# searchable with the same controls. This order never implies sign-off.
FIRST = [('N','flat'),('AE','counter'),('bell','icon-fragment'),('K','corner'),
         ('new_file','icon-hole'),('ij','dot'),('uni20A6','counter'),('k','flat'),
         ('k','arm-junction'),('project','icon-hole'),('seven','flat'),('l','flat'),
         ('lslash','flat'),('timer','icon-fragment'),('b','flat'),('trash','icon-hole')]


def proof_font(path, gids):
    with TTFont(path) as tt:
        order=tt.getGlyphOrder()
        cmap={0xf0000+i:order[i] for i in gids}
        table=CmapSubtable.newSubtable(12)
        table.platformID,table.platEncID,table.language=3,10,0
        table.cmap=cmap
        tt["cmap"].tables=[table]
        # Render GIDs directly, including inactive alternates, and keep gvar.
        options=subset.Options()
        options.layout_features=[]
        sub=subset.Subsetter(options=options)
        sub.populate(unicodes=cmap)
        sub.subset(tt)
        tt.flavor='woff2'
        sink=BytesIO()
        tt.save(sink)
        return base64.b64encode(sink.getvalue()).decode()


def shared_bounds(font, gid, row):
    boxes=[]
    for w in (row['wght'],400):
        font.set_variations(dict(wght=w,wdth=row['wdth'],RADI=row['RADI']))
        ink=font.get_glyph_extents(gid)
        if ink and ink.width and ink.height:
            x=720-font.get_glyph_h_advance(gid)/2+ink.x_bearing
            y=1030-ink.y_bearing
            boxes.append((x,y,x+ink.width,y-ink.height))
    if not boxes:
        raise ValueError((row,'no ink in candidate or reference'))
    x,y=min(b[0] for b in boxes),min(b[1] for b in boxes)
    right,bottom=max(b[2] for b in boxes),max(b[3] for b in boxes)
    pad=max(36,.09*max(right-x,bottom-y))
    return [round(x-pad),round(y-pad),round(right-x+2*pad),round(bottom-y+2*pad)]


def build(scan_path, directory, output):
    raw=scan_path.read_bytes()
    report=json.loads(raw)
    mono_width = report['schema'] == 'admiralty-mono-width-scan/1'
    groups=defaultdict(list)
    faces={}
    css=[]
    for i,(family,info) in enumerate(report['fonts'].items()):
        path=directory/info['file']
        binary=path.read_bytes()
        if hashlib.sha256(binary).hexdigest()!=info['sha256']:
            raise ValueError(f"{family} changed since the optical scan")
        faces[family]=dict(info,css=f'Proof{i}')
        rows=[r for r in report['rows'] if r['family']==family]
        if not rows:
            continue
        font=hb.Font(hb.Face(binary))
        gids=set()
        with TTFont(path) as tt:
            codes=defaultdict(list)
            for cp,n in tt.getBestCmap().items():
                codes[n].append(f'U+{cp:04X}')
            for r in rows:
                gid=r.get('renderedGlyphID',r['glyphID'])
                gids.add(gid)
                # Lock the scale across all weights and references for a spacing review.
                bound=[306, 205, 858, 880] if mono_width else shared_bounds(font,gid,r)
                if mono_width and r['glyph'] == 'perthousand':
                    faces[family]['percentGid'] = tt.getGlyphID('percent')
                    gids.add(faces[family]['percentGid'])
                by_group=defaultdict(list)
                for m in r['findings']:
                    rule='flat' if m['rule'] in FLAT else m['rule']
                    component=m.get('component',r['base'])
                    if component.endswith('.tnum'):
                        component=component.removesuffix('.tnum')
                    by_group[component,rule].append(m)
                for group,points in by_group.items():
                    groups[group].append(dict(f=family,g=r['glyph'],gid=r['glyphID'],draw=gid,
                        u=codes[r['glyph']] or ([f"U+{r['codepoint']:04X}"] if 'codepoint' in r else []),
                        w=r['wght'],d=r['wdth'],r=r['RADI'],box=bound,p=points))
        blob=proof_font(path,gids)
        css.append("@font-face{font-family:Proof"+str(i)+";src:url(data:font/woff2;base64,"+
                   blob+");font-weight:100 900;font-stretch:65% 150%;font-display:block}")
    result=[]
    for component,rule in sorted(groups, key=lambda k:(k[1]=='cell-width-context', FIRST.index(k) if k in FIRST else len(FIRST),
                    k[1]=='corner',-len(groups[k]),k)):
        cases=groups[component,rule]
        cases.sort(key=lambda r:(not any('sourceMark' in p for p in r['p']), r['g']!=component,-max(p['score'] for p in r['p']),
                                 r['f'],r['g'],r['w'],r['d'],r['r']))
        result.append(dict(id=f'{component}|{rule}',glyph=component,rule=rule,
                           first=mono_width or (component,rule) in FIRST,cases=cases))
    dataset=dict(id=hashlib.sha256(raw).hexdigest(),schema=report['schema'],fonts=faces,
                 grid=report['grid'],frame=report['annotationFrame'],groups=result,cellCount=len(report['rows']))
    if mono_width:
        marked = [row for row in report['rows'] if 'sourceMark' in row['findings'][0]]
        hits = [row for row in report['rows'] if row['findings'][0]['rule'] == 'cell-width-dip']
        dataset['widthScan'] = dict(minDip=report['minDip'], totalMarks=len(marked), hits=len(hits),
                                    sourceExport=report['sourceExport'], sourceSha256=report['sourceSha256'])
    source=(HERE/'candidate_review.html.in').read_text()
    source=source.replace('/* FONTS */','\n'.join(css)).replace('/* DATA */',json.dumps(
            dataset,ensure_ascii=False,separators=(',',':')).replace('<','\\u003c'))
    temp=output.with_suffix('.tmp')
    temp.write_text(source)
    temp.replace(output)
    print(f"{len(result)} groups, {sum(g['first'] for g in result)} priority, {dataset['cellCount']} candidate cells, {output.stat().st_size:,} bytes")


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('scan',type=Path)
    p.add_argument('--fonts',type=Path,default=OUTPUT)
    p.add_argument('--out',type=Path,required=True)
    a=p.parse_args()
    build(a.scan,a.fonts,a.out)
