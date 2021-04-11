from coldtype import *
from coldtype.filtering import spackler

@animation(bg=0)
def stub(f):
    return DPS([
        (DP(f.a.r)
            .chain(spackler(cut=235, cutw=1))
            .phototype(f.a.r, blur=3, cut=120, fill=hsl(0.35, 1))),
        (DP(f.a.r)
            .chain(spackler(cut=235, cutw=30))
            .phototype(f.a.r, blur=3, cut=120, fill=hsl(0.85, 1))),
        (DP(f.a.r)
            .chain(spackler(cut=205, cutw=1))
            .phototype(f.a.r, blur=10, cut=150, cutw=80, fill=hsl(0.17, 1)))])
