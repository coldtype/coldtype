from coldtype.test import *

ov = Font("assets/ColdtypeObviously.designspace")

@test((1000, 1000), rstate=1)
def test_mouse_interp(r, rs):
    ri = r.inset(100)
    sx, sy = ri.ipos(rs.mouse)
    return [
        DATPen().rect(ri).f(None).s(hsl(0.9, a=0.3)).sw(10),
        (StyledString("COLD",
            Style(ov, 250+sy*100, wdth=sx))
            .pens()
            .align(r)
            .f(0))]
