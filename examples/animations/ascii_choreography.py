from coldtype import *
from coldtype.time.nle.ascii import AsciiTimeline

fnt = Font.MutatorSans()

at = AsciiTimeline(3, 30, """
                                                <
[0     ][1     ][2     ][3     ]  [ro   ]
[4         ]    [6         ]       [tu     ]
        [5         ]    [7          ]
            [slnt                          ]
""", sort=1)

@animation((1080, 1080), timeline=at, bg=hsl(0.9, 1, 0.9))
def choreography(f):
    now = at.now(f.i, 1, True, lambda m: m.index < 4)

    return (Glyphwise("TYPE", lambda g:
        Style(fnt, 200,
            wght=at[g.i].e(f.i),
            wdth=at[g.i+4].e(f.i, "qeio")))
        .track(at["tu"].e(f.i, "eeio", 1, rng=(0, 150)))
        .align(f.a.r)
        .skew(at["slnt"].e(f.i, "seio", rng=(0, 0.2)), 0)
        .f(hsl(0.7, 1))
        .pmap(lambda i, p: p.rotate(at["ro"].e(f.i-i, 0, rng=(0, -360))))
        .cond(now, lambda ps: ps
            .centerOnPoint(f.a.r,
                ps[now.index].ambit().pc,
                interp=now.e(f.i))
            .scale(1+now.e(f.i)*2,
                point=ps[now.index].ambit().pc)))