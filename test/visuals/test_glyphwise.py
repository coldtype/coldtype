from coldtype import *
from coldtype.text.composer import Glyphwise
from coldtype.time.nle.ascii import AsciiTimeline

fnt = Font.Cacheable("~/Type/fonts/fonts/ObviouslyVariable.ttf")
at = AsciiTimeline(3, 30, """
                                                <
[0     ][1     ][2     ][3     ]  [ro   ]
[4         ]    [6         ]       [tu     ]
        [5         ]    [7          ]
            [slnt                     ]
""", sort=1)

@animation((1080, 1080), timeline=at, bg=hsl(0.9, 1, 0.9))
def test_glyphwise(f):
    return (Glyphwise("TYPE", lambda g:
        Style(fnt, 200,
            wght=at[g.i].e(f.i),
            wdth=at[g.i+4].e(f.i, "qeio"),
            slnt=at["slnt"].e(f.i, "seio")))
        .track(150*at["tu"].e(f.i, "eeio", 1))
        .align(f.a.r)
        .f(hsl(0.7, 1))
        .pmap(lambda i, p: p.rotate(-360*at["ro"].e(f.i-i, 0)))
        .cond(now:=at.now(f.i, 1, True, lambda m: m.index < 4), 
            lambda pens:
            (pens.center_on_point(f.a.r,
                    pens[now.index].bounds().point("C"),
                    interp=now.e(f.i))
                .scale(1+now.e(f.i)*2,
                    point=pens[now.index].bounds().point("C")))))