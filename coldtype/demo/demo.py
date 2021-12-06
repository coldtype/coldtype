from coldtype import *

states = [
    dict(wdth=0, rotate=0),
    dict(wdth=1, rotate=15),
    dict(wdth=0.5, rotate=-210),
    dict(wdth=1, rotate=-25)
]

spacings = [
    dict(tu=300),
    dict(tu=80),
    dict(tu=330),
    dict(tu=150)
]

at = AsciiTimeline(2, 30, """
                                <
[0     ][1     ][2     ][3     ]
""").shift("end", -10)

@animation((1080, 1080/4), timeline=at, bg=1)
def render(f):
    state = at.kf("eeio", keyframes=states)
    spacing = at.kf("seio", keyframes=spacings)

    return (StSt("COLDTYPE", Font.ColdtypeObviously(),
        150, fill=0, **{**state, **spacing}, r=1, leading=80)
        .align(f.a.r)
        .f(0))