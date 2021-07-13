from coldtype import *
from coldtype.fx.skia import phototype

fnt = Font.Cacheable("assets/ColdtypeObviously-VF.ttf")

"""
An example of a reuseable "chained"-function, i.e. a function
that can be inserted into a fluent chain without the
need to stop and define intermediate variables
"""

def tapered(r, offset, ph1, ph2):
    def _tapered(p:DATPen):
        return (DPS([
            DPS([
                p.copy().f(1).translate(offset, -offset),
                p.copy().f(0).s(0).sw(5),
            ]).ch(phototype(r, **ph1)),
            p.copy().f(1).ch(phototype(r, **ph2))
        ]))

    return _tapered, dict(returns=DATPens)

@renderable(bg=0)
def taper(r):
    return (StSt("COLD\nTYPE", fnt, 330, wdth=0.5, leading=30, tu=60, rotate=10).align(r)
        .ch(tapered(r, 15,
            dict(blur=5, cut=186, cutw=8, fill=hsl(0.75, 0.94, 0.68)),
            dict(blur=5, cut=220, cutw=8, fill=hsl(0.20, 0.86, 0.63)))))