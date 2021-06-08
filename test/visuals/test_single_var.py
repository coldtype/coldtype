from coldtype.test import *
from coldtype.text.composer import Glyphwise

tl = Timeline(180, fps=30)

@animation((1080, 1080), timeline=tl, bg=0)
def test_multi_var(f):
    fs = 200
    
    # TODO rewrite w/ an asciitimeline?

    lookup = dict(
        T=dict(wght=f.e(4, on=[0]), wdth=f.e(4, on=[0])),
        Y=dict(wght=f.e(4, on=[1]), wdth=f.e(4, on=[1])),
        P=dict(wght=f.e(4, on=[2]), wdth=f.e(4, on=[2])),
        E=dict(wght=f.e(4, on=[3]), wdth=f.e(4, on=[3])))
    
    pens = (Glyphwise("TYPE",
        lambda i, c: Style(mutator, fs, **lookup[c]))
        .align(f.a.r)
        .f(1))
    
    ero = 360*f.e(4, on=[3])
    pens[-1].rotate(ero)

    if True:
        zoom = f.a.progress(f.i, loops=4, easefn="eeio")
        cidx = math.floor(zoom.loop/2)
        pe = zoom.e
        (pens.center_on_point(f.a.r, pens[cidx].bounds().point("C"), interp=pe)
            .scale(1+pe*2, point=pens[cidx].bounds().point("C")))

    return DPS([
        pens,
        #StSt("TYPE", mutator, fs).align(f.a.r)
    ])