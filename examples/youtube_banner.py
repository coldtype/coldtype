from coldtype import *
from coldtype.fx.skia import phototype

obv = Font.Cacheable("assets/ColdtypeObviously-VF.ttf")
logos = raw_ufo("assets/logos.ufo")

@renderable((2048, 1152))
def banner(r):
    return (DATPens([
        DATPen().rect(r).f(hsl(0.65)),
        (StyledString("COLDTYPE",
            Style(obv, 300, wdth=1, tu=-90, r=1, rotate=-10))
            .pens()
            .f(1)
            .understroke(sw=35)
            .align(r)
            .translate(0, 5)
            .ch(phototype(r, blur=5, cut=200, cutw=10)))]))