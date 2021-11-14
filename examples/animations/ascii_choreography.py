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
    es = at[(0, 1, 2, 3), f.i]
    ei, eidx = es.e(1, find=1)

    def styler(g):
        return Style(fnt,
            fontSize=200, 
            wght=at.ki(g.i, f.i)
                .e(1),
            wdth=at.ki(g.i+4, f.i)
                .e("qeio", 1))

    return (Glyphwise("TYPE", styler)
        .track(at.ki("tu", f.i).e(1, ŋ=150))
        .align(f.a.r)
        .f(hsl(0.7, 1))
        .pmap(lambda i, p: p
            .rotate(at.ki("ro", f.i-i)
                .e(ŋ=-360)))
        .centerOnPoint(f.a.r, (eidx, "C"), interp=ei)
        .scale(es.e(1, ŋ=(1,3)), ṗ=(eidx, "C")))