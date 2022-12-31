from coldtype import *
from coldtype.axidraw import *

@animation((200, 200), tl=(8**2, 24))
def sheet_animation(f):
    return (StSt("A", Font.MuSan(), 100, wght=f.e("l", 0))
        .align(f.a.r, ty=1)
        .removeOverlap())

@axidrawing()
def sheet(r):
    return sheet_animation.contactsheet(r.inset(150), 0.75)

numpad = {
    1: sheet.draw("border"),
    2: sheet.draw("grid"),
    3: sheet.draw("frames"),
}