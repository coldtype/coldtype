from coldtype import *

co = Font("assets/ColdtypeObviously_BlackItalic.ufo")

@renderable()
def hello(r):
    return StyledString("C", Style(co, 1000)).pen().align(r, tv=1).f(hsl(0.5))