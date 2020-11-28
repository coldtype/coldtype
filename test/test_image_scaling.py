from coldtype import *

tl = Timeline(30)

@animation((1000, 1000), timeline=tl)
def test_scaling(f):
    px = (0.01+f.a.progress(f.i, loops=1, easefn="eei").e*0.99)*1000
    pr = Rect(math.floor(px), math.floor(px))
    return (StyledString("CT",
        Style("assets/ColdtypeObviously-VF.ttf", 800, wdth=1))
        .pen()
        .scale(px/1000)
        .align(pr)
        .f(0)
        .precompose(pr, f.a.r))

@animation((1000, 1000), timeline=tl)
def test_precomposed_scaling(f):
    px = (0.01+f.a.progress(f.i, loops=1, easefn="eei").e*0.99)*1000
    pr = Rect(math.floor(px), math.floor(px))
    return (StyledString("TY",
        Style("assets/ColdtypeObviously-VF.ttf", 800, wdth=1, tu=-200, r=1))
        .pens()
        .f(1)
        .understroke(sw=20)
        .align(f.a.r)
        .phototype(f.a.r, blur=10, cut=230, cutw=3, fill=bw(0))
        .precompose(f.a.r, scale=px/1000))