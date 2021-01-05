from coldtype.test import *
from time import sleep

tmp_angle = 0 # "tmp" b/c it will be set back to 0 when the program restarts

@test((1000, 1000), rstate=1)
def test_select(r, rs):
    dps = DATPens()
    txts = "COLDTYPE"
    selection = None

    for idx, c in enumerate(r.inset(10).subdivide_with_leading(len(txts), 10, "mxy")):
        rf = hsl(idx/len(txts)*0.3+0.5)
        if rs.mouse and rs.mouse.inside(c):
            dps += DATPen().rect(c).f(0)
            selection = txts[idx]
        else:
            dps += DATPen().rect(c).f(rf)
        dps += (StyledString(txts[idx],
            Style(co, 100))
            .pen()
            .align(c.subdivide(len(txts), "mnx")[idx])
            .f(rf.lighter(0.1)))

    if selection:
        rs.request = selection
    
    return dps