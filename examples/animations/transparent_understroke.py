from coldtype import *
from functools import partial

r = Rect(1080, 680)

def cut(line, i, p):
    if i > 0:
        return p.difference(line[i-1].copy().outline(10, drawOuter=False))

letters = (StSt("COLD\nTYPE", Font.ColdObvi(), 300
    , tu=-200
    , ro=1)
    .map(lambda p: p.map(partial(cut, p))))

curve = (P().withRect(1000, lambda r, p: p
    .m(r.psw)
    .ioc(r.pn, 30, -10)
    .ioc(r.pse, 0, 50)
    .ep()))

@animation(r, tl=Timeline(60), bg=0)
def understroke_cut(f):
    return (letters
        .copy()
        .map(lambda p: p
            .track(f.e(curve, 0, rng=(0, 150))))
        .align(f.a.r)
        .f(1))