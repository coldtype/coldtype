from coldtype import *

@renderable((1580, 350))
def render(r):
    c1 = hsl(0.65, 0.7)
    c2 = hsl(0.53, 0.6)

    return P(
        (P(r.inset(10))
            .outline(10)
            .f(Gradient.H(r, c2.lighter(0.3), c1.lighter(0.3)))),
        (StSt("COLDTYPE", Font.ColdtypeObviously()
                , fontSize=250
                , wdth=1
                , tu=-250
                , r=1
                , rotate=15)
            .align(r)
            .fssw(Gradient.H(r, c1, c2), 1, 5, 1)
            .translate(0, 5)))