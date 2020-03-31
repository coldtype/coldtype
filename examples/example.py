from coldtype import Rect, StyledString, Style, Slug
from coldtype.text.reader import Font

page = Rect(1080, 1080)
#font = Font("ç/ColdtypeObviously.designspace")
#font = Font("ç/MutatorSans.ttf")
font = Font("ç/ColdtypeObviously_CompressedBlackItalic.ufo")

async def render():
    style = Style(font, 650, fill="random", wdth=1, tu=-50, r=1, ro=1)
    pens = StyledString("COLDTYPE", style).fit(700).pens().align(page).f(None).s("random").sw(2)
    pens.print_tree()
    return pens.frameSet(), pens

renders = [render]