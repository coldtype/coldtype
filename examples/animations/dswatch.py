from coldtype import *
from coldtype.warping import warp_fn
from functools import partial

ds = Font("assets/ColdtypeObviously.designspace")

def shake(idx, p):
    """shake up the vector w/ a skia effect"""
    return p.attr(skp=dict(
        PathEffect=skia.DiscretePathEffect.Make(2, 2, idx)))

@animation(timeline=(120, 23.976), watch=[ds])
def dswatch(f):
    return (DPS([
        (StSt("COLD", ds, 510, ro=1, r=1,
            wdth=f.e(1),
            tu=250+-450*(f.e(1)))
            .align(f.a.r)
            .f(0).s(1).sw(4)
            .pmap(lambda i,p: p
                .flatten(15)
                .nlt(warp_fn(f.i*20, mult=10)))
            .chain(partial(shake, f.i)))])
        .phototype(f.a.r, blur=2,
            cut=125, cutw=20,
            fill=hsl(0.65)))