from coldtype import *
from coldtype.fx.skia import precompose

at = AsciiTimeline(1, 18, """
                                <
0       1       2       3   4
""")

@animation((1080, 1080/2), timeline=at, bg=hsl(0.6, 1, 0.7))
def pixellation(f):
    return (StSt("PIXEL", "Times", 460, tu=250)
        .f(1)
        .scale(0.5, 1)
        .align(f.a.r)
        .map(lambda i, p: p
            .ch(precompose(f.a.r
                , scale=at.ki(i).adsr([5, 25], ["qeio", "l"]
                    , r=(0.25, 0.015))))))
