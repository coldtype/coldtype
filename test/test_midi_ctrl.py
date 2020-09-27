from coldtype import *
from coldtype.midi.controllers import LaunchControlXL, LaunchkeyMini

obv = Font.Cacheable("~/Type/fonts/fonts/ObviouslyVariable.ttf")

@renderable((1080, 1080), bg=1, rstate=1)
def render(r, rstate):
    nxl, style = LaunchControlXL(rstate.midi)
    nmn, _ = LaunchkeyMini(rstate.midi)

    dps = (StyledString("Midi",
        Style(obv, **style, r=1, ro=1))
        .fit(500)
        .pen()
        .align(r)
        .f(1)
        #.understroke(sw=nxl(71)*20)
        )
    
    return [
        (DATPen().rect(r)
            .f(Gradient.Vertical(r, hsl(nxl(10, 0.25)), hsl(nxl(20, 0.45))))),
        (dps.copy()
            .castshadow(nxl(41, 0)*150-75, nxl(51, 0.75)*1000).f(0)
            .f(Gradient.Vertical(r, hsl(nxl(30, 0.8)), hsl(nxl(40, 0.5))))),
        dps
    ]