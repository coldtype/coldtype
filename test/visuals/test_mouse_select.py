from coldtype.test import *

@ui((1000, 1000))
def test_select(u):
    txts = "COLDTYPE"
    rows = u.r.inset(10).subl(len(txts), 10, "N")

    return PS.Enumerate(rows, lambda x: PS([
        (P(x.el).f(rf:=hsl(x.e*0.3+0.5))
            .cond(u.c.inside(x.el), lambda p: p.f(0))),
        (StSt(txts[x.i], Font.ColdtypeObviously(), 100)
            .align(x.el.subdivide(len(txts), "W")[x.i])
            .f(rf.lighter(0.2)))]))