from coldtype import Rect, StyledString, Style, Slug
from coldtype.text.reader import Font

page = Rect(1080, 1080)
font = Font("ç/MutatorSans.ttf")

async def render():
    style = Style("ç/MutatorSans.ttf", 250, fill="random", wdth=0, wght=1, tu=-350, r=1, ro=1)
    pens = StyledString("COLDTYPE", style).pens().align(page).f(0.5, 0, 1).understroke()
    #pens.print_tree()
    return pens

renders = [render]