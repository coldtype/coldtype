from coldtype import *
from coldtype.midi.controllers import LaunchControlXL

"""
For instagram
"""

obv = Font.Cacheable("assets/ColdtypeObviously-VF.ttf")

@renderable(rstate=1)
def logo(r, rs):
    nxl = LaunchControlXL(rs.midi)
    
    return DATPens([
        DATPen().rect(r).f(hsl(0.6, s=1, l=0.25)).f(0),
        (DATPen()
            .oval(r.inset(-20))
            .f(None)
            .s(1)
            .sw(2)
            .phototype(r, blur=10, cut=23, cutw=5)),
        (Composer(r, "COLD\nTYPE",
            Style(obv, 500, wdth=0.5, tu=-50, r=1, kp={"P/E":-100}),
            leading=15)
            .pens()
            .index(0, lambda p: p.translate(-10, 0))
            .reversePens()
            .f(1)
            .align(r, th=1, tv=1)
            .rotate(15)
            .translate(3, 10)
            .understroke(sw=25)
            .f(1)
            .phototype(r,
                blur=2+10*nxl(10),
                cut=50+200*nxl(20),
                cutw=1+10*nxl(30),
                fill=bw(1)))])