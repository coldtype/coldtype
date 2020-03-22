from coldtype import Rect, StyledString, Style
from coldtype.text.reader import FontGoggle

page = Rect(1080, 1080)

font = FontGoggle("ç/MutatorSans.ttf")

def render():
    pens = StyledString("COLDTYPE", Style(font, 250, fill="random", wght=1, tu=-250, r=1)).pens().align(page).understroke(s=1)
    pens.print_tree()
    return pens

renders = [render]