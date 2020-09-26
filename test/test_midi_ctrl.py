from coldtype import *
from coldtype.midi.controllers import LaunchControlXL, LaunchkeyMini

obv = Font.Cacheable("~/Type/fonts/fonts/ObviouslyVariable.ttf")

nxl, style = LaunchControlXL(CMC)
nmn, _ = LaunchkeyMini(CMC)

@renderable((1080, 1080), bg=1)
def render(r):
    return [
        (DATPen().rect(r)
            .f(Gradient.Vertical(r, hsl(nxl(10)), hsl(nxl(20))))),
        (StyledString("Midi",
            Style(obv, **style, r=1, ro=1))
            .pens()
            .align(r)
            .f(1)
            .understroke(sw=nxl(71)*20))]