from coldtype import *
from coldtype.raster import phototype

r = Rect(1080)
ri = r.inset(160)
p = P().m(ri.psw).ioc(ri.pne, 50).fssw(-1, 1, 10)

def angler(e):
    return ez(e, "seio", 1, rng=(-90, -110))

def hatch(pt, a=-45, w=100, h=5):
    return (P()
        .rect(Rect.FromCenter(pt, w, h))
        .rotate(a)
        .f(1))

samples = p.samples(7)
curve = p.enumerate(samples, lambda x: hatch(x.el.pt, angler(x.e))).ch(phototype(r, 5, 90, 13))

@animation(bg=0, tl=Timeline(240, 48))
def scratch(f):
    return (P(
        curve,
        hatch(p.point_t(f.e("seio", 1))[0], angler(f.e("seio", 1)), 102, 20)
            .ch(phototype(f.a.r, 3, 120, 30, hsl(0.07, 0.90, 0.50)))))
