from coldtype.test import *
from coldtype.midi.controllers import LaunchControlXL

@test((1000, 300))
def test_system_font(r):
    return DATText("Hello, world!", Style("Times", 100, load_font=0, fill=0), r.offset(100, 100))

@test((1000, 300), rstate=1)
def test_return_string(r, rs):
    ri = r.inset(30)
    sx, sy = ri.ipos(rs.mouse, (0, 0))

    rt = r.take(80, "mdy").take(0.8, "mdx")
    style = Style(co, 150, wdth=sx, fill=(0, 0.5))

    return DATPens([
        (StyledString("COLDTYPE", style)
            .pens()
            .align(rt, "mnx")
            .translate(-5, 17)
            .f(hsl(0.9))),
        (DATText("COLDTYPE", style, rt)
            .translate(0, 0))])

@test((1000, 300), rstate=1, solo=0)
def test_midi(r, rs):
    nxl = LaunchControlXL(rs.midi)
    style = Style(co, 250, wdth=nxl(10, 0), fill=hsl(nxl(11, 0)))
    return DATText("CLDTYP", style, r.inset(50))