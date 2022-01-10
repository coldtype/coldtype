from subprocess import run
from coldtype import *
from coldtype.fx.xray import skeleton

@animation(timeline=60, bg=1)
def easer(f):
    p = P().withRect(1000, lambda r, p: p
        .moveTo(r.psw)
        .ioEaseCurveTo(r.pne, 5, 50)
        .connect(P()
            .moveTo(r.psw)
            .ioEaseCurveTo(r.pne, 15, 50)
            .scale(1, -1)))
    
    return PS([
        (p.copy()
            .scaleToWidth(f.a.r.w-100)
            .align(f.a.r)
            .layerv(
                λ.fssw(-1, hsl(0.9), 2),
                λ.ch(skeleton(scale=0.5)).s(hsl(0.65)))),
        (StSt("COLD", Font.ColdtypeObviously()
            , 300
            , wdth=f.e(p, 0))
            .align(f.a.r)
            .f(0, 0.5))])