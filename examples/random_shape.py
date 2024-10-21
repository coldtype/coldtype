from coldtype import *
from coldtype.fx.skia import phototype

@animation(bg=0, tl=Timeline(120, 12))
def scribble(f):
    seed = f.i
    ri = f.a.r.inset(50)
    rx = random_series(ri.mnx, ri.mxx, seed=seed)
    ry = random_series(ri.mny, ri.mxy, seed=seed+1)

    return (P().enumerate(range(0, int(f.e("seio", 1, rng=(1, 200)))), lambda x: P()
        .moveTo(rx[x.i], ry[x.i])
        .enumerate(range(0, 20), lambda y: y.parent
            .declare(yi:=y.i*10)
            .curveTo(
                (rx[1+yi+x.i], ry[1+yi+x.i]),
                (rx[2+yi+x.i], ry[2+yi+x.i]),
                (rx[3+yi+x.i], ry[3+yi+x.i])))
        .endPath()
        .fssw(-1, 1, f.e("eei", 1, rng=(0.5, 5)))
        .ch(phototype(f.a.r
            , blur=f.e("eei", 1, rng=(1.75, 10))
            , cut=40
            , cutw=15
            , fill=hsl(x.e*0.5+f.e("l", 0, rng=(0, 10)), 0.8))))
        .blendmode(BlendMode.Cycle(14)))

release = scribble.export("h264", loops=2)