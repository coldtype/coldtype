from coldtype import *

page = Rect(1080, 1080)

font = Font("ç/ColdtypeObviously.designspace")
#font = Font("ç/MutatorSans.ttf")
#font = Font("ç/ColdtypeObviously_CompressedBlackItalic.ufo")

@renderable
async def render():
    style = Style(font, 650, fill="random", wdth=1, tu=-50, r=1, ro=1)
    return StyledString("COLDTYPE", style).fit(750).pens().align(page).f(1, 0, 0.5).understroke()