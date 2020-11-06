from coldtype.test import *

tmp_angle = 0 # "tmp" b/c it will be set back to 0 when the program restarts

@test((1000, 1000), rstate=1)
def test_oval(r, rs):
    global tmp_angle

    if rs.mouse:
        rm = Rect.FromCenter(rs.mouse, 100)
    else:
        rm = r
    
    if rs.mods.super:
        tmp_angle += 33
    
    return (StyledString("COLDTYPE",
        Style(co, 300, wdth=0))
        .pen()
        .align(rm)
        .rotate(tmp_angle)
        .f(hsl(random(), s=0.75)))