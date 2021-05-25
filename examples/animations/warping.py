from coldtype import *
from coldtype.warping import warp_fn

Style.RegisterShorthandPrefix("≈", "~/Type/fonts/fonts")
peshka = Font.Cacheable("≈/CoFoPeshkaV0.4_Variable.ttf")

@animation(timeline=120)
def warp(f):
    return ((ß:=StSt("WARP", peshka,
        690-f.e(1)*500,
        wdth=f.e(2),
        wght=f.e(1)
        ))
        .align(f.a.r)
        .pen()
        .f(Gradient.V(ß.ambit(), hsl(0.7), hsl(0.9)))
        .flatten(5)
        .nlt(warp_fn(f.i*30, f.i, mult=1+f.e(1)*100)))
