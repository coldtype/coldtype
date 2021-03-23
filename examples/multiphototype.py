from coldtype import *

fnt = Font.Cacheable("assets/ColdtypeObviously-VF.ttf")

@animation((1080, 540), bg=hsl(0.4, s=1, l=0.8))
def stub(f):
    e = f.a.progress(f.i, loops=1, easefn="eeio").e

    txt = (StyledString("COLDTYPE",
        Style(fnt, 500-e*170, wdth=0.20+e*0.3, r=1, ro=1, tu=-50, rotate=e*10, kp={"T/Y":-30}))
        .pens()
        .f(1)
        .align(f.a.r))

    return DPS([
        ßshow(txt.copy()
            .understroke(s=1, sw=20)
            .phototype(f.a.r, cut=90, cutw=30, fill=hsl(0.7, s=1, l=0.3))),
        (txt.copy()
            .understroke(s=0, sw=20)
            .phototype(f.a.r, cut=190, cutw=20, fill=hsl(0.9, s=1, l=0.8))
            )])