from coldtype import *

at = AsciiTimeline(2, 30, """
                                        <
    a        a          b        b
        [left                ]
""")

@animation((1080, 260), tl=at)
def scratch(f):
    a = (StSt("NICE", "ObviouslyV", 250)
        .align(f.a.r.inset(50), "W"))

    b = (StSt("NICE", "ObviouslyV", 250, slnt=1)
        .align(f.a.r.inset(50), "E"))

    left = at.ki("left").on()
    out = (P().enumerate(a, lambda x: x.el
        .copy()
        .interpolate(
            at.kf(keyframes=dict(a=0, b=1)
                , offset=x.i*2 if left else (len(a)-x.i)*2),
            b[x.i].copy())))
    
    return P(a, b, out)