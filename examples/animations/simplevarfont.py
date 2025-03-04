from coldtype import *

@animation((1920, 540), timeline=Timeline(60, 30), bg=1)
def unfold(f):
    return (StSt("Coldtype".upper()
        , Font.ColdObvi()
        , fontSize=f.e("eeio", rng=(100, 300))
        , wdth=f.e("eeio")
        , tu=f.e("eeio", rng=(-130, 100))
        , ro=1)
        .align(f.a.r)
        .mapv(lambda i, p: p
            .rotate(360*f.adj(-i*0.25).e("eeio", 1)))
        .reverse()
        .fssw(hsl(0.7, a=0.75), 0, 10, 1))