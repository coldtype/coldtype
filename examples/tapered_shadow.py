from coldtype import *
from coldtype.fx.skia import phototype

fnt = Font.Cacheable("assets/ColdtypeObviously-VF.ttf")

@renderable(bg=0)
def taper(r):
    return (StSt("COLD\nTYPE", fnt, 330,
        wdth=0.5, leading=35, tu=60, rotate=10)
        .align(r)
        .layer(
            lambda p: (p.layer(
                lambda p: p.f(1).translate(15, -15),
                lambda p: p.f(0).s(0).sw(7))
                .ch(phototype(r, blur=5, cut=183, cutw=8,
                    fill=hsl(0.75, 0.94, 0.68)))),
            lambda p: p.f(1)
                .ch(phototype(r, blur=3, cut=230, cutw=15,
                    fill=hsl(0.2, 0.86, 0.63)))))