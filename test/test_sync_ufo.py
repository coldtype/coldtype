from coldtype import *

co = Font("assets/ColdtypeObviously_CompressedBlackItalic.ufo")
#co = Font("assets/ColdtypeObviously.designspace")

@renderable()
def hello(r):
    return StyledString("COLDTYPE", Style(co, 500, wdth=0, tu=0)).pens().align(r, tv=1).f(hsl(0.5))