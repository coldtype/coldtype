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

    def styler(g):
        return Style(fnt,
            fontSize=200,
            wght=at.ki(g.i, f.i)
                .e(1),
            wdth=at.ki(g.i+4, f.i)
                .e("qeio", 1))

    return (Glyphwise("TYPE", styler)
        .track(at.ki("tu", f.i).e(1, rng=(0, 150)))
        .align(f.a.r)
        .f(hsl(0.7, 1))
        .pmap(lambda i, p: p
            .rotate(at.ki("ro", f.i-i)
                .e(rng=(0, -360))))
        .cond(now, lambda ps: ps
            .centerOnPoint(f.a.r,
                ps[now.t.index].ambit(th=1).pc,
                interp=now.e(1))
            .scale(1+now.e(1)*2,
                point=ps[now.t.index].ambit().pc)
                ))