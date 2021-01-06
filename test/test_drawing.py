from coldtype.test import *
from coldtype.midi.controllers import LaunchControlXL

@renderable(bg=1, rstate=1)
def draw1(r, rs):
    nxl = LaunchControlXL(rs.midi)
    contours = DATPen()
    wdth = nxl(20)*150
    angle = nxl(10)*180
    if mh := rs.mouse_history:
        for m in mh:
            for p in m:
                contours.line([p.project(angle-180, wdth), p.project(angle, wdth)])

    return (DATPenSet([
        #StyledString("P", Style(co, 1000)).pen().align(r).f(0.7),
        (DATPens([contours])
            #.s(hsl(0.9))
            #.sw(10)
            .s(1)
            .sw(15)
            #.f(1)
            .phototype(r, blur=5, cut=50, fill=0)
            -.img_opacity(0.5))]))