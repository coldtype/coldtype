from coldtype import *
from coldtype.raster import *

r = Rect(1080)
s = Scaffold(r.inset(10, 10)).labeled_grid(d:=23, d, 4, 4)

img = (StSt("e", "neuehaas", 70)
    .f(1)
    .align(s[0].r, tx=1, ty=1)
    .insert(0, P(s[0].r)
        .f(hsl(0.08, 0.8, 0.6, a=0.0)))
    .ch(rasterized(s[0].r, wrapped=True)))

eases = ["eeio", "ceio", "seio", "eei", "eeo"]
re = random_series(0, len(eases), 0, mod=int)

@animation(1080, tl=60, bg=0, mute=0)
def manye_live(f):
    return (P().enumerate(s.cells(), lambda x: img.copy()
        .align(x.el.r, tx=1, ty=1)
        .rotate(f.adj(-x.e).e(eases[re[x.i]], 1, r=(x.i*(d:=8), 180+x.i*d)), point=x.el.r.pc)))