from coldtype import *
from coldtype.timing.nle.ascii import AsciiTimeline

at = AsciiTimeline(4, """
                                <
[1   ]    [1       ]
            [0          ]
                [2         ]
                    [wght     ]
""")

@animation((1080, 540), timeline=at)
def ascii(f):
    return (Glyphwise("AAA", lambda g:
        Style(Font.MutatorSans(), 120,
            wdth=at.ki(g.i).io(8),
            wght=at.ki("wght").io(10)))
        .align(f.a.r, ty=1)
        .mapv(lambda i, p: p
            .scale(at.ki(i).io(8, r=(1, 1.35)))))
