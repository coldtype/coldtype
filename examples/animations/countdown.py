from coldtype.test import *
from coldtype.fx.skia import phototype, spackle, color_phototype
from coldtype.fx.motion import filmjitter

at = AsciiTimeline(2, 18, """
                                <
[C ][O ][L ][D ][T ][Y ][P ][E ]
""")

@animation((1080, 1080)
    , tl=at
    , bg=0
    , composites=1
    , render_bg=1)
def countdown(f:Frame):
    c = at.current()

    return (P(f.a.r)
        .ch(spackle(xs=0.35, ys=0.35, cut=230, fill=bw(0), base=f.i))
        .ups()
        .insert(0, P(f.a.r).f(1, 0.1))
        .insert(0, f.last_render(
            filmjitter(f.a.progress(f.i).e, speed=(50, 50), scale=(3, 5))))
        .append(StSt(c.name
            , Font.Find("ObviouslyV")
            , c.e("l", 0, rng=(1, 1500))
            , wdth=f.e("seio", 1, rng=(1, 0.25))
            #, wght=f.e("seio", 0, rng=(1, 0))
            , wght=0.25
            , ro=1
            , ss01=1)
            #.pen()
            .fssw(1, 1, 25)
            .align(f.a.r, th=1, tv=1)
            #.cond(c.name == "C",
            #    lambda p: p.insert(0,
            #        P(f.a.r).f(0)))
            .blendmode(BlendMode.Cycle(22, show=0)))
        .cond(f.i == at.timeables[0].end-1,
            lambda p: p.insert(2, P(f.a.r).f(0)))
        .ch(phototype(f.a.r
            , cut=150
            , blur=2.5
            , cutw=20)))

    c = at.current()
    return (StSt(c.name
        , Font.ColdObvi()
        , c.e("eeo", 0, rng=(0, 1200))
        , wdth=1
        , ro=1)
        .align(f.a.r)
        .fssw(0, 1, 20)
        .blendmode(BlendMode.Xor)
        #.f(1)
        .append(P(f.a.r).ch(spackle(cut=155, cutw=1, fill=bw(0), base=f.i)))
        .ch(phototype(f.a.r, 2, cutw=1))
        .ups()
        .insert(0, f.lastRender(lambda p: p
            .ch(filmjitter(f.e("l", 0), speed=(50, 50)))))
        .insert(1, P(f.a.r).f(0, 0.25))
        .ch(phototype(f.a.r, 2, cut=151, cutw=20)))
    
release = countdown.export("h264", loops=2)