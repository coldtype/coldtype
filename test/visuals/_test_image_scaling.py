from coldtype import *
from coldtype.fx.skia import phototype, precompose

tl = Timeline(30)

@animation(r:=(750, 750), timeline=tl)
def test_scaling(f):
    px = f.e("eei", r=(10, 1000))
    pr = Rect(math.floor(px), math.floor(px))
    return (StSt("CT", Font.ColdObvi(), 800, wdth=1)
        .pen()
        .scale(px/1000)
        .align(pr, th=1)
        .f(0)
        .ch(precompose(pr, f.a.r)))

@animation((1000, 1000), timeline=tl)
def test_precomposed_scaling(f):
    px = f.e("eei", r=(10, 1000))
    return (StSt("TY", Font.ColdObvi(), 800, wdth=1, tu=-200, r=1)
        .pens()
        .f(1)
        .understroke(sw=20)
        .align(f.a.r)
        .ch(phototype(f.a.r, blur=10, cut=230, cutw=3, fill=bw(0)))
        .ch(precompose(f.a.r, scale=-px/1000)))