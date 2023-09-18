# a good invocation: coldtype examples/capture.py -wpass -wt -wo 0.85 -wp NW -ps 2

from coldtype import *
from coldtype.capture import read_frame
from coldtype.midi.controllers import LaunchControlXL

Style.RegisterShorthandPrefix("≈", "~/Type/fonts/fonts")
fnt = Font.Cacheable("≈/CheeeVariable.ttf")

@animation((1080, 1080), cv2caps=[0], rstate=1)
def capture_with_midi(f:Frame, rs): 
    nxl = LaunchControlXL(rs.midi)
    img = (read_frame(rs.cv2caps[0]).align(f.a.r))
    
    return P(
        img.a(0.25),
        (StSt("CTRL", fnt, 200+nxl(10, 0)*500,
            r=1, # reverse
            ro=1, # remove-overlap
            rotate=nxl(60, 0)*360,
            grvt=nxl(40, 0),
            yest=nxl(20, 0),
            tu=(1-nxl(30, 0))*-650)
            .align(f.a.r.take(0.75, "mxy"))
            .f(hsl(0.7, 1, 0.7))
            .understroke(sw=nxl(50, 0)*100)))