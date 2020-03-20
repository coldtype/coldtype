from coldtype import Rect, StyledString, Style
from coldtype.text.reader import FontGoggle

page = Rect(1080, 1080)

def render():
    font = FontGoggle("≈/ObviouslyVariable.ttf")
    style = Style(font, 1000, fill=0, slnt=1, wdth=0.25, wght=1, ss01=1)
    print(style.features)
    return []
    return StyledString("S", Style("≈/ObviouslyVariable.ttf", 1000, fill=0, slnt=0, wdth=0.25, wght=1, ss01=1)).pens().align(page)
    return StyledString("COLDTYPE", Style("ç/MutatorSans.ttf", 300, fill="random")).pens().align(page)

renders = [render]