from coldtype.test import *
from coldtype.midi.controllers import LaunchControlXL

swear = Font.Cacheable("~/Type/fonts/fonts/SwearRomanVariable.ttf")


@renderable(bg=1, rstate=1)
def draw1(r, rs):
    nxl = LaunchControlXL(rs.midi)
    current = DATPen()
    strokes = DATPen()
    wdth = nxl(20)*150
    angle = nxl(10)*180

    def draw_item(to, item):
        if item:
            p = item.position
            angle = LaunchControlXL(item.midi)(10)*-90-90
            to.line([p.project(angle-180, wdth), p.project(angle, wdth)])

    for t, items in rs.input_history.strokes(lambda t, xs: t == "down" and len(xs) > 1):
        for item in items:
            draw_item(strokes, item)
    
    draw_item(current, rs.input_history.last())

    editing = rs.keylayer == Keylayer.Editing

    return (DATPenSet([
        DATPen().rect(r.inset(5)).f(None).s(0).sw(5) if editing else DATPen().rect(r).f(1),
        #StyledString("a", Style(swear, 1000, wght=0.5)).pen().align(r).f(hsl(0.5)),
        current.s(0.5).sw(10),
        (DATPens([strokes])
            #.s(hsl(0.9))
            #.sw(10)
            .s(hsl(0.7) if editing else 0)
            .sw(15)
            #.f(1)
            .color_phototype(r, blur=5, cut=190)
            .img_opacity(0.5 if editing else 1))]))