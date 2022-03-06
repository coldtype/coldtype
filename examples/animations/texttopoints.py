from coldtype import *
from coldtype.fx.skia import phototype

# inspired by https://p5js.org/reference/#/p5.Font/textToPoints

@animation(timeline=126, bg=hsl(0.6, 1, 0.33))
def texttopoints(f):
    return (StSt("COLD", Font.ColdObvi(), 1000, wdth=0)
        .align(f.a.r)
        .pen()
        .removeOverlap()
        .flatten(10)
        .nonlinear_transform(lambda x, y: (x+math.sin(f.i+(y*0.05))*10, y))
        .f(1)
        .ch(phototype(f.a.r, fill=hsl(0.6, 1, 0.7), cutw=10)))