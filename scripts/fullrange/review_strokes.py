"""Probe exposed flat cuts and through-bars whose geometry is straight in Regular."""
import numpy as np

from check_junctions import RAILS
from check_word_proof import section

FLAT = set("AEFHIKLMNPRTVWXYZbdfhiklmnprtu vwxz".replace(" ", "")) | {
    'dotlessi','dotlessj','Hbar','hbar','Dcroat','dcroat','Tbar','tbar',
    'Eng','Lslash','lslash','IJ','ij','one','four','seven','one.tnum','four.tnum','seven.tnum'}
BARS = dict(RAILS, plus=[(350,(.09,.23,.77,.91))], plusminus=[(475,(.09,.23,.77,.91))],
            equal=[(270,(.12,.3,.7,.88)),(432,(.12,.3,.7,.88))])


def cuts_at_end(edges, height, inward):
    far = height + inward*np.array([46., 60., 74., 88.])
    near = height + inward*np.array([.75, 1.75, 3., 4.25])
    spans = [section(edges,y) for y in [*far,*near]]
    count = len(spans[0])
    if not count or count%2 or any(len(z)!=count for z in spans):
        return {}
    bands = np.array(spans).reshape(8,-1,2)
    output = {}
    for index in range(count//2):
        rails = bands[:4,index]
        model = np.polyfit(far-height, rails, 1)
        def predict(ys):
            return (ys[:,None]-height)*model[0]+model[1]
        if np.max(abs(rails-predict(far))) > 1.4:
            continue
        normal = np.ptp(predict(near),axis=1)
        if normal.min() < 8 or normal.max()>280:
            continue
        ends = bands[4:,index]
        ratios = np.ptp(ends,axis=1)/normal
        j = np.argsort(ratios)[1]
        output[count,index] = (float(ratios[j]), float(normal[j]), complex(np.mean(ends[j]),near[j]),
                               np.max(abs(ends-predict(near))))
    return output


def straight_cuts(current, regular, height, regular_height, inward, side):
    ref = cuts_at_end(regular, regular_height, inward)
    if not ref:
        return
    for key,(ratio,pred,point,_) in cuts_at_end(current,height,inward).items():
        anchor = ref.get(key)
        if (anchor and abs(anchor[0]-1)<.065 and anchor[3]<3 and
                ratio < .73 and (1-ratio)*pred>6):
            yield side, point, 1-ratio, dict(tipWidth=ratio*pred,expectedWidth=pred)


def sample_bar(edges, expected, taps):
    left = edges.real.min()
    span = np.ptp(edges.real)
    result = []
    for x in left+span*np.array(taps):
        plateau = []
        samples = []
        for delta in (-.022, -.011, 0., .011, .022):
            sample = x+span*delta
            bands = section(edges,sample,vertical=True).reshape(-1,2)
            band = min(bands,key=lambda pair: abs(pair.mean()-expected), default=None)
            if band is None or abs(band.mean()-expected)>80 or not 7<np.ptp(band)<160:
                samples.append(None)
            else:
                samples.append(np.r_[sample, band])
        for a,b in zip(samples,samples[1:]):
            if a is not None and b is not None and max(abs(a[1:]-b[1:])) < 1.6:
                plateau.append((a+b)/2)
        if not plateau:
            return None
        result.append(min(plateau,key=lambda p: abs(p[0]-x)))
    return np.array(result)


def through_bars(edges, regular, specs):
    for row,(y,taps) in enumerate(specs):
        ref = sample_bar(regular,y,taps)
        if ref is None or np.ptp(ref[:,1:],axis=0).max()>3:
            continue
        result = sample_bar(edges, np.mean(ref[:,1:]), taps)
        if result is None:
            continue
        centers = result[:,1:].mean(axis=1)
        drift = np.ptp(centers)
        thick = np.median(result[:,2]-result[:,1])
        if drift > max(8, .24*thick):
            j = np.argmax(abs(centers-np.median(centers)))
            yield 'rail', complex(result[j,0],centers[j]), drift/thick, dict(offset=drift, thickness=thick,
                                                                             railNumber=row+1)
