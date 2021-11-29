from coldtype import *
from coldtype.time.nle.ascii import AsciiTimeline

at = AsciiTimeline(2, 30, """
A   A   B   B   C   C   D    D  <
""", {
    "A": dict(grvt=0, yest=1, rotate=0),
    "B": dict(grvt=1, yest=0, rotate=0),
    "C": dict(grvt=1, yest=1, rotate=0),
    "D": dict(grvt=0, yest=0, rotate=180),
})

@animation((1080, 520), timeline=at, bg=0)
def cheee_wild(f):
    return (Glyphwise("CHEEE", lambda g: [
        Style("CheeeVariable", 270, tu=50),
        at.kf(f.i+g.i*30, easefn="eeio")])
        .f(1)
        .align(f.a.r, th=0)
        .rp().understroke(0, 8))