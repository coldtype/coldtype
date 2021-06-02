from coldtype.test import *
from coldtype.capture import read_frame
from coldtype.fx.skia import phototype, precompose
from coldtype.midi.controllers import LaunchControlXL

tl = Timeline(120, fps=30)

@animation((1080, 1080), timeline=tl, cv2caps=[0, 1], composites=1, rstate=1)
def opcam8(f:Frame, rs):
    nxl = LaunchControlXL(rs.midi)
    webcam = (read_frame(rs.cv2caps[round(nxl(11, 0.5))])
        .align(f.a.r))
    if nxl(10, 0.5) > 0.5:
        return webcam
    
    return (DPS([
        DP(f.a.r).f(1),
        (webcam.ch(phototype(f.a.r,
            blur=1,
            cut=nxl(20, 0.5)*255,
            fill=0)))
        ])
        .ch(phototype(f.a.r, nxl(30, 0.5)*20,
            cutw=nxl(40, 0.5)*50,
            fill=hsl(nxl(50, 0.5)))))