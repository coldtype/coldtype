from coldtype import Rect, StyledString, Style, Slug
from coldtype.text.reader import Font

page = Rect(1080, 1080)

async def render():
    #font = Font("ç/MutatorSans.ttf")
    #font = Font("ç/ColdtypeObviously_CompressedBlackItalic.ufo")
    font = Font("ç/ColdtypeObviously.designspace")
    await font.load()
    style = Style(font, 500, fill="random", wdth=1, tu=-50, r=1, ro=1)
    pens = StyledString("COLDTYPE", style).fit(700).pens().align(page).f(None).s("random").sw(2)
    #pens.print_tree()
    return pens.frameSet(), pens

renders = [render]