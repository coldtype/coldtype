from coldtype import *

@animation((1920, 540), timeline=Timeline(60))
def irregardless(f):
    return (StSt("COLDTYPE",
        Font.ColdtypeObviously(),
        font_size=300,
        wdth=f.e("eeio", 1),
        tu=f.e("eeio", 1, rng=(-190, 100)))
        .remove_overlap()
        .align(f.a.r)
        .pmap(λ.rotate(360*f.e("ceio", 1)))
        .fssw(hsl(0.7, a=0.75), 0, 5))