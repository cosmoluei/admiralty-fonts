"""Optical sizes for isolated dots, quote heads, narrow tails and solid geometric signs."""
import numpy as np

PUNCT = {"period","colon","colon.case","semicolon","semicolon.case","comma","periodcentered","divide",
         "periodcentered.case","ellipsis","quoteleft","quoteright","quotedblleft","quotedblright",
         "quotesinglbase","quotedblbase","bullet","filledbox","triagup","triagdn","uni25AA",
         "uni25B4","uni25B6","uni25B8","uni25BE","uni25C0","uni25C2","uni25C6","uni25CF"}


def punctuation_coords(optical,name,w,d,scale,shift):
    z=optical.base
    out=z.copy()
    geometric=name.startswith(("uni25","triag")) or name in ("bullet","filledbox")
    for ring in optical.rings:
        ids=np.flatnonzero(ring.segments.sum(axis=(0,1)))
        pts=z[ids]
        center=(pts.real.min()+pts.real.max())/2+1j*(pts.imag.min()+pts.imag.max())/2
        span=max(np.ptp(pts.real),1)
        height=max(np.ptp(pts.imag),1)
        if name=='divide':
            if w==400 and d==100:
                continue
            # The two dots sit above and below the midpoint of the division
            # bar. Set their diameter and the bar's pen weight independently.
            bar=span>2.5*height
            thickness={100:24 if bar else 40,400:height,900:height*1.25}[w]
            xscale=scale if bar else thickness/height
            out[ids]=(center.real*scale+shift+(pts.real-center.real)*xscale
                      +1j*(center.imag+(pts.imag-center.imag)*thickness/height))
            continue
        curved_tail=height>1.46*span and not geometric
        if geometric:
            factor={100:.59 if name=="bullet" else .90,400:1.,900:1.13}[w]
        else:
            factor={100:min(1,40/min(span,height)),400:1.,900:1.19}[w]
        horizontal=1 if w==100 and not curved_tail and not geometric else 1+.22*(d/100-1)
        if w==400 and d==100:
            continue
        # A quote loses weight across its principal direction. This keeps
        # its lower taper visible while its dot-sized head can become thin.
        if curved_tail:
            factor=max(factor,.37)
            v=pts-center
            cov=np.cov(np.column_stack([v.real,v.imag]),rowvar=False)
            _,axes=np.linalg.eigh(cov)
            principal=complex(*axes[:,-1])
            local=v*principal.conjugate()
            delta=principal*(local.real*({100:.83,400:1.,900:1.04}[w])+1j*local.imag*factor)
        else:
            delta=(pts-center)*factor
        cy=center.imag
        if not geometric and not curved_tail and abs(pts.imag.min())<14:
            cy=pts.imag.min()+(cy-pts.imag.min())*factor
        out[ids]=center.real*scale+shift+delta.real*horizontal + 1j*(cy+delta.imag)
    return out+optical.slant*out.imag
