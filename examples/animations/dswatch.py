from coldtype import *

ds = Font("assets/ColdtypeObviously.designspace")

@animation(timeline=120, watch=[ds], composites=1)
def dswatch(f):
    return (DPS([
        (StSt("C", ds,
            1000, ro=1, wdth=f.e("ceio", 1))
            .align(f.a.r)
            .f(0).s(1).sw(5))])
        #.phototype(f.a.r, blur=2, cut=130, fill=0, cutw=20)
        )