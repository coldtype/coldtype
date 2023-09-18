from coldtype import *
from coldtype.fx.skia import phototype

fatface = Font.Find("OhnoFatfaceV")

@animation(timeline=Timeline(100, storyboard=[0]), bg=0)
def render(f):
    c1, c2 = (f.a.r
        .inset(0, 50)
        .divide(f.e(1, rng=(0.15, 0.85)), "N")
        .map(lambda p: p.inset(20, 5)))

    s = Style(fatface, t=-25, wdth=1, wght=1, ro=1, r=1)

    return (P(
            (StSt("STACKED &",
                s.mod(fitHeight=c1.h, opsz=f.e(1))
                , fit=c1)
                .align(c1)
                .trackToRect(c1.inset(f.e(1, rng=(30, 0)), 0), pullToEdges=1, r=1)),
            (StSt("JUSTIFIED",
                s.mod(fitHeight=c2.h, opsz=f.e(1, rng=(1, 0)))
                , fit=c1)
                .align(c2)
                .trackToRect(c2, pullToEdges=1, r=1)))
        .fssw(1, 0, 11, 1)
        .sm(0.99)
        .ch(phototype(f.a.r, blur=2, cut=150, cutw=25)))