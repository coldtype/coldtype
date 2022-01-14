from coldtype import *
from coldtype.time.nle.ascii import AsciiTimeline

states = {
    "A": dict(grvt=0, yest=1, rotate=0),
    "B": dict(grvt=1, yest=0, rotate=0),
    "C": dict(grvt=1, yest=1, rotate=0),
    "D": dict(grvt=0, yest=0, rotate=180),
}

at = AsciiTimeline(2, 30, """
                                <
[A     ][B     ][C     ][D     ]
""", states).shift("end", -8)

@animation((1080, 520), timeline=at, bg=0)
def cheee_wild(f):
    return (Glyphwise("CHEEE", lambda g: [
        Style("CheeeVariable", 270, tu=50),
        at.kf("eeio", f.i-g.i*10)])
        .fssw(1, 0, 8, 1)
        .align(f.a.r, th=0)
        .reverse())