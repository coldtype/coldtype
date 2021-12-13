from coldtype import *
from coldtype.fx.skia import phototype, spackle, luma, fill, precompose
from coldtype.fx.motion import filmjitter

at = AsciiTimeline(3, 18, """
                                <
C   O   L   D   T   Y   P   E
""")

for a, b in at.enumerate(pairs=True):
    if a.start == a.end:
        if a.start < b.start:
            a.end = b.start
        else:
            a.end = at.duration

rs = random_series(seed=8)

@animation((1080, 800)
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
            filmjitter(f.e("l"), speed=(50, 50), scale=(3, 5))))
        .append(StSt(c.name, Font.MutatorSans()
            , c.e("sei", 0, rng=(100, 1200))
            , 500
            , wdth=c.e("sei", 0)
            , wght=rs[c.idx+1]*0.25
            , ro=1)
            .fssw(1, 1, 13)
            .align(f.a.r, th=1, tv=1)
            .blendmode(BlendMode.Xor))
        .ch(phototype(f.a.r
            , cut=139, blur=2.5, cutw=20)))

@animation((1080, 800), tl=at, bg=hsl(0.7, 0.7, 0.8), render_bg=1, solo=1)
def recolor(f):
    return (countdown.frame_img(f.i)
        .ch(luma(f.a.r))
        .ch(precompose(f.a.r))
        .ch(fill(hsl(0.7, 0.7, 0.4))))

release = recolor.export("h264", loops=4)