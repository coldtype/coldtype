from coldtype import *
from coldtype.warping import warp

font = Font.Cacheable("assets/ColdtypeObviously.designspace")

@renderable(rect=(900, 500))
def coldtype(r):
    return (StSt("COLDTYPE", font, 450,
        wdth=1, tu=-50,
        r=1, ro=1, fit=r.w,
        kp={("L","D"): -5,
            ("T","Y"): -20,
            ("Y","P"): 10,
            ("P","E"): -100})
        .align(r)
        .pmap(lambda idx, p: (p
            .f(hsl(0.5+idx/len(p.parent())*0.15, s=0.6, l=0.55))
            .ch(warp(5, mult=25))))
        .understroke(sw=30)
        .rotate(5)
        .scale(0.75))