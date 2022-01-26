from coldtype import *
from coldtype.time.nle.ascii import AsciiTimeline

at = AsciiTimeline(3, 30, """
                                                <
[0     ][1     ][2     ][3     ]
[0w        ]    [2w        ]
        [1w        ]    [3w         ]
                                  [ro   ]
                                   [tu     ]
""")

@animation((1080, 1080), timeline=at, bg=hsl(0.9, 1, 0.9))
def choreography(f):
    letter = at.ki(list("0123"))
    li, lidx = letter.e(find=1)

    return (Glyphwise("TYPE", lambda g:
        Style(Font.MutatorSans(), 200,
            wght=at.ki(g.i).e(),
            wdth=at.ki(f"{g.i}w").e("qeio", 1)))
        .track(at.ki("tu", f.i).e(r=150))
        .align(f.a.r)
        .f(hsl(0.7, 1))
        .pmap(lambda i, p: p
            .rt(at.ki("ro", f.i-i).e("eeio", 0, r=-360)))
        .centerPoint(f.a.r, (lidx, "tvC"), i=li)
        .scale(letter.e(r=(1,2+lidx))
            , pt=(lidx, "tvC")))