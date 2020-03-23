from coldtype import Rect, StyledString, Style, Slug
from coldtype.text.reader import FontGoggle

page = Rect(1080, 1080)

font = FontGoggle("ç/MutatorSans.ttf")
#font = FontGoggle("≈/Hershey-TriplexGothicEnglish.ufo")

def render():
    pens = Slug("COLDTYPE", Style(font, 500, fill="random", wght=1, wdth=1, tu=-250, r=1, ro=1)).fit(500).pens().align(page).f(None).s("random")
    #pens.print_tree()
    return pens

renders = [render]