from coldtype import *
from coldtype.fx.skia import phototype, fill

@animation(timeline=80, bg=0, composites=1)
def recursive(f):
    return (P(
        (StSt("COLDTYPE", Font.ColdtypeObviously()
            , font_size=f.e(1, rng=(250, 20))
            , wdth=f.e("ceio", 1, rng=(1, 0))
            , tu=f.e(1, rng=(-150, 0))
            , r=1)
            .align(f.a.r)
            .fssw(1, 0, 15, 1)),
        (StSt("Recursive", Font.RecursiveMono()
            , font_size=f.e("ceio", 1, rng=(1, 200))
            , tu=f.e("ceio", 1, rng=(0, -100))
            , r=1)
            .align(f.a.r)
            .fssw(1, 0, 15, 1)
            .visible(f.e(1) > 0.5)))
        .translate(0, f.e("eeio", 1, rng=(y:=390, -y)))
        .insert(0, f.lastRender(lambda p: p
            .scale(0.995)
            .ch(fill(1))))
        .ch(phototype(f.a.r, blur=1.5, cut=137, cutw=35,
            fill=hsl(f.e(1, rng=(0.95, 0.75)), 0.6, 0.6))))

release = recursive.export("h264", loops=4)