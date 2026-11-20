"""Screen shaped public icons for disconnected ink and disappearing counters at two sizes."""
from pathlib import Path
import ctypes
import hashlib

import freetype as ft
import numpy as np
from scipy.ndimage import label
from fontTools.ttLib import TTFont
import uharfbuzz as hb

from audit_symbol_family import BY_NAME, shape


def features(face, gid, ppem):
    face.load_glyph(gid, ft.FT_LOAD_RENDER | ft.FT_LOAD_NO_HINTING | ft.FT_LOAD_NO_BITMAP)
    slot=face.glyph
    b=slot.bitmap
    if not b.width or not b.rows:
        return [], []
    raw=np.frombuffer(ctypes.string_at(b._FT_Bitmap.buffer,b.pitch*b.rows),np.uint8)
    ink=np.pad(raw.reshape(b.rows,b.pitch)[:,:b.width]>=128,1)
    def regions(mask, holes):
        ids, count=label(mask,structure=np.ones((3,3),int))
        sizes=np.bincount(ids.ravel(),minlength=count+1)
        exclude=ids[0,0] if holes else 0
        result=[]
        for i in np.flatnonzero(sizes>=max(4,round(6*(ppem/144)**2))):
            if i==0 or i==exclude:
                continue
            ys,xs=np.nonzero(ids==i)
            x=(xs.mean()-.5+slot.bitmap_left)*1000/ppem
            y=(slot.bitmap_top-ys.mean()+.5)*1000/ppem
            result.append((complex(x,y),sizes[i]*(1000/ppem)**2))
        return result
    return regions(ink,False), regions(~ink,True)


def compare(reference, current):
    from scan_family_candidates import mark
    findings=[]
    for element,(old,new) in enumerate(zip(reference,current)):
        # Extra disconnected ink, or a white hole present in Regular that
        # has closed. Compare the same active variable drawing only.
        if (element==0 and len(new)<=len(old)) or (element==1 and len(new)>=len(old)):
            continue
        more,less=(new,old) if element==0 else (old,new)
        # Match surviving regions first; the unmatched center is the marker.
        pool=set(range(len(more)))
        for z,_ in sorted(less,key=lambda v:-v[1]):
            pool.remove(min(pool,key=lambda j:abs(z-more[j][0])))
        for idx in pool:
            z,area=more[idx]
            if area < 360 or (element==0 and area>20000):
                continue
            rule='icon-fragment' if element==0 else 'icon-hole'
            findings.append(mark(z,840,rule,area,area=area,regularCount=len(old),instanceCount=len(new)))
    return findings


def scan_icons(directory, widths, radii, weights):
    family='AdmiraltySymbols'
    path=directory/(family+'[wght,wdth,RADI].ttf')
    binary=path.read_bytes()
    font=hb.Font(hb.Face(binary))
    faces=[ft.Face(str(path)) for _ in range(2)]
    sizes=(144,216)
    for f,size in zip(faces,sizes):
        f.set_pixel_sizes(0,size)
    directions=[(name,spec.codepoint,direction) for name,spec in BY_NAME.items()
                for direction in (('ltr','rtl') if spec.rtl_mirror else ('ltr',))]
    with TTFont(path) as tt:
        ids={n:i for i,n in enumerate(tt.getGlyphOrder())}
    rows=[]
    for d in widths:
        for radius in radii:
            regular={}
            cache={}
            for w in (400, *(v for v in weights if v!=400)):
                font.set_variations(dict(wght=w,wdth=d,RADI=radius))
                for f in faces:
                    f.set_var_design_coords((w,d,radius))
                for name,cp,direction in directions:
                    gid,_=shape(font,cp,direction)
                    current=features(faces[0],gid,sizes[0])
                    key=name,direction
                    if w==400:
                        regular[key]=(gid,current)
                        continue
                    ref_gid,ref=regular[key]
                    if gid!=ref_gid:
                        continue
                    coarse=compare(ref,current)
                    if not coarse:
                        continue
                    if gid not in cache:
                        faces[1].set_var_design_coords((400,d,radius))
                        cache[gid]=features(faces[1],gid,sizes[1])
                        faces[1].set_var_design_coords((w,d,radius))
                    fine=compare(cache[gid],features(faces[1],gid,sizes[1]))
                    hits=[p for p in fine if any(q['rule']==p['rule'] and
                          np.hypot(q['x']-p['x'],q['y']-p['y'])<.04 for q in coarse)]
                    if hits:
                        stem=name.replace('-','_')
                        glyph=stem+('.rtl' if direction=='rtl' else '')
                        rows.append(dict(family=family,glyph=glyph,base=stem,glyphID=ids[glyph],renderedGlyphID=gid,codepoint=cp,direction=direction,
                                         wght=w,wdth=d,RADI=radius,findings=hits))
    info=dict(file=path.name,sha256=hashlib.sha256(binary).hexdigest(), glyphs=len(BY_NAME),
              directionalForms=len(directions))
    return family,info,rows
