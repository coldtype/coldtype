from coldtype import *

font = Font("ç/ColdtypeObviously.designspace")

@renderable(rect=(1000, 300))
def test_kern_pairs(r):
    return StyledString("CLD", Style(font, 300, rotate=-10, kp={"C/L":20, "L/D":45})).pens().align(r)