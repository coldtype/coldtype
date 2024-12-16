from coldtype import *
from coldtype.raster import *
from functools import partial

rsx = random_series(-2, 2, 1)
rsy = random_series(-2, 2, 2)
rsa = random_series(-10, 10, 3)
rsw = random_series(0, 1, 4)

@renderable(bg=hsl(0.7))
def restmake(r):
    d = 17
    s = Scaffold(r.inset(0, 60)).numeric_grid(d)

    def letter(txt, i, r, seed=0):
        return (StSt(list(txt)[i%4], "NCND", 40, wght=rsw[i+seed])
            .pen()
            .unframe()
            .f(0)
            .align(r)
            .t(rsx[i+seed*5], rsy[i+seed*10])
            .rotate(rsa[i+seed]))

    def point(txt, seed, x):
        row = x.el.data("row")
        col = x.el.data("col")
        if p := x.el.r.pc if row%2 == 0 else x.el.r.pe if col < d - 1 else None:
            return letter(txt, x.i, Rect.FromCenter(p, 20), seed).f(1)

    return (P(
        P().enumerate(s.cells(), partial(point, "rest", 0)),
        P().enumerate(s.cells(), partial(point, "make", 1))
            .rotate(10, point=s.r.psw),
    ).align(s).ch(phototype(r, 1, 110, 65)))
