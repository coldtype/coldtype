from coldtype import *
from coldtype.raster import *

r = Rect(1080)
s = Scaffold(r.inset(10, 10)).labeled_grid(d:=15, d, g:=4, g)

img = (StSt("e", "neuehaas", 135)
    .f(1)
    .align(s[0].r, tx=1, ty=1)
    .insert(0, P(s[0].r)
        .f(hsl(0.08, 0.8, 0.6, a=0.0)))
    .ch(rasterized(s[0].r.inset(-10), wrapped=True)))

@animation(1080, tl=60, bg=hsl(1.09, 0.80, 0.40), mute=0)
def manye_live(f):
    return (P().enumerate(s.cells(), lambda x: img.copy()
        .align(x.el.r, tx=1, ty=1)
        .rotate(f.adj(-x.e)
            .e("eeio", 0, r=(x.i*(d:=23), -360+x.i*d))
            , point=x.el.r.pc))
        .ch(phototype(f.a.r, 1.5, 120, 30, fill=hsl(0.17, 0.8, 0.7))))