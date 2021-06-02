from coldtype import *
from coldtype.fx.skia import phototype

r = Rect(1080, 1080)
a = DP().oval(r.inset(150, 300)).flatten(10).roughen(200, seed=3)
b = DP().oval(r.inset(150, 300)).flatten(10).roughen(200, seed=1)

tl = Timeline(90)

@animation(r, timeline=tl)
def cloud(f):
    return DPS([
        DP(f.a.r).f(hsl(0.6, 0.6, 0.6)),
        (DP.Interpolate([a, b], f.a.progress(f.i, loops=1, easefn="ceio").e)
            .f(1)
            .smooth()
            .ch(phototype(f.a.r, blur=20, cut=100, cutw=20)))])

def release(passes):
    FFMPEGExport(cloud, passes).gif().write()