from coldtype import *
from functools import partial

def pair(tx, f, i, _):
    fa = f.adj(-i*4)
    ro = fa.e("linear", rng=(0, -360))
    
    dp = (DP((f.a.r
            .take(350, "mdx")
            .take(30, "mny")))
        .f(1).s(0).sw(5)
        .translate(0, i*10))

    return DPS([
        (dp.copy().rotate(ro)),
        ßhide(dp.copy()
            .rotate(-ro+270)
            .translate(tx, 0))])

@animation((1080, 1920), timeline=240)
def twister(f:Frame):
    tx = 250
    return (DPS.Enumerate(range(0, 1), partial(pair, tx, f))
        .translate(-tx*0.5, 300)
        .reversePens()) #+ DP(f.a.r).f(None).s(0).sw(1)