from coldtype import *
from coldtype.fx.skia import phototype

tl = Timeline(90)
r = Rect(1080, 1080)

a = P().oval(r.inset(150, 300)).flatten(10).roughen(200, seed=3)
b = P().oval(r.inset(150, 300)).flatten(10).roughen(200, seed=1)

@animation(r, timeline=tl)
def cloud(f):
    print(__memory__)
    return PS([
        P(f.a.r).f(hsl(0.6, 0.6, 0.6)),
        (P.Interpolate([a, b], f.e("eeio", 1))
            .f(1)
            .smooth()
            .ch(phototype(f.a.r, blur=10, cut=100, cutw=50)))])

release = cloud.export("gif")