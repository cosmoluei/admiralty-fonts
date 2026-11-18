import pathlib
SOURCES = str(pathlib.Path(__file__).resolve().parents[2] / "sources")
import ufoLib2
R=ufoLib2.Font.open(SOURCES + "/AdmiraltySans-Regular.ufo")
P=ufoLib2.Font.open("out3/pilot-w400-d100.ufo")
for n in "nhmurоil".replace("о","o"):
    a,b=R[n],P[n]
    print(n,"adv",a.width,b.width,"bounds",[round(v) for v in a.getBounds(R)],[round(v) for v in b.getBounds(P)])
    pa=[(round(p.x),round(p.y)) for c in a.contours for p in c]
    pb=[(round(p.x),round(p.y)) for c in b.contours for p in c]
    print("  npts",len(pa),len(pb))
    print("  R",pa[:40]); print("  P",pb[:40])
