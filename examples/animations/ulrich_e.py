from coldtype import *
from coldtype.raster import *

r = Rect(1080)
s = Scaffold(r.inset(10, 10)).numeric_grid(19, gap=4, annotate_rings=True)

img = (StSt("e", "neuehaas", 85)
    .f(1)
    .align(s[0].r, tx=1, ty=1)
    .insert(0, P(s[0].r)
        .f(hsl(0.08, 0.8, 0.6, a=0.0)))
    .ch(rasterized(s[0].r.inset(-10), wrapped=True)))

@animation(1080, tl=60, bg=hsl(0.11, 0.80, 0.88), mute=0)
def manye_live(f):
    return (P().enumerate(s.cells(), lambda x: img.copy()
        .align(x.el.r, tx=1, ty=1)
        .rotate(x.el.data("ring_e")*360+f.adj(-x.el.data("ring")*6).e("eeio", 0, r=(0, -360))))
        .ch(phototype(f.a.r, 1.5, 120, 30, fill=0.1)))