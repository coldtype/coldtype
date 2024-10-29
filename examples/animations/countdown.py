from coldtype import *
from coldtype.raster import *
from coldtype.fx.motion import filmjitter

at = AsciiTimeline(3, 18, """
                                <
C   O   L   D   T   Y   P   E
""").inflate()

rs = random_series(seed=8)

@animation((1080, 800)
    , tl=at
    , bg=0
    , composites=1
    , render_bg=1
    , release=lambda x: x.export("h264", loops=4))
def countdown(f:Frame):
    c = at.current()

    def postprocess(result):
        return P(
            P(f.a.r).f(hsl(0.7, 0.7, 0.8)),
            result.ch(luma(f.a.r, hsl(0.7, 0.7, 0.4))))

    return (P(f.a.r)
        .ch(spackle(xs=0.35, ys=0.35, cut=230, fill=bw(0), base=f.i))
        .ups()
        .insert(0, P(f.a.r).f(1, 0.1))
        .insert(0, f.last_render(
            filmjitter(f.e("l"), speed=(50, 50), scale=(3, 5))))
        .append(StSt(c.name, Font.MutatorSans()
            , fontSize=c.e("sei", 0, rng=(100, 1200))
            , wdth=c.e("sei", 0)
            , wght=rs[c.idx+1]*0.25
            , ro=1)
            .fssw(1, 1, 13)
            .align(f.a.r, tx=1, ty=1)
            .blendmode(BlendMode.Xor))
        .ch(phototype(f.a.r
            , cut=139, blur=2.5, cutw=20, fill=1))
        .postprocess(postprocess))