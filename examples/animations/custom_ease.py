from coldtype import *
from coldtype.fx.xray import skeleton

@animation(timeline=60, bg=1)
def easer(f):
    ease_curve = P().withRect(1000, lambda r, p: p
        .moveTo(r.psw)
        .ioEaseCurveTo(r.pn, 2, 50)
        .ioEaseCurveTo(r.pse, 21, 30))
    
    return P(
        ease_curve.copy()
            .scaleToWidth(f.a.r.w-50)
            .align(f.a.r)
            .layer(
                lambda p: p.fssw(-1, hsl(0.9), 2),
                lambda p: p.ch(skeleton(scale=1.25)).s(hsl(0.65))),
        StSt("COLD", Font.ColdtypeObviously()
            , 300
            , wdth=f.e(ease_curve, 0))
            .align(f.a.r)
            .fssw(-1, (0, 0.5), 2))