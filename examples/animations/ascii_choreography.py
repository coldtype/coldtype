from coldtype import *
from coldtype.time.nle.ascii import AsciiTimeline

fnt = Font.MutatorSans()

at = AsciiTimeline(3, 30, """
                                                <
[0     ][1     ][2     ][3     ]
[0w        ]    [2w        ]
        [1w        ]    [3w         ]
                                  [ro   ]
                                   [tu     ]
""")

@animation((1080, 1080)
    , timeline=at
    , bg=hsl(0.9, 1, 0.9))
def choreography(f):
    letter = at[list("0123"), f.i]
    li, lidx = letter.e(1, find=1)

    return (Glyphwise("TYPE", lambda g:
        Style(fnt, 200,
            wght=at.ki(f"{g.i}", f.i).e(1),
            wdth=at.ki(f"{g.i}w", f.i).e("qeio", 1)))
        .track(at.ki("tu", f.i).e(1, r=150))
        .align(f.a.r)
        .f(hsl(0.7, 1))
        .pmap(ι,λ.rt(at.ki("ro", f.i-ι).e(r=-360)))
        .centerPoint(f.a.r, (lidx, "tvC"), i=li)
        .scale(letter.e(1, r=(1,2+lidx))
            , pt=(lidx, "tvC")))