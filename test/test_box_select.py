from coldtype.test import *

@test((1000, 1000), rstate=1)
def stub(r, rs):
    out = DATPenSet()
    out += (DATPen()
        .oval(r.inset(50))
        .f(0.8))
    if br := rs.box_selection():
        out += DATPen().rect(br).f(None).s(0).sw(10)
    return out