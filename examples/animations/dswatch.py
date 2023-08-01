from coldtype import *
from coldtype.fx.skia import phototype, shake

"""
Saving a change to UFOs included in the designspace
file should automatically update the coldtype window
"""

ds = Font("assets/ColdtypeObviously.designspace")

@animation(timeline=(120, 23.976), watch=[ds], bg=0)
def dswatch(f):
    return (StSt("COLD", ds, 510
        , wdth=f.e(1)
        , tu=250+-450*(f.e(1))
        , r=1
        , ro=1)
        .align(f.a.r)
        .fssw(0, 1, 5)
        .chain(shake(5, 2, seed=f.i))
        .chain(phototype(f.a.r,
            blur=3,
            cut=155,
            cutw=20,
            fill=1)))