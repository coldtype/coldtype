from coldtype.test import *

@test((1000, 1000), rstate=1)
def stub(r, rs):
    out = DATPenSet()
    out += (DATPen()
        .oval(r.inset(50))
        .f(0.8))
    if box := rs.shape_selection():
        if rs.mouse_down:
            box.f(None).s(hsl(0.6, s=1)).sw(5)
        else:
            box.f(hsl(0.7, a=0.2))
        out += box
    return out