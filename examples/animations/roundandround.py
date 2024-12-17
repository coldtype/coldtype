from coldtype import *
from coldtype.raster import phototype, filmjitter

e1 = (P().withRect(Rect(1000), lambda r, p: p
    .m(r.psw)
    .ioc(r.pc, 10, 30)
    .ioc(r.pne, 10, 30)
    .ep()))

e2 = (P().withRect(Rect(1000), lambda r, p: p
    .m(r.psw)
    .ioc(r.pn, 10, 30)
    .ioc(r.pse, 10, 30)
    .ep()))

e3 = (P().withRect(Rect(1000), lambda r, p: p
    .m(r.psw)
    .ioc(r.pc, 30, 30)
    .ioc(r.pne, 30, 30)
    .ep()))


@renderable(1000, bg=1, solo=-1)
def easer(r):
    return P(e1, e2, e3).fssw(-1, 0, 1)


@animation(bg=hsl(0.07, 0.8, 0.50), tl=Timeline(180, 18), release=λ.export("h264", loops=2))
def rounder(f):
    j = f.e("seio", 1, rng=(7, 6))

    h = 500
    def setter(x):
        nonlocal h
        fs = 32 - x.i*0.58
        h -= (fs)

        #el = StSt("S", Font.MuSan(), fs+12, wght=1, wdth=1-x.e).layer(21)
        el = P(Rect(fs*(1-(x.e*0.9)), fs)).layer(21)

        return (el
            .align(f.a.r)
            .t(0, h)
            .f(0)
            .unframe()
            .map(lambda i, p: p
                .rotate(-i * 360/len(el), point=f.a.r.pc)
                .ch(filmjitter(f.adj(-x.i).e("l", 0), x.i+i, scale=(j,j))))
            .align(f.a.r)
            .rotate(f.e(e1, 0, rng=(0, f.e(e2, 0, rng=(0, -x.i*85.10))))))
            
    
    return (P().enumerate(range(0, 14), setter)
        .f(1)
        .rotate(f.e(e3, 0, rng=(0, -360)))
        .ch(phototype(f.a.r
            , blur=f.e(e2, 0, rng=(12, 1))
            , cut=f.e(e2, 0, rng=(60, 183))
            , cutw=f.e(e2, 0, rng=(3, 43))
            , fill=hsl(0.17, 1.00, 0.70))))