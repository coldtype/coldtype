from coldtype import *
from coldtype.fx.warping import warp
from coldtype.fx.skia import phototype, shake

"""
Saving a change to UFOs included in the designspace
file should automatically update the coldtype window
"""

ds = Font("assets/ColdtypeObviously.designspace")

@animation(timeline=(120, 23.976), watch=[ds], bg=0)
def dswatch(f):
    return (PS([
        (StSt("COLD", ds, 510,
            wdth=f.e(1), tu=250+-450*(f.e(1)))
            .ro().rp().align(f.a.r)
            .fssw(0, 1, 5)
            .pmap(warp(5, f.i*20, mult=10))
            .ch(shake(5, 2, seed=f.i)))])
        .ch(phototype(f.a.r,
            blur=2,
            cut=125,
            cutw=20,
            fill=1)))