from coldtype import *

fnt = Font.Cacheable("assets/ColdtypeObviously-VF.ttf")

@renderable((1080, 540), bg=hsl(0.4, s=1, l=0.8))
def stub(r):
    txt = (StyledString("COLDTYPE",
        Style(fnt, 500, wdth=0.20, r=1, ro=1, tu=-50, rotate=10))
        .pens()
        .f(1)
        .align(r))

    return DPS([
        (txt.copy()
            .understroke(s=1, sw=20)
            .phototype(r, cut=90, cutw=30, fill=hsl(0.7, s=1, l=0.3))),
        (txt.copy()
            .understroke(s=0, sw=20)
            .phototype(r, cut=190, cutw=20, fill=hsl(0.9, s=1, l=0.8)))])