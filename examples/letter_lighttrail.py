from coldtype import *
from coldtype.raster import *

r = Rect(1080, 1080)
letters = "RANDOM"

rc = random_series()
rstroke = random_series(0.45, 1)

@animation(r, bg=1
    , tl=Timeline(240, 12)
    , release=lambda x: x.export("h264", loops=2, date=True))
def scribble_random(f):
    seed = f.i+2
    
    letter = (StSt(
        letters[math.floor(f.e("l", 0, rng=(0, len(letters) )))]
        , font=Font.MuSan()
        , fontSize=1105
        , wght=f.e("l", 1)
        , wdth=0.25
        , ro=1)
        .align(r, ty=1)
        .scaleToRect(f.a.r.inset(50)))
    
    points = letter.pen().flatten(10).point_list()
    rp = random_series(0, len(points), seed=seed, mod=int)

    lines = (P().enumerate(range(0, int(f.e("eei", 1, rng=(15, 25)))), lambda x: P()
        .moveTo(points[rp[x.i]])
        .enumerate(range(0, int(f.e("seio", rng=(6, 200)))), lambda y: y.parent
            .declare(yi:=y.i*10)
            .cond(rc[x.i+yi] > f.e("l", rng=(0.1, 0.75)),
                lambda p: p.lineTo(points[rp[1+yi+x.i]]),
                lambda p: p.curveTo(
                    points[rp[1+yi+x.i]],
                    points[rp[2+yi+x.i]],
                    points[rp[3+yi+x.i]])))
        .endPath()
        .fssw(-1, 1, rstroke[x.i])
        .ch(phototype(f.a.r
            , blur=2
            , cut=40
            , cutw=15
            , fill=hsl(x.e*0.5+f.e("l", 0, rng=(0, 10)), 0.9, 0.4))))
        .blendmode(BlendMode.Cycle(16)))
    
    return (P(
        P(f.a.r)
            .ch(spackle(cut=235, cutw=1, base=f.i, fill=bw(1)))
            .ch(phototype(f.a.r,
                blur=3, cut=170, fill=hsl(f.i*0.1))),
        lines)
        .postprocess(lambda p: p.ch(temptone(.05,.02))))