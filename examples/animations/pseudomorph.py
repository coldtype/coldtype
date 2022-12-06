from coldtype import *

r = Rect(1440, 540)

@animation(r, tl=70)
def pseudomorph(f):
    return (StSt("HELLO" if f.e() < 0.5 else "WORLD"
        , Font.MutatorSans()
        , f.e(rng=(300, 100))
        , wght=f.e()
        , wdth=f.e()
        , rotate=f.e(rng=(0, 360))
        )
        .align(f.a.r, tx=0))