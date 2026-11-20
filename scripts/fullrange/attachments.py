"""Carry the actual contact point of an ogonek, cedilla or horn across changing outlines."""
import functools

import numpy as np
import pathops

from check_word_proof import Edges, section

ATTACHED = {"horncomb","ogonekcomb","cedillacomb"}


def is_mark(name):
    return 'comb' in name


def clearance(first,second,direction):
    """Smallest gap between facing outlines along the indicated direction."""
    a=first*direction.conjugate()
    b=second*direction.conjugate()
    y0=max(a.imag.min(),b.imag.min())
    y1=min(a.imag.max(),b.imag.max())
    if y1-y0<.02:
        return np.inf
    box_gap=b.real.min()-a.real.max()
    if box_gap>42:
        return box_gap
    ys=np.linspace(y0+.005,y1-.005,30)
    gaps=[]
    for y in ys:
        aa=section(a,y)
        bb=section(b,y)
        if len(aa) and len(bb):
            gaps.append(bb[0]-aa[-1])
    return min(gaps,default=np.inf)


def intervals(edges,y):
    hits=section(edges,y)
    return list(zip(hits[::2],hits[1::2]))


def indexed(spans, rank, frac):
    a,b=spans[max(-len(spans),min(len(spans)-1,rank))]
    return a+(b-a)*frac


class Attachments:
    def __init__(self, design):
        self.design=design
        self.ink={}
        self.paths={}
        self.bases=set()
        self.pairs=set()
        self.detached=set()
        reg=design.regular
        for n in reg.getGlyphOrder():
            g=reg["glyf"][n]
            if not g.isComposite():
                continue
            first=g.components[0].glyphName
            for c in g.components[1:]:
                if is_mark(c.glyphName):
                    self.bases.update((first,c.glyphName))
                    if c.glyphName not in ATTACHED:
                        self.detached.add((first,c.glyphName,c.x,c.y))
                if c.glyphName in ATTACHED:
                    self.bases.add(first)
                    self.pairs.add((first,c.glyphName,c.x,c.y))
        self.bases.update(ATTACHED)
        gs=reg.getGlyphSet()
        for n in self.bases:
            pen=Edges(gs,1)
            gs[n].draw(pen)
            self.ink[n,None]=np.array(pen.edges)

    def record(self,name,cell,glyph,radius=0):
        if name in self.bases and not glyph.isComposite():
            if not radius:
                pen=Edges(None,1)
                glyph.draw(pen,None)
                self.ink[name,cell]=np.array(pen.edges)
            path=pathops.Path()
            glyph.draw(path.getPen(),None)
            path.simplify()
            self.paths[name,cell,radius]=path

    @functools.lru_cache(None)
    def contact(self,base,mark,x,y):
        b=self.ink[base,None]
        m=self.ink[mark,None]
        lo=max(b.imag.min(),y+m.imag.min())
        hi=min(b.imag.max(),y+m.imag.max())
        if hi<=lo:
            return None
        best=None
        # Locate a slice through the original contact. Record which part of
        # the mark and which side of the base stroke are intended to meet.
        for yy in np.linspace(lo+.04,hi-.04,21):
            bs=intervals(b,yy)
            ms=intervals(m,yy-y)
            for i,(a,z) in enumerate(bs):
                for j,(ma,mz) in enumerate(ms):
                    low,high=max(a,ma+x),min(z,mz+x)
                    overlap=high-low
                    if overlap<=0 or (best and overlap<=best[0]):
                        continue
                    center=(high+low)/2
                    rank=i-len(bs) if i>=len(bs)/2 else i
                    best=(overlap,yy,rank,(center-a)/max(z-a,.01),j,(center-x-ma)/max(mz-ma,.01))
        return best

    @functools.lru_cache(None)
    def offset(self,base,mark,x,y,w,d):
        dx = self.design.anchor(base,x,y,w,d)-self.design.anchor(mark,0,0,w,d)
        if (w,d)==(400,100) or (base,mark,x,y) not in self.pairs:
            return dx,y
        cell=w,d
        if (base,cell) not in self.ink:
            return dx,y
        b,m=self.ink[base,cell],self.ink[mark,cell]
        if self.design.mono and base=='E' and mark=='ogonekcomb':
            # On a thin sloped baseline the very lowest scanline can catch
            # only the heel of E. Follow the arm near its right end and keep
            # the returning hook inside the neighbouring character's margin.
            by=b.imag.min()+min(14,max(7,(w/900)*14))
            my=m.imag.max()-5
            body,hook=intervals(b,by),intervals(m,my)
            if body and hook:
                end=b.real.max()-.16*np.ptp(b.real)
                lo,hi=body[-1]
                anchor=min(hi-2,max(lo+2,end))
                dx=min(anchor-indexed(hook,-1,.5),self.design.advance0[base]-8-m.real.max())
                return self.join(base,mark,cell,round(dx),round(by-my))
        if base=='A' and mark=='ogonekcomb':
            # The right foot is the intended contact. When a light serif
            # splits into two scanline intervals, the left foot must never
            # become the nearest substitute for the original node.
            by=b.imag.min()+8
            my=m.imag.max()-5
            foot,tip=intervals(b,by),intervals(m,my)
            if foot and tip:
                dx=round(indexed(foot,-1,.5)-indexed(tip,-1,.5))
                return self.join(base,mark,cell,dx,round(by-my))
        if self.design.serif and base=='U' and mark=='horncomb':
            # Nest the horn against the outer upright, below the cap serif.
            # A hook touching the stem and the serif at two different
            # heights encloses an unintended white pocket.
            by=b.imag.max()-51
            stem,hook=intervals(b,by),intervals(m,by-y)
            if stem and hook:
                dx=round(indexed(stem,-1,.67)-indexed(hook,0,.04))
                return self.join(base,mark,cell,dx,y)
        c=self.contact(base,mark,x,y)
        if c is None:
            return self.join(base,mark,cell,dx,y)
        _,yy,rank,bfrac,j,mfrac=c
        original=self.ink[mark,None]
        fy=(yy-y-original.imag.min())/max(np.ptp(original.imag),1)
        my=m.imag.min()+np.clip(fy,.005,.995)*np.ptp(m.imag)
        ms=intervals(m,my)
        if not ms:
            return self.join(base,mark,cell,dx,y)
        original_base=self.ink[base,None]
        rel=(yy-original_base.imag.min())/max(np.ptp(original_base.imag),1)
        yref=b.imag.min()+rel*np.ptp(b.imag)
        for by in [yref,yref+1,yref-1,yref+3,yref-3,yref+7,yref-7]:
            bs=intervals(b,by)
            if bs:
                dx,y=round(indexed(bs,rank,bfrac)-indexed(ms,j,mfrac)),round(by-my)
                break
        return self.join(base,mark,cell,dx,y)

    def join(self,base,mark,cell,x,y):
        drawings=[(self.paths[base,cell,r],self.paths[mark,cell,r]) for r in (0,100)
                  if (base,cell,r) in self.paths and (mark,cell,r) in self.paths]
        def topology(shape):
            rings=[c for c in shape.contours if abs(c.area)>4]
            return np.array([len(rings),sum(c.clockwise for c in rings)])
        goals=[topology(b)+topology(m)-[1,0] for b,m in drawings]
        directions=[(-1,0),(-1,-1),(0,-1),(-1,1),(0,1),(1,0)] if mark=='horncomb' else [
                    (0,1),(-1,1),(1,1),(-1,0),(1,0),(0,-1)]
        candidates=[(x,y)]+[(x+round(i*step),y+round(j*step)) for step in (2,4,7,11,16,23,32,44,60)
                             for i,j in directions]
        for px,py in candidates:
            for (b,m),goal in zip(drawings,goals):
                placed=m.transform(1,0,0,1,px,py)
                union=pathops.op(b,placed,pathops.PathOp.UNION)
                # A real overlap survives rounding and changes in radius.
                overlap=abs(b.area)+abs(m.area)-abs(union.area)
                if overlap<min(540,max(165,.024*abs(m.area))) or not np.array_equal(topology(union),goal):
                    break
            else:
                return px,py
        return x,y

    def separate(self,base,mark,origin,cell,transform=None,placed=()):
        if cell==(400,100) or (base,cell) not in self.ink or (mark,cell) not in self.ink:
            return origin
        mark_ink=self.ink[mark,cell]
        if transform:
            (a,b),(c,d)=transform
            mark_ink=(a*mark_ink.real+c*mark_ink.imag)+1j*(b*mark_ink.real+d*mark_ink.imag)
        pos=complex(*origin)
        if mark.startswith(('commaaccent','dotbelow')):
            axis=-1j
        elif mark.endswith('.alt'):
            axis=1+0j
        else:
            axis=1j
        for other,ink in [(base,self.ink[base,cell]),*placed]:
            vector=axis
            if is_mark(other):
                if other in ATTACHED or other.startswith(('commaaccent','dotbelow')) or axis==-1j:
                    continue
                if other.startswith('circumflex') and mark.startswith(('acute','grave','hookabove')):
                    vector=1+0j
            gap=clearance(ink,mark_ink+pos,vector)
            target=16 if vector==1 else 14
            if gap<target:
                pos+=vector*np.ceil(target-gap)
        return round(pos.real),round(pos.imag)

    def position_marks(self,name,glyph,cell):
        w,d=cell
        base=glyph.components[0].glyphName
        positions=[]
        placed=[]
        for i,comp in enumerate(glyph.components):
            child=comp.glyphName
            x=self.design.anchor(name,comp.x,comp.y,w,d)-self.design.anchor(child,0,0,w,d)
            origin=(x,comp.y)
            transform=getattr(comp,'transform',None)
            if i and child in ATTACHED:
                origin=self.offset(base,child,comp.x,comp.y,w,d)
            elif i and is_mark(child):
                origin=self.separate(base,child,origin,cell,transform,placed)
            positions.append(origin)
            if i and (child,cell) in self.ink:
                ink=self.ink[child,cell]
                if transform:
                    (a,b),(c,d)=transform
                    ink=(a*ink.real+c*ink.imag)+1j*(b*ink.real+d*ink.imag)
                placed.append((child,ink+complex(*origin)))
        return np.asarray(positions)
