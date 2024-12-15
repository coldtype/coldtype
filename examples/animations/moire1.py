from coldtype import *
from coldtype.raster import *

from noise import pnoise1

r = Rect(1080)

def patternmaker():
    d = 20
    s = Scaffold(Rect(1920)).numeric_grid(d, int(d))
    return s.borders().s(1).ch(rasterized(s.r, wrapped=True)).align(r)

pattern = freeze(1, 0, patternmaker)

def postprocess(p):
    return P(
        P(r).f(hsl(0.50, 0.6)),
        p.ch(phototype(r, 1.40, 100, 14, fill=hsl(0.60))))

@animation(bg=0, tl=Timeline(120, 18), composites=1)
def scratch(f):
    last = f.last_render(λ.align(f.a.r).a(0.95))
    
    n = pnoise1(f.e("l", 0, rng=(0, 10)), base=2, octaves=16)
    ro = n * -150
    
    return (P(
        last,
        pattern.copy()
            .align(f.a.r)
            .rotate(ro, point=r.pc))
        .postprocess(postprocess))