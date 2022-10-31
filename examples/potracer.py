from coldtype import *
from coldtype.fx.skia import phototype, potrace

@animation((1080, 540), bg=1)
def potraced(f):
    return (StSt("COLD".upper(), Font.ColdObvi(), 300, wdth=1, tu=-190)
        .align(f.a.r)
        .reverse()
        .fssw(1, 0, 10, 1)
        #.ch(phototype(f.a.r, 3, cut=170, cutw=16))
        #.ch(potrace(f.a.r, turdsize=100))
        #.f(hsl(0.8))
        )