from coldtype.test import *

@ui((1000, 1000))
def test_mouse_interp(u):
    ri = u.r.inset(100)
    sx, sy = ri.ipos(u.c)
    return [
        P(ri).fssw(-1, hsl(0.9, a=0.3), 2),
        (StSt("VARI\nABLE", Font.MutatorSans(), 150
            , wdth=sx, wght=sy)
            .xalign(u.r)
            .lead(30)
            .align(u.r)
            .f(0))]
