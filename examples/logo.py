from coldtype import *
from coldtype.midi.controllers import LaunchControlXL
from coldtype.fx.skia import phototype

"""
For instagram
"""

obv = Font.Cacheable("assets/ColdtypeObviously-VF.ttf")

@renderable(rstate=1)
def logo(r, rs):
    nxl = LaunchControlXL(rs.midi)
    return DPS([
        DP(r).f(0),
        (DP().oval(r.inset(-20))
            .f(None).s(1).sw(2)
            .ch(phototype(r, blur=10, cut=23, cutw=5))),
        (StSt("COLD\nTYPE", obv, 500,
            wdth=0.5, tu=-50, r=1,
            kp={"P/E":-100}, leading=5)
            .index(0, lambda p: p.translate(-10, 0))
            .reversePens()
            .align(r, th=1, tv=1)
            .rotate(15)
            .translate(3, 10)
            .understroke(sw=25)
            .f(1)
            .ch(phototype(r,
                blur=2+10*nxl(10),
                cut=50+200*nxl(20),
                cutw=1+10*nxl(30),
                fill=bw(1))))])