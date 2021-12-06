from coldtype import *

@animation((1920, 540), timeline=Timeline(60, 30))
def irregardless(f):
    return (StSt("Coldtype".upper(), Font.ColdObvi(), 300
        , wdth=f.e("eeio")
        , tu=f.e("eeio", rng=(-190, 100))
        , ro=1)
        .align(f.a.r)
        .pmap(lambda i,p: p
            .rotate(360*f.adj(-i*0.25).e("eeio", 1)))
        .fssw(hsl(0.7, a=0.75), 0, 5))