from coldtype import *
from coldtype.fx.skia import phototype

r = Rect(1080, 540)

@renderable(r)
def bg(r):
    return P(
        P(r).f(Gradient.Vertical(r, hsl(0.3), hsl(0.6))),
        StSt("BG", Font.MuSan(), 250, wght=1, wdth=0)
            .f(1)
            .align(r)
            .ch(phototype(r, blur=3, cutw=30)))

@renderable(r, bg=bg)
def bg_user(r):
   return P(r.inset(50)).fssw(-1, 1, 6)