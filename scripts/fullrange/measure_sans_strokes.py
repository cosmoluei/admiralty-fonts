"""Measure stroke contrast, counters and turning in the exported Sans n, o, a, s and g."""
import argparse
import json

import numpy as np
from fontTools.ttLib import TTFont
from scipy.signal import savgol_filter

from build_text_family import OUTPUT
from check_word_proof import Edges, section_limits, section
from stroke_geometry import bezier, curvature, fair_curves
from study_shapes import draw_letter


def outline(gs, glyph):
    pen = Edges(gs,1)
    gs[glyph].draw(pen)
    return np.asarray(pen.edges)


def s_samples(gs, width):
    design = draw_letter('s',gs['s'].width,100,width)
    curves = fair_curves(design.spines[0])
    ts = np.linspace(0,1,401)
    parameters, spine = [], []
    for index, curve in enumerate(curves):
        for t in (ts if index==0 else ts[1:]):
            parameters.append(index+t)
            spine.append(bezier(curve.points,t))
    arc = np.r_[0,np.cumsum(abs(np.diff(spine)))]
    edges = outline(gs,'s')
    starts,vectors = edges[:,0],edges[:,1]-edges[:,0]
    rows = []
    for u in np.linspace(.01,.99,201):
        v = np.interp(u*arc[-1],arc,parameters)
        index = min(int(v),len(curves)-1)
        t = v-index
        curve = curves[index]
        point, velocity = curve.boundary(t,0)
        normal = 1j*velocity/abs(velocity)
        low,high=section_limits(starts,vectors,point,normal)
        middle=point+(low+high)/2*normal
        bend = curvature(velocity,bezier(curve.acceleration,t))
        rows.append(dict(arc_fraction=u, thickness=high-low, design_curvature_x_height=520*bend,
                         native_mid_x=middle.real,native_mid_y=middle.imag,
                         x=point.real,y=point.imag,normal_x=normal.real,normal_y=normal.imag))
    # Differentiate the actual exported ink midpoints, at a stated physical
    # scale. Single 1000-UPM grid steps can dominate an unsmoothed derivative.
    coords=np.array([(row['native_mid_x'],row['native_mid_y']) for row in rows])
    step=.98*arc[-1]/(len(coords)-1)
    window=max(5,round(80/step/2)*2+1)
    v=savgol_filter(coords,window,3,deriv=1,delta=step,axis=0)
    a=savgol_filter(coords,window,3,deriv=2,delta=step,axis=0)
    bends=(v[:,0]*a[:,1]-v[:,1]*a[:,0])/np.linalg.norm(v,axis=1)**3
    for row,bend in zip(rows,bends):
        row['native_curvature_x_height']=520*bend
        row['curvature_window_units']=(window-1)*step
    return rows


def measure():
    font=TTFont(OUTPUT/'AdmiraltySans[wght,wdth,RADI].ttf')
    readings, traces = [],{}
    for weight in (100,400,900):
        for width in (65,100,150):
            gs=font.getGlyphSet(location=dict(wght=weight,wdth=width,RADI=0))
            n,o,a,g=[outline(gs,c) for c in 'noag']
            def center(edges):
                return (edges.real.min()+edges.real.max())/2
            stem=section(n,260)
            side=section(o,260)
            top=section(o,center(o),True)
            white=section(a,center(a),True)
            g_mid=section(g,260)
            g_vertical=section(g,center(g),True)
            readings.append(dict(weight=weight,width=width,n_stem=stem[1]-stem[0],
                                 o_side=side[1]-side[0],o_top=top[-1]-top[-2],
                                 a_lower_counter=white[2]-white[1],a_upper_space=white[4]-white[3],
                                 g_right_stem=g_mid[-1]-g_mid[-2],
                                 g_tail_clearance=g_vertical[2]-g_vertical[1]))
            if weight==100:
                traces[width]=s_samples(gs,width)
    return dict(units_per_em=font['head'].unitsPerEm, radius=0, measurements=readings, s_thin=traces)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--json', action='store_true')
    args=parser.parse_args()
    report=measure()
    if args.json:
        print(json.dumps(report,separators=(',',':')))
    else:
        print('   Weight    Width   n stem   o side    o top  a lower  a upper   g stem   g tail gap')
        for row in report['measurements']:
            print(''.join(f'{value:9.2f}' for value in row.values()))
        for width,rows in report['s_thin'].items():
            values=[row['thickness'] for row in rows]
            signs=np.sign([row['native_curvature_x_height'] for row in rows])
            changes=[f"{(rows[i]['arc_fraction']+rows[i+1]['arc_fraction'])/2:.1%}" for i in np.flatnonzero(np.diff(signs))]
            print(f'Thin s at {width}%: 201 normal sections, {min(values):.2f} to {max(values):.2f} units; '
                  f'native midline inflections at {", ".join(changes)} (window {rows[0]["curvature_window_units"]:.0f} units)')
