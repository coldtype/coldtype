from coldtype import *
from coldtype.fx.skia import phototype

r = Rect(1080, 1080)
a = P().oval(r.inset(200)).flatten(10).roughen(10, seed=3)
b = P().oval(r.inset(200)).flatten(10).roughen(2000, seed=1)

@animation(r, timeline=90, bg=hsl(0.7))
def cloud(f):
    return (a.copy().interpolate(f.e("eeio", 1), b)
        .f(1)
        .smooth()
        .ch(phototype(f.a.r, blur=10, cut=210, cutw=3)))

release = cloud.export("gif")