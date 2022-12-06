from coldtype import *

@renderable((1580, 350))
def render(r):
    return P(
        P(r.inset(10)).outline(10).f(hsl(0.65)),
        StSt("COLDTYPE", Font.ColdtypeObviously()
            , fontSize=250
            , wdth=1
            , tu=-250
            , r=1
            , rotate=15)
            .align(r)
            .fssw(hsl(0.65), 1, 5, 1)
            .translate(0, 5))