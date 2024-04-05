from coldtype import *
from functools import partial

def pair(tx, f, x):
    fa = f.adj(-x.i*3)
    ro = fa.e("eeio", 0, rng=(0, -360))
    p = (P(f.a.r
            .take(350, "mdx")
            .take(30, "mny"))
        .fssw(1, 0, 5)
        .translate(0, x.i*10))

    return P(
        p.copy().rotate(ro),
        p.copy()
            .rotate(-ro+270)
            .translate(tx, 0))

@animation((1080, 1080), timeline=120)
def twister(f:Frame):
    tx = 250
    return (P().enumerate(range(0, 30),
        partial(pair, tx, f))
        .translate(-tx*0.5, 300)
        .reversePens())