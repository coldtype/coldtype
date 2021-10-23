from coldtype import *

@aframe()
def spiral(f):
    return PS.Enumerate(range(0, 30), lambda x:
        StSt("COLDTYPE", Font.ColdtypeObviously(), 220,
            wdth=x.e)
            .align(f.a.r)
            .fssw(-1, hsl(random(), a=1-x.e), 2)
            .rotate(-200+x.e*200))