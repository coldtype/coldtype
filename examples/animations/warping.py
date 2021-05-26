from coldtype import *
from coldtype.warping import warp_fn

Style.RegisterShorthandPrefix("≈", "~/Type/fonts/fonts")
peshka = Font.Cacheable("≈/CoFoPeshkaV0.4_Variable.ttf")

loop = Loop(120, 12, [
    dict(wdth=0, wght=1, rotate=-15, font_size=700, warp=0),
    dict(wdth=1, wght=1, rotate=0, font_size=110, warp=100),
    dict(wdth=0, wght=0, rotate=15, font_size=500, warp=0),
    dict(wdth=0.5, wght=0.5, rotate=0, font_size=330, warp=50),])

@animation(timeline=loop)
def warp(f):
    state = f.a.t.current_state(f.i)
    return ((ß:=StSt("WARP", peshka, **state))
        .align(f.a.r)
        .pen()
        .f(Gradient.V(ß.ambit(), hsl(0.7), hsl(0.9)))
        .nlt(warp_fn(f.i*30, f.i, mult=state["warp"])))
