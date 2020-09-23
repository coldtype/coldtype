from coldtype import *

co = Font("assets/ColdtypeObviously.designspace")

@renderable()
def scratch(r):
    ss = (StyledString("COLDTYPE",
        Style(co, 150, tu=-50, ro=1, r=1, rotate=-10))
        .pens()
        .align(r)
        .rotate(15)
        .translate(0, 10)
        .f(hsl(0.85))
        #.s(0).sw(2)
        .understroke(sw=20)
        )
    
    return DATPenSet([ss])