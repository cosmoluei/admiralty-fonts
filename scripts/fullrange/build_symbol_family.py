"""Compile icon masters and shape-dependent rvrn/rtlm substitutions into one native VF."""
import argparse
import collections
import hashlib
import itertools
import os
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np
from scipy.optimize import linear_sum_assignment
from fontTools.fontBuilder import FontBuilder
from fontTools.feaLib.builder import addOpenTypeFeaturesFromString
from fontTools.ttLib import TTFont
from fontTools.ttLib.tables._g_l_y_f import Glyph, GlyphComponent
from fontTools.ttLib.tables.TupleVariation import TupleVariation
from fontTools.varLib.featureVars import addFeatureVariations
from fontTools.varLib.instancer import instantiateVariableFont
from fontTools.varLib.models import normalizeLocation,normalizeValue

from build_text_family import AXES, AXIS_NAMES, WEIGHTS, ROOT, OUTPUT, fullrange_unique_id, ints, simple
from compatible import OutlinePen, Profile, compatible_points
from symbol_masters import CATALOG, by_name, glyph_parts

VALUES=[(100,200,300,400,500,600,700,800,900),(65,82.5,100,125,150),(0,50,100)]
DEFAULT=(400,100,0)
CELLS=[DEFAULT]+[c for c in itertools.product(*VALUES) if c!=DEFAULT]
KEYS=list(AXES)
NORMAL=[normalizeLocation(dict(zip(KEYS,c)),AXES) for c in CELLS]
HERE=Path(__file__).resolve().parent
CACHE=ROOT/'build'/'fullrange-symbols'


def fingerprint():
    h=hashlib.sha256()
    for file in [HERE/'compatible.py',HERE/'symbol_masters.py',Path(__file__),*sorted(HERE.parent.glob('symbols*.py')),HERE.parent/'build_symbols.py']:
        h.update(file.read_bytes())
    return h.hexdigest()[:16]


def ring_layout(contours):
    centers=np.asarray([c.center for c in contours])
    lo,hi=min(z.real for z in centers),max(z.real for z in centers)
    bot,top=min(z.imag for z in centers),max(z.imag for z in centers)
    return (centers.real-lo)/max(hi-lo,60)+1j*(centers.imag-bot)/max(top-bot,60)


def order_rings(outer,inner):
    if len(outer)==1:return inner
    a,b=ring_layout(outer),ring_layout(inner)
    area_a,area_b=np.array([c.area for c in outer]),np.array([c.area for c in inner])
    loss=abs(a[:,None]-b)+.18*abs(np.log(abs(area_a[:,None]/area_b)))+50*(np.sign(area_a[:,None])!=np.sign(area_b))
    _,ids=linear_sum_assignment(loss)
    return [inner[i] for i in ids]


class ArcProfile:
    """Match open-sided ink contours in order, including around cut-out badges."""
    def __init__(self, reference, target):
        from compatible import Contour
        if reference.area*target.area<0:
            target=Contour(target.pieces[::-1,::-1])
        self.target=target
        size=192
        units=np.arange(size)/size
        def normalized(contour):
            z=contour.eval(units)-contour.center
            return z.real/max(np.ptp(z.real),1)+1j*z.imag/max(np.ptp(z.imag),1)
        a,b=normalized(reference),normalized(target)
        # A source path may start halfway down a different side at another
        # weight. Register the whole circuit before matching local spans.
        phases=(np.arange(size)[:,None]+np.arange(0,size,3))%size
        start=int(np.argmin(np.mean(abs(b[phases]-a[::3])**2,axis=1)))
        b=np.roll(b,-start)
        indices=np.arange(0,size+1,8)
        self.ref=indices/size
        jumps=np.arange(1,29)
        j=np.arange(size+1)
        previous=j[:,None]-jumps
        step_penalty=.004*((jumps-8)/8)**2
        cost=np.full(size+1,np.inf)
        cost[0]=0.
        parents=[]
        for i in indices[1:]:
            transitions=cost[np.maximum(previous,0)]+step_penalty
            transitions[previous<0]=np.inf
            winner=np.argmin(transitions,axis=1)
            parents.append(previous[j,winner])
            cost=transitions[j,winner]+abs(b[j%size]-a[i%size])**2
        matched=[size]
        for parent in reversed(parents):
            matched.append(parent[matched[-1]])
        self.positions=(np.array(matched[::-1])+start)/size
        corners=target.knots[target.corners]
        turns=self.positions[0]+(corners-self.positions[0])%1
        self.stops=np.r_[self.ref,np.interp(turns,self.positions,self.ref)]

    def eval(self,positions):
        return self.target.eval(np.interp(positions,self.ref,self.positions))


class PolarProfile:
    """Corresponding points on closed rings lie on the same normalized ray.

    A circle and a rounded rectangle may start on unrelated source nodes.
    Registering their contours by ray keeps their straight sides stationary
    while the corner radius changes. Open-sided shapes need arc registration.
    """
    def __init__(self, contour):
        self.contour = contour
        self.arc = np.unique(np.r_[contour.knots, np.linspace(0,1,max(96,int(contour.length/1.8)))])
        samples = contour.eval(self.arc)
        x, y = samples.real, samples.imag
        rx, ry = np.ptp(x)/2, np.ptp(y)/2
        if min(rx,ry)<1:
            self.valid=False
            return
        self.center = (x.min()+rx)+1j*(y.min()+ry)
        self.scale = (rx,ry)
        relative = samples-self.center
        rays = relative.real/rx+1j*relative.imag/ry
        self.sign = 1 if contour.area>0 else -1
        self.angles = np.unwrap(self.sign*np.angle(rays))/(2*np.pi)
        # A radial side, as on a pie wedge, is not single-valued in this
        # coordinate system. Register it by arc length instead.
        self.valid = (min(abs(rays))>.03 and self.angles[-1]-self.angles[0]>.999
                      and np.all(np.diff(self.angles)>=np.diff(self.arc)/18-1e-9))
        self.stops = self.angle(contour.eval(contour.knots[contour.corners])) if self.valid else []

    def angle(self,points):
        z=points-self.center
        return (self.sign*np.angle(z.real/self.scale[0]+1j*z.imag/self.scale[1])/(2*np.pi))%1

    def eval(self,positions):
        angles=self.angles[0]+(positions-self.angles[0])%1
        return self.contour.eval(np.interp(angles,self.angles,self.arc))


def layer_box(rings):
    if not rings:
        return None
    # Include interior extrema of native quadratic and cubic segments.
    samples=np.concatenate([c.eval(np.unique(np.r_[c.knots,np.linspace(0,1,128)])) for c in rings])
    lo=np.array([samples.real.min(),samples.imag.min()])
    size=np.array([np.ptp(samples.real),np.ptp(samples.imag)])
    return lo,np.maximum(.5,size)


def fit_layer(layer,valid,xyz):
    reference=layer[valid[0]]
    ordered=[order_rings(reference,layer[i]) for i in valid]
    tracks=[]
    ends=[]
    count=0
    for j,ring in enumerate(reference):
        if len(ring.corners):
            ring=ring.roll(ring.corners[0])
        profiles=[PolarProfile(cs[j]) for cs in ordered]
        if not all(p.valid and p.sign==profiles[0].sign for p in profiles):
            profiles=[Profile(ring,[0.,1.],[0.,1.],0)]
            profiles.extend(ArcProfile(ring,cs[j]) for cs in ordered[1:])
        points=compatible_points(profiles,tolerance=.45,compact=.24)
        tracks.append(np.array(points))
        count+=len(points[0])
        ends.append(count-1)
    z=np.concatenate(tracks,axis=1)
    actual=np.stack([z.real,z.imag],axis=-1)
    result=np.empty((len(xyz),*actual.shape[1:]),dtype=np.int16)
    result[valid]=np.rint(actual)
    if len(valid)<len(xyz):
        boxes=[layer_box(rings) for rings in layer]
        origins,sizes=map(np.array,zip(*(boxes[i] for i in valid)))
        relative=(actual-origins[:,None,:])/sizes[:,None,:]
        for i in sorted(set(range(len(xyz)))-set(valid)):
            displacements=xyz[valid]-xyz[i]
            distances=np.linalg.norm(displacements,axis=1)
            neighbors=np.argsort(distances)[:16]
            first=neighbors[0]
            lo,size=boxes[i] or (origins[first]+sizes[first]/2,np.zeros(2))
            # Continue a contour's motion across the small interval in which
            # its neighbouring alternate is active. The command bounds are
            # known exactly even when a fresh slit has just opened.
            nearby=displacements[neighbors]-displacements[first]
            weights=1/(.015+distances[neighbors]**2)
            fit=nearby.T@(nearby*weights[:,None])+.04*np.eye(3)
            predict=-displacements[first]@np.linalg.solve(fit,nearby.T*weights)
            delta=np.tensordot(predict,relative[neighbors]-relative[first],axes=1)
            result[i]=np.rint(lo+(relative[first]+np.clip(delta,-.16,.16))*size)
    return result,ends


def pack_icon(job):
    name,cache_path=job
    file=Path(cache_path)/(name+'.npz')
    if file.exists():
        return name
    shapes=[]
    for cell in CELLS:
        parts=[]
        for path in glyph_parts(name,*cell):
            p=OutlinePen(None)
            for ring in path.contours:
                if abs(ring.area)>1.2:ring.draw(p)
            parts.append(p.contours)
        shapes.append(parts)
    signatures=[tuple((sum(c.area<0 for c in rs),sum(c.area>0 for c in rs)) for rs in parts)
                for parts in shapes]
    unique=list(dict.fromkeys(signatures))
    groups=np.array([unique.index(s) for s in signatures])
    entries={"groups":groups}
    xyz=np.asarray([[n[k] for k in KEYS] for n in NORMAL])
    # A knockout may split one stroke while the other strokes keep their
    # identities. Fit each individual paint command across every master where
    # it exists, independent of the topology of the neighbouring commands.
    layers={}
    for group,signature in enumerate(unique):
        tracks=[]
        ends=[]
        count=0
        for j,kind in enumerate(signature):
            if not any(kind):
                continue
            key=(j,kind)
            if key not in layers:
                valid=[i for i,sig in enumerate(signatures) if sig[j]==kind]
                best=min(valid,key=lambda i:sum(xyz[i]**2))
                valid=[best]+[i for i in valid if i!=best]
                layer=[parts[j] for parts in shapes]
                layers[key]=fit_layer(layer,valid,xyz)
            points,stops=layers[key]
            tracks.append(points)
            ends.extend(count+np.array(stops))
            count+=points.shape[1]
        entries['coords'+str(group)]=np.concatenate(tracks,axis=1)
        entries['ends'+str(group)]=np.asarray(ends,dtype=int)
    temp=file.with_suffix('.part.npz')
    np.savez_compressed(temp,**entries)
    os.replace(temp,file)
    return name


def interval(i,value):
    tag=KEYS[i]
    choices=VALUES[i]
    j=choices.index(value)
    lo=AXES[tag][0] if not j else (choices[j-1]+value)/2
    hi=AXES[tag][2] if j==len(choices)-1 else (value+choices[j+1])/2
    a,b = normalizeValue(lo,AXES[tag]),normalizeValue(hi,AXES[tag])
    if j<len(choices)-1:b=round(b*16384)/16384-1/16384
    return a,b


def grid_supports():
    """Local tensor-product tents reproduce each integer master exactly."""
    indices = {c:i for i,c in enumerate(CELLS)}
    for cell in CELLS[1:]:
        varying = [i for i in range(3) if cell[i] != DEFAULT[i]]
        support = {}
        for i in varying:
            values = VALUES[i]
            j = values.index(cell[i])
            left, right = values[max(0,j-1)], values[min(len(values)-1,j+1)]
            support[KEYS[i]] = tuple(normalizeValue(v, AXES[KEYS[i]]) for v in (left,cell[i],right))
        terms = []
        for size in range(len(varying)+1):
            for subset in itertools.combinations(varying,size):
                knot = tuple(cell[i] if i in subset else DEFAULT[i] for i in range(3))
                terms.append((indices[knot], (-1)**(len(varying)-size)))
        yield support,terms


def compile_cached(directory):
    source=ROOT/'fonts/variable/AdmiraltySymbols[wght].ttf'
    font=instantiateVariableFont(TTFont(source,recalcTimestamp=False),{'wght':400},optimize=False)
    cmap=dict(font.getBestCmap())
    del font['GSUB'],font['STAT']
    order=['.notdef','space']
    glyphs={n:font['glyf'][n] for n in order}
    variations={n:[] for n in order}
    substitutions=[{} for _ in CELLS]
    rtl_rules=[]
    supports = list(grid_supports())
    for spec in CATALOG:
        stem=spec.name.replace('-','_')
        with np.load(directory/(spec.name+'.npz')) as data:
            groups=data['groups']
            for k in np.unique(groups):
                i=int(k)
                name=stem if not i else stem+'.design'+str(i)
                coords,ends=data['coords'+str(i)],data['ends'+str(i)].tolist()
                master_coords=coords.astype(np.int32)
                base=master_coords[0]
                glyphs[name]=simple(base,ends,[1,0]*(len(base)//2))
                glyphs[name].flags[0]|=0x40
                variations[name]=[]
                for support,terms in supports:
                    delta=sum(master_coords[j]*sign for j,sign in terms)
                    if np.any(delta):
                        variations[name].append(TupleVariation(support,[tuple(p) for p in delta.tolist()]+[(0,0)]*4))
                order.append(name)
                if spec.rtl_mirror:
                    mirror=name+'.rtl'
                    g=Glyph();g.numberOfContours=-1
                    c=GlyphComponent();c.glyphName=name;c.x=840;c.y=0;c.transform=[[-1,0],[0,1]];c.flags=4
                    g.components=[c];glyphs[mirror]=g;order.append(mirror);variations[mirror]=[]
                    rtl_rules.append(f'sub {name} by {mirror};')
                if i:
                    for idx in np.flatnonzero(groups==i):
                        substitutions[idx][stem]=name
                        if spec.rtl_mirror:substitutions[idx][stem+'.rtl']=name+'.rtl'
    font.setGlyphOrder(order)
    glyf=font['glyf'];glyf.glyphOrder=order;glyf.glyphs=glyphs
    metrics={}
    for n in order:
        g=glyphs[n];g.recalcBounds(glyf);metrics[n]=(840,getattr(g,'xMin',0))
    font['hmtx'].metrics=metrics
    b=FontBuilder(font=font)
    b.setupCharacterMap(cmap)
    b.setupFvar([(k,*v,AXIS_NAMES[k]) for k,v in AXES.items()],
                [{'location':dict(wght=100*j,wdth=100,RADI=0),'stylename':n} for j,n in enumerate(WEIGHTS,1)])
    b.setupStat([{'tag':k,'name':v} for k,v in AXIS_NAMES.items()])
    b.setupGvar(variations)
    addOpenTypeFeaturesFromString(font,'languagesystem DFLT dflt; feature rtlm {'+' '.join(rtl_rules)+'} rtlm;')
    regions=[([{k:interval(i,cell[i]) for i,k in enumerate(KEYS)}],mapping) for cell,mapping in zip(CELLS,substitutions) if mapping]
    if regions:addFeatureVariations(font,regions,featureTag='rvrn')
    unique_id=fullrange_unique_id(font,'AdmiraltySymbols-Fullrange')
    for rec in list(font['name'].names):
        value={1:'Admiralty Symbols Fullrange',3:unique_id,4:'Admiralty Symbols Fullrange',
               6:'AdmiraltySymbols-Fullrange',16:'Admiralty Symbols Fullrange'}.get(rec.nameID)
        if value:font['name'].setName(value,rec.nameID,rec.platformID,rec.platEncID,rec.langID)
    font.recalcTimestamp=False
    OUTPUT.mkdir(exist_ok=True)
    dest=OUTPUT/'AdmiraltySymbols[wght,wdth,RADI].ttf'
    font.save(dest)
    font.flavor='woff2';font.save(dest.with_suffix('.woff2'))
    print(len(CATALOG),'symbols,',len(order),'glyph records,',dest.stat().st_size,'bytes',flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workers',type=int,default=3)
    parser.add_argument('--only',nargs='+')
    args=parser.parse_args()
    directory=CACHE/fingerprint();directory.mkdir(parents=True,exist_ok=True)
    names=args.only or list(by_name)
    jobs=[(n,str(directory)) for n in names]
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        for i,n in enumerate(pool.map(pack_icon,jobs),1):
            if i%25==0 or args.only:print(i,n,flush=True)
    if not args.only:compile_cached(directory)
