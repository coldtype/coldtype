from coldtype import *
from coldtype.raster import phototype, potrace

@renderable((1080, 540), bg=1)
def potraced(r):
    return (StSt("COLD".upper(), Font.ColdObvi(), 300, wdth=1, tu=-190)
        .align(r)
        .reverse()
        .fssw(1, 0, 10, 1)
        .ch(phototype(r, 3, cut=170, cutw=16))
        .ch(potrace(r, turdsize=100))
        #.print(lambda p: p.value)
        .f(hsl(0.8)))