from coldtype import *
from coldtype.midi.controllers import LaunchControlXL

cottf = Font.Cacheable("assets/ColdtypeObviously-VF.ttf")
co = raw_ufo("assets/ColdtypeObviously_BlackItalic.ufo")

@renderable(rstate=1)
def memory(r, rstate):
    nxl = LaunchControlXL(rstate.midi)
    dps = (StyledString("CDELOPTY",
        Style(cottf, 100+nxl(20)*200, ro=1, wdth=nxl(10))).pen())
    
    return [
        DATPen().rect(r).f(hsl(nxl(30, 0.5))),
        DATPen().glyph(co["C"]).align(r).f(hsl(nxl(40, 0))),
        dps.align(r).f(hsl(nxl(50, 0.75)))
    ]