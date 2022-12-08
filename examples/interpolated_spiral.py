from coldtype import *

rs = random_series()

@aframe()
def spiral(f):
    return (P().enumerate(range(0, 30), lambda x:
        StSt("COLDTYPE", Font.ColdtypeObviously(), 220, wdth=x.e, ro=1)
            .align(f.a.r)
            .fssw(-1, hsl(x.e, s=0.7, a=1.3-x.e), 2)
            .rotate(-200+x.e*200)))