from coldtype.test import *

@test((1000, 1000), rstate=1)
def test_oval(r, rs):
    if rs.mouse:
        rm = Rect.FromCenter(rs.mouse, 100)
    else:
        rm = r.take(100, "mdx").square()
    
    return (StyledString("COLDTYPE",
        Style(co, 300, wdth=0))
        .pen()
        .align(rm)
        .rotate(180 if rs.mods.super else 0)
        .f(hsl(random(), s=0.75)))