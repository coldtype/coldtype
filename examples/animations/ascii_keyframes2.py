from coldtype import *
from coldtype.css import *

r = Rect(1080)

at = AsciiTimeline(1, """
                                            <
                ~i                   ~o
    A        A      B            B
    C     C            D        D
                ~x                   ~y
""")

r1s = dict(
    keyframes={
        "A": dict(r1=r.take(200, "SW")),
        "B": dict(r1=r.take(300, "NE"))},
    eases={"i": "eeo", "o": "eei"})

r2s = dict(
    keyframes={
        "C": dict(r2=r.take(300, "NW"), f=hsl(0)),
        "D": dict(r2=r.take(200, "SE"), f=hsl(0.1))},
    eases={"x": "seio", "y": "seio"})

@animation(r, tl=at, bg=0)
def kf(f):
    r1 = f.t.kf(**r1s)
    r2 = f.t.kf(**r2s)
    return P(r1["r1"]).f(1) + P(r2["r2"]).f(r2["f"])