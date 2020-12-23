from coldtype import *
from coldtype.midi.controllers import LaunchControlXL, LaunchkeyMini

obv = Font.Cacheable("~/Type/fonts/fonts/ObviouslyVariable.ttf")

@renderable((1080, 1080), bg=1, rstate=1)
def render(r, rstate):
    nxl = LaunchControlXL(rstate.midi)
    nmn = LaunchkeyMini(rstate.midi)

    style = Style(obv,
        20+nxl(12, 0.25)*2000,
        wdth=nxl(11, 0.25),
        wght=nxl(21),
        slnt=nxl(31),
        tu=-250+nxl(22)*500,
        r=1,
        ro=1)

    dps = (StyledString("Midi", style)
        .pens()
        .align(r)
        .f(1))

    g1 = Gradient.Vertical(r, hsl(nxl(20, 0.25), a=0.25), hsl(nxl(10, 0.45), a=0.25))
    
    return [
        (DATPen().rect(r).f(g1)),
        # (dps.copy().pen()
        #     #.castshadow(nxl(41, 0.3)*100-50, nxl(51, 1)*1000).f(0)
        #     .f(Gradient.Vertical(r, hsl(nxl(30, 0.66)), hsl(nxl(40, 0.5))))),
        dps.understroke(s=g1, sw=nxl(71)*20)
    ]