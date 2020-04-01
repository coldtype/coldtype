from coldtype import *

page = Rect(1080, 1080)

@renderable
async def render():
    style = Style("ç/MutatorSans.ttf", 250, fill="random", wdth=0, wght=1, tu=-350, r=1, ro=1)
    return StyledString("COLDTYPE", style).pens().align(page).f(0.5, 0, 1).understroke()