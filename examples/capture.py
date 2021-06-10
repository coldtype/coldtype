from coldtype import *
from coldtype.capture import read_frame
from coldtype.midi.controllers import LaunchControlXL

Style.RegisterShorthandPrefix("≈", "~/Type/fonts/fonts")
fnt = Font.Cacheable("≈/CheeeVariable.ttf")

@animation((1080, 1080), cv2caps=[0], rstate=1)
def capture_with_midi(f:Frame, rs): 
    nxl = LaunchControlXL(rs.midi)
    img = (read_frame(rs.cv2caps[0]).align(f.a.r))
    
    return DPS([
        img.a(0.5),
        (StSt("MIDI", fnt, 200+nxl(10, 0)*500,
            r=1, # reverse
            ro=1, # remove-overlap
            grvt=nxl(21, 0),
            yest=nxl(20, 0),
            tu=(1-nxl(11, 0))*-300)
            .align(f.a.r.take(0.75, "mxy"))
            .f(hsl(0.7, 1, 0.7))
            .understroke(sw=nxl(30, 0)*100))])