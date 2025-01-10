from coldtype import *
from coldtype.raster import phototype
from coldtype.fx.skia import freeze

@animation(bg=0, tl=240)
def scratch(f):
    ri = f.a.r.inset(160)
    dt = P().m(ri.psw).ioc(ri.pne, 50).fssw(-1, 1, 10)

    def pt(t, a=-45, w=100, h=5):
        return (P()
            .rect(Rect.FromCenter(dt.point_t(t)[0], w, h))
            .rotate(a)
            .f(1))
    
    def angler(e):
        return ez(e, "seio", 1, rng=(-90, -110))
    
    def strokes():
        return (P().enumerate(range(0, 250), lambda x: pt(x.e, angler(x.e)))
            .ch(phototype(f.a.r, 5, 90, 13)))
    
    form = freeze(1, 1, strokes, [angler])

    return (P(
        #dt,
        form,
        pt(f.e("seio", 1), angler(f.e("seio", 1)), 102, 20)
            .ch(phototype(f.a.r, 3, 120, 30, hsl(0.07, 0.90, 0.50))),
    ))
