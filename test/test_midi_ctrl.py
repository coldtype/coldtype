from coldtype import *
from coldtype.midi.controllers import LaunchControlXL, LaunchkeyMini

obv = Font.Cacheable("~/Type/fonts/fonts/ObviouslyVariable.ttf")

@renderable((1080, 1080), bg=1, rstate=1)
def render(r, rstate):
    nxl, style = LaunchControlXL(rstate.midi)
    nmn, _ = LaunchkeyMini(rstate.midi)

    dps = (StyledString("Midi",
        Style(obv, **style, r=1, ro=1))
        .pen()
        .align(r)
        .f(1)
        #.understroke(sw=nxl(71)*20)
        )
    
    return [
        (DATPen().rect(r)
            .f(Gradient.Vertical(r, hsl(nxl(10)), hsl(nxl(20))))),
        dps.copy().castshadow(nxl(41)*200-100, nxl(51)*1000).f(0),
        dps
    ]