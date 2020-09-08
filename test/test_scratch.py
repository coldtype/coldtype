from coldtype import *

co = Font("assets/ColdtypeObviously.designspace")

@renderable()
def scratch(r):
    return (StyledString("COLDTYPE",
        Style(co, 150, tu=100, ro=1, r=1))
        .pens()
        .align(r)
        .rotate(15)
        .translate(0, 10)
        .f(hsl(0.9, s=1, l=0.6))
        .understroke(sw=20))