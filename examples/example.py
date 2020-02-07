from coldtype import Rect, StyledString, Style

def render():
    return StyledString("COLDTYPE", Style("ç/MutatorSans.ttf", 200, fill="random")).pens().align(page)

page = Rect(1920, 1080)
renders = [
    render
]