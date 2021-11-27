from coldtype import *
from coldtype.fx.xray import skeleton

@animation(timeline=60, write_start=30)
def scratch(f):
    p = P().With1000(lambda r, p: p
        .moveTo(r.psw)
        .ioEaseCurveTo(r.pne, 5, 50)
        .connect(P()
            .moveTo(r.psw)
            .ioEaseCurveTo(r.pne, 15, 50)
            .scale(1, -1)))
    
    return PS([
        P(f.a.r).f(1),
        P(f.a.r.take(80, "mxy").take(f.e("l", 0), "W")).f(0, 0.1),
        (p.copy()
            .scaleToWidth(f.a.r.w-100)
            .align(f.a.r)
            .layer(
                λ.fssw(-1, hsl(0.9), 2),
                λ.ch(skeleton()).s(hsl(0.65))
            )),
        StSt("COLD", Font.ColdtypeObviously(), 300,
            wdth=f.e(p, 0)).align(f.a.r).f(0, 0.5)])

release = scratch.export("h264", loops=4)