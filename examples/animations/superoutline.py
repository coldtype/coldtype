from coldtype import *
from coldtype.fx.skia import phototype
from coldtype.warping import warp

fnt = Font.ColdtypeObviously()
rs = random_series(0, 1000)

@animation(bg=1, timeline=Timeline(92, 23.976))
def outline(f):
    return (StSt("COLD\nTYPE", fnt, 330,
            ro=1, rotate=10, leading=45,
            tu=f.e(1, rng=(500, 70)),
            wdth=f.e(1))
        .align(f.a.r)
        .pen()
        .ch(warp(-1, rs[f.i//4+10], mult=5))
        .layer(
            lambda p: p.fssw(hsl(0.3), hsl(0.3, 1, 0.75), 30),
            lambda p: p.layer(
                lambda p: p.fssw(1, 1, 100).ch(warp(-1, rs[f.i//4], mult=10)),
                lambda p: p.fssw(0, 0, 17))
                .ch(phototype(f.a.r,
                    blur=3, cut=200, cutw=20,
                    fill=hsl(0.75, 1, 0.605))),
            lambda p: p.f(1)
                .ch(phototype(f.a.r,
                    blur=3, cutw=10,
                    cut=230+f.e(1, rng=(-30, 5)),
                    fill=hsl(0.65, 0.7, 0.55)))))