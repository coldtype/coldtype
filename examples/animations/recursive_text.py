from coldtype import *
from coldtype.fx.skia import phototype, fill

fnt = Font.ColdtypeObviously()
dfnt = Font.RecursiveMono()

@animation(timeline=80, bg=hsl(0.3, 1, 0.9), composites=1)
def discord(f):
    return (DPS([
            (StSt("COLDTYPE", fnt,
                font_size=f.e(1, rng=(250, 20)),
                wdth=f.e("ceio", 1, rng=(1, 0)),
                tu=f.e(1, rng=(-150, 0)), r=1)
                .align(f.a.r)
                .f(1).understroke(sw=15)),
            (StSt("Recursive", dfnt,
                font_size=f.e("ceio", 1, rng=(1, 200)),
                tu=f.e("ceio", 1, rng=(0, -100)))
                .rp()
                .align(f.a.r)
                .f(1)
                .understroke(sw=15)
                .v(f.e(1) > 0.5))])
        .translate(0, f.e("eeio", 1, rng=(y:=390, -y)))
        .insert(0, f.lastRender(lambda p: p
            .scale(0.995)
            .ch(fill(1))))
        .ch(phototype(f.a.r, blur=1.5, cut=137, cutw=35,
            fill=hsl(f.e(1, rng=(0.65, 0.85))))))