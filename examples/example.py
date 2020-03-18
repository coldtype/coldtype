from coldtype import Rect, StyledString, Style

page = Rect(1920, 1080)

def render():
    return StyledString("COLDTYPE", Style("ç/MutatorSans.ttf", 300, fill="random")).pens().align(page)

renders = [render]