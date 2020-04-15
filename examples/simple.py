from coldtype import *

@renderable()
def render(r):
    style = Style("assets/MutatorSans.ttf", 250, wdth=0, wght=1, tu=-350, r=1, ro=1)
    return StyledString("COLDTYPE", style).pens().align(r).f("hr", 0.8, 0.7).understroke()