from coldtype import *
from coldtype.fx.skia import phototype

fatface = Font.Find("OhnoFatfaceV")

@animation(timeline=Timeline(100, storyboard=[0]), bg=0)
def render(f):
    c1, c2 = (f.a.r
        .inset(0, 50)
        .divide(f.e(1, rng=(0.15, 0.85)), "N")
        .map(λ.inset(20, 5))
        )

    #c1, c2 = [r.inset(20, 5) for r in cs]
    s = Style(fatface, t=-25, wdth=1, wght=1, ro=1, r=1)

    return (PS([
            (StSt("STACKED &",
                s.mod(fitHeight=c1.h, opsz=f.e(1))
                , fit=c1)
                .align(c1)
                .track_to_rect(c1, pullToEdges=1, r=1)),
            (StSt("JUSTIFIED",
                s.mod(fitHeight=c2.h, opsz=f.e(1, rng=(1, 0)))
                , fit=c1)
                .align(c2)
                .track_to_rect(c2, pullToEdges=1, r=1))])
        .f(1)
        .understroke(sw=10)
        .ch(phototype(f.a.r, blur=3, cut=150, cutw=25)))