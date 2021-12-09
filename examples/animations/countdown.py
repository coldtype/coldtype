from coldtype import *
from coldtype.fx.skia import phototype, spackle
from coldtype.fx.motion import filmjitter

at = AsciiTimeline(2, 18, """
                                <
[C ][O ][L ][D ][T ][Y ][P ][E ]
""")

rs = random_series(seed=8)

@animation((1080, 1080)
    , tl=at
    , bg=0
    , composites=1
    , render_bg=1)
def countdown(f:Frame):
    c = at.current()

    return (P(f.a.r)
        .ch(spackle(xs=0.35, ys=0.35, cut=190, fill=bw(0), base=f.i))
        .ups()
        .insert(0, P(f.a.r).f(1, 0.1))
        .insert(0, f.last_render(
            filmjitter(f.e("l"), speed=(50, 50), scale=(3, 5))))
        .append(StSt(c.name, Font.MutatorSans()
            , c.e("l", 0, rng=(1, 1000))
            , wdth=rs[c.idx]
            , wght=rs[c.idx+1]*0.25
            , ro=1)
            .fssw(1, 1, 25)
            .align(f.a.r, th=1, tv=1)
            .blendmode(BlendMode.Xor))
        .ch(phototype(f.a.r
            , cut=150, blur=2.5, cutw=20)))
    
release = countdown.export("h264", loops=4)