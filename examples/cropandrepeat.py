from coldtype import *
from coldtype.fx.skia import phototype
from coldtype.fx.motion import filmjitter

@animation(bg=hsl(0.93, 0.6, 0.5), tl=120*2)
def scratch(f):
    _, cycle = f.adj(23*2).e("eeio", 4, loop_info=1)
    loops = 2

    def crop(e, p):
        _e = 10+ez(e, "eei") * p.ambit(tx=0, ty=1).h
        _crop = P(p.ambit(tx=0, ty=1).take(_e, "N", forcePixel=1))
        return (p
            .intersection(_crop)
            .unframe()
            .align(f.a.r, "S", tx=1)
            .t(ez(e, "seio", 1)*f.e("eeio", loops, rng=(f.e("eeio", rng=(110, 510)), -f.e("eeio", rng=(110, 610)))), 0))

    out = (StSt("CROP AND REPEAT", Font.MuSan(), 170, wght=f.e("eeio", loops, rng=(0, 1)), wdth=1, fit=f.a.r.w+-10)
        .layer(47)
        .mape(crop)
        .stack(f.e("eeio", loops, rng=(4, 6)))
        .scale(f.e("eeio", loops, rng=(0.7, 0.36)))
        .align(f.a.r.drop(10, "S"), "S")
        .rotate(0.25)
        .f(1)
        .ch(phototype(f.a.r, 1.5, 105, 30, fill=hsl(0.17, 0.8, 0.65)))
        )
    
    return P().gridlines(f.a.r).fssw(-1, bw(1, 0.3), 1).ch(filmjitter(f.e("l"), speed=(2, 3))) + out

release = scratch.export("h264", loops=4)