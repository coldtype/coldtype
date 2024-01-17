from coldtype import *
from coldtype.fx.skia import spackle, phototype

@animation(bg=0)
def scratches(f):
    return P(
        P(f.a.r)
            .ch(spackle(cut=235, cutw=1))
            .ch(phototype(f.a.r,
                blur=3, cut=120, fill=hsl(0.35, 1))),
        P(f.a.r)
            .ch(spackle(cut=235, cutw=30))
            .ch(phototype(f.a.r,
                blur=3, cut=120, fill=hsl(0.85, 1))),
        P(f.a.r)
            .ch(spackle(cut=205, cutw=1))
            .ch(phototype(f.a.r,
                blur=10, cut=150, cutw=20, fill=hsl(0.17, 1))))
