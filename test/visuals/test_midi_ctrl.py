from coldtype import *
from coldtype.midi.controllers import LaunchControlXL

@animation((1080, 1080), bg=1, rstate=1)
def render(f, rstate):
    nxl = LaunchControlXL(rstate.midi)
    
    return P(
        (P(f.a.r).f(Gradient.V(f.a.r,
            hsl(nxl(20, 0.25), a=0.5),
            hsl(nxl(10, 0.45), a=0.5)))),
        (StSt("MIDI", Font.MutatorSans()
            , fontSize=20+nxl(12, 0.25)*500
            , wdth=nxl(11, 0.25)
            , wght=nxl(21)
            , tu=-250+nxl(22)*500
            , r=1
            , ro=1)
            .align(f.a.r, tv=1)
            .f(1)))