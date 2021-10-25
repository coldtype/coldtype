from coldtype import *
from coldtype.midi.controllers import LaunchControlXL

co = raw_ufo("assets/ColdtypeObviously_BlackItalic.ufo")

@ui()
def memory(u):
    nxl = LaunchControlXL(u.midi)

    txt = (StSt("CDELOPTY", Font.ColdtypeObviously(), ro=1,
        font_size=100+nxl(20)*200,
        wdth=nxl(10))
        .align(u.r).f(hsl(nxl(50, 0.75))))
    
    return PS([
        P(u.r).f(hsl(nxl(30, 0.5))),
        P().glyph(co["C"]).align(u.r).f(hsl(nxl(40, 0))),
        txt])