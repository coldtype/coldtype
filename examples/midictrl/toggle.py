from coldtype import *
from coldtype.midi.controllers import LaunchControlXL

@animation((1080, 1080), bg=1, rstate=1)
def render(f, rstate):
    nxl = LaunchControlXL(rstate.midi)
    toggle_state = nxl(10, 0) > 0.5
    
    return (StSt(
        "ON" if toggle_state else "OFF"
        , font=Font.MutatorSans()
        , fontSize=500 if toggle_state else 100)
        .align(f.a.r))