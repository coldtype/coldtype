from coldtype import *
from coldtype.timing.nle.ascii import AsciiTimeline

states = {
    "A": dict(wdth=0, wght=1, rotate=360),
    "B": dict(wdth=1, wght=0, rotate=0),
    "C": dict(wdth=1, wght=1, rotate=0),
    "D": dict(wdth=0, wght=0, rotate=180),
}

at = AsciiTimeline(2, 30, """
                                <
[A     ][B     ][C     ][D     ]
""", states).shift("end", -8)

@animation((1080, 520), timeline=at, bg=0)
def cheee_wild(f):
    return (Glyphwise("COLD", lambda g: [
            Style(Font.MuSan(), 270, tu=50, ty=1),
            at.kf("eeio", f.i-g.i*10)
        ])
        .fssw(1, 0, 8, 1)
        .align(f.a.r, tx=0)
        .reverse())