from coldtype import *

tl = Timeline(30)

@animation(timeline=tl)
def test_scaling(f):
    px = (0.01+f.a.progress(f.i, loops=1, easefn="eei").e*0.99)*1000
    pr = Rect(math.floor(px), math.floor(px))
    return (StyledString("CT",
        Style("assets/ColdtypeObviously-VF.ttf", px*0.8, wdth=1))
        .pen()
        .align(pr)
        .f(0)
        .precompose(SkiaPen, pr, f.a.r, context=__CONTEXT__))