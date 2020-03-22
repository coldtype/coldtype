from coldtype import Rect, StyledString, Style, Slug
from coldtype.text.reader import FontGoggle

page = Rect(1080, 1080)

font = FontGoggle("ç/MutatorSans.ttf")

def render():
    pens = Slug("COLDTYPE", Style(font, 250, fill="random", wght=1, wdth=1, tu=-250, r=1)).fit(500).pens().align(page).understroke(s=1)
    pens.print_tree()
    return pens

renders = [render]