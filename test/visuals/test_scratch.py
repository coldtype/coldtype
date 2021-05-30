from coldtype import *

co = Font("assets/ColdtypeObviously.designspace")

@renderable()
def scratch(r):
    return (StyledString("COLDTYPE",
        Style(co, 150, tu=-100, ro=1, r=1, rotate=-10))
        .pens()
        .align(r)
        .rotate(5)
        .translate(0, 10)
        .f(hsl(0.45))
        .understroke(sw=20))