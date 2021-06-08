from coldtype import *
from coldtype.text.composer import Glyphwise
from coldtype.time.nle.ascii import AsciiTimeline

fnt = Font.Cacheable("~/Type/fonts/fonts/ObviouslyVariable.ttf")
at = AsciiTimeline(4, 30, """
                                                <
[0     ][1     ][2     ][3     ]   [ro   ]
[4         ]    [6       ]         [tu       ]
        [5         ]    [7           ]
            [slnt                    ]
""", sort=1)

@animation((1080, 1080), timeline=at, bg=hsl(0.9, 1, 0.9))
def test_glyphwise(f):
    nows = at.now(f.i, 1)
    now = nows[0] if nows else None

    return (Glyphwise("TYPE",
        lambda i, c: Style(fnt, 300,
            wght=at[i].e(f.i),
            wdth=at[i+4].e(f.i, "ceio"),
            slnt=at["slnt"].e(f.i, "seio")))
        .track(150*at["tu"].e(f.i, "eeio", 1))
        .align(f.a.r)
        .f(hsl(0.7, 1))
        .pmap(lambda _, p: p.rotate(-360*at["ro"].e(f.i, 0)))
        .cond(True and now and now.index < 4, lambda pens:
            (pens.center_on_point(f.a.r,
                    pens[now.index].bounds().point("C"),
                    interp=now.e(f.i))
                .scale(1+now.e(f.i)*1.5,
                    point=pens[now.index].bounds().point("C")))))