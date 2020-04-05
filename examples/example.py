from coldtype import *

font = Font("ç/ColdtypeObviously.designspace")

@renderable(Rect(1500, 800))
def render(r):
    style = Style(font, 650, fill="random", wdth=1, tu=-50, r=1, ro=1)
    return StyledString("COLDTYPE", style).fit(1150).pens().align(r).f("hr0.6-0.95", "r0.5-0.7", "r0.7-0.85").understroke()