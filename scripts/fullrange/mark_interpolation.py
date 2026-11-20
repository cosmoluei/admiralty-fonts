"""Set accent clearance and attachment using the interpolated ink on both axes."""
import copy
import functools
import itertools
from io import BytesIO

import numpy as np
import pathops
import uharfbuzz as hb
from fontTools.ttLib.tables.TupleVariation import TupleVariation
from fontTools.varLib.builder import buildVarDevTable
from fontTools.varLib.models import VariationModel, normalizeLocation, supportScalar
from fontTools.varLib.varStore import OnlineVarStoreBuilder, VarStoreInstancer

from attachments import ATTACHED, is_mark
from build_axis_study import AXES

WEIGHTS=sorted([*range(100,901,100),385,415])
WIDTHS=(65,82.5,96,100,104,125,150)
CELLS=[(400,100,0)]+[p for p in itertools.product(WEIGHTS,WIDTHS,(0,50,100)) if p!=(400,100,0)]
LOCATIONS=[normalizeLocation(dict(zip(AXES,p)),AXES) for p in CELLS]
MODEL=VariationModel(LOCATIONS,axisOrder=list(AXES))


def signature(path):
    rings=[c for c in path.contours if c.area>4]
    return len(rings),sum(c.clockwise for c in rings)


def adjust_contact(base,mark,child):
    """Find the closest bonded placement or a gap along the proper accent direction."""
    attached=child in ATTACHED
    a,b,c,d=base.bounds
    u,v,w,z=mark.bounds
    if not attached and (a>w+12 or b>z+12 or c<u-12 or d<v-12):
        return (0,0)
    nb,hb=signature(base)
    nm,hm=signature(mark)
    expected=(nb+nm-int(attached),hb+hm)
    def connected(x,y):
        placed=mark.transform(1,0,0,1,x,y)
        union=pathops.op(base,placed,pathops.PathOp.UNION)
        if signature(union)!=expected:
            return False
        return not attached or base.area+mark.area-union.area>=min(230,max(65,.018*mark.area))
    def accepts(x,y):
        # GVAR tuple deltas and the component offsets can each round at a
        # different stage. Keep a margin on either side of the contact.
        if not attached:
            if child.endswith('.alt'):
                return connected(x,y) and connected(x-12,y)
            amount=12 if child.startswith(('commaaccent','dotbelow')) else -12
            return connected(x,y) and connected(x,y+amount)
        return all(connected(x+i,y+j) for i,j in [(0,0),(-3,0),(3,0),(0,-3),(0,3)])
    if accepts(0,0):
        return (0,0)
    if attached:
        steps=range(2,326,3)
        angles=np.arange(24)*np.pi/12
        # A hook is allowed to travel along the sloping side of the stem.
        # Search the entire small neighbourhood before increasing travel.
        directions=np.column_stack([np.cos(angles),np.sin(angles)])
    else:
        downward=child.startswith(('commaaccent','dotbelow'))
        directions=[(1,0)] if child.endswith('.alt') else [(0,-1 if downward else 1)]
        steps=range(2,200,3)
    for distance in steps:
        for i,j in directions:
            x,y=round(i*distance),round(j*distance)
            if accepts(x,y):
                if not attached:
                    x+=round(i*8)
                    y+=round(j*8)
                return (x,y)
    return (0,0)


def layout_corrections(font,corrections):
    if not corrections:
        return
    gdef=font['GDEF'].table.VarStore
    store=OnlineVarStoreBuilder(list(AXES))
    store.setModel(MODEL)
    outer=len(gdef.VarData)
    instancers=[VarStoreInstancer(gdef,font['fvar'].axes,loc) for loc in LOCATIONS]
    for lookup in font['GPOS'].table.LookupList.Lookup:
        if lookup.LookupType!=4:
            continue
        for st in lookup.SubTable:
            for name,br in zip(st.BaseCoverage.glyphs,st.BaseArray.BaseRecord):
                for mark,mr in zip(st.MarkCoverage.glyphs,st.MarkArray.MarkRecord):
                    anchor=br.BaseAnchor[mr.Class]
                    if not anchor:
                        continue
                    key=(name,mark,anchor.XCoordinate-mr.MarkAnchor.XCoordinate,
                         anchor.YCoordinate-mr.MarkAnchor.YCoordinate)
                    shifts=corrections.get(key)
                    if shifts is None:
                        continue
                    target=br.BaseAnchor[mr.Class]=copy.copy(anchor)
                    target.Format=3
                    for axis,delta in zip('XY',shifts.T):
                        device=axis+'DeviceTable'
                        existing=getattr(anchor,device,None)
                        setattr(target,device,existing)
                        if np.any(delta):
                            if existing:
                                assert existing.DeltaFormat==0x8000
                                idx=(existing.StartSize<<16)+existing.EndSize
                                delta=delta+[instance[idx] for instance in instancers]
                            default,new=store.storeMasters(delta)
                            assert default==0
                            setattr(target,device,buildVarDevTable(new+(outer<<16)))
    new=store.finish()
    start=len(gdef.VarRegionList.Region)
    for piece in new.VarData:
        piece.VarRegionIndex=[i+start for i in piece.VarRegionIndex]
        gdef.VarData.append(piece)
    gdef.VarRegionList.Region.extend(new.VarRegionList.Region)
    gdef.VarDataCount=len(gdef.VarData)
    gdef.VarRegionList.RegionCount=len(gdef.VarRegionList.Region)


def refine_marks(font):
    # Native coordinates include GVAR component offsets and integer rounding.
    # Refine only bases that have a hooked attachment, an ascender accent that
    # sits alongside the stem, or an acute on l. Other pairs use the master fit.
    glyphs=font['glyf']
    work={}
    for n in font.getGlyphOrder():
        g=glyphs[n]
        if not g.isComposite():
            continue
        base=g.components[0].glyphName
        indices=[i for i,c in enumerate(g.components[1:],1) if c.glyphName in ATTACHED or
                 c.glyphName.endswith('.alt') and is_mark(c.glyphName) or base=='l' and c.glyphName.startswith('acute')]
        if indices:
            work[n]=g.components,indices
    raw=BytesIO()
    font.save(raw)
    ink=hb.Font(hb.Face(raw.getvalue()))
    delta_by_name={}
    deltas={}
    for name,(components,indices) in work.items():
        values=np.asarray([(c.x,c.y) for c in components],dtype=float)
        all_positions=np.broadcast_to(values,(len(CELLS),*values.shape)).copy()
        for variation in font['gvar'].variations[name]:
            scalar=np.array([supportScalar(loc,variation.axes) for loc in LOCATIONS])
            all_positions+=scalar[:,None,None]*np.array(variation.coordinates[:-4])[None,:,:]
        delta_by_name[name]=np.round(all_positions).astype(int)
        deltas[name]=np.zeros_like(all_positions,dtype=int)
    for k,cell in enumerate(CELLS):
        if cell[:2]==(400,100):
            continue
        ink.set_variations(dict(zip(AXES,cell)))
        @functools.lru_cache(None)
        def shape(n):
            p=pathops.Path()
            ink.draw_glyph_with_pen(font.getGlyphID(n),p.getPen())
            p.simplify()
            return p
        cache={}
        for name,(components,indices) in work.items():
            base=components[0].glyphName
            for i in indices:
                c=components[i]
                x,y=delta_by_name[name][k,i]-delta_by_name[name][k,0]
                transform=tuple(sum((list(row) for row in getattr(c,'transform',((1,0),(0,1)))),[]))
                key=(base,c.glyphName,x,y,transform)
                if key not in cache:
                    placed=shape(c.glyphName).transform(*transform,x,y)
                    cache[key]=adjust_contact(shape(base),placed,c.glyphName)
                deltas[name][k,i]=cache[key]
    layout={}
    for name,shifts in deltas.items():
        if not np.any(shifts):
            continue
        components,indices=work[name]
        for i in indices:
            c=components[i]
            if not hasattr(c,'transform') and np.any(shifts[:,i]):
                layout.setdefault((components[0].glyphName,c.glyphName,c.x,c.y),shifts[:,i])
        masters=list(shifts.astype(float))
        for support,delta in zip(MODEL.supports[1:],MODEL.getDeltas(masters,round=np.rint)[1:]):
            if np.any(delta):
                font['gvar'].variations[name].append(TupleVariation(support,[tuple(v) for v in delta.astype(int).tolist()]+[(0,0)]*4))
    layout_corrections(font,layout)
