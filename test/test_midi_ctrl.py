from coldtype import *
from coldtype.warping import warp_fn
from coldtype.midi.controllers import LaunchControlXL, LaunchkeyMini

obv = Font("~/Type/fonts/fonts/ObviouslyVariable.ttf")
nxl, style = LaunchControlXL(CMC)
nmn, _ = LaunchkeyMini(CMC)

@animation((1080, 1080), bg=hsl(0.5))
def render(f):
    return [
        DATPen().rect(f.a.r).f(Gradient.Vertical(f.a.r, hsl(nmn(10)), hsl(nmn(20)))),
        (StyledString("Midi",
            Style(obv, **style, r=1, ro=1))
            .pens()
            .align(f.a.r)
            .pmap(lambda i,p: (p
                .flatten(5)
                .nlt(warp_fn(nxl(81)*1000, mult=nxl(80, 0)*200+1))))
            .f(1)
            .understroke(sw=nxl(71)*20+1))]