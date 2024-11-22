from coldtype import *
from coldtype.axidraw import *

@animation((120, 120), tl=(16**2, 24))
def sheet_animation(f):
    return (StSt("A", Font.MuSan(), 60, wght=f.e("eeio", 4))
        .align(f.a.r, ty=1)
        .removeOverlap())

@axidrawing()
def sheet(r):
    return sheet_animation.contactsheet(r.inset(20), 0.75)

numpad = {
    1: sheet.draw("border"),
    2: sheet.draw("grid"),
    3: sheet.draw("frames"),
}