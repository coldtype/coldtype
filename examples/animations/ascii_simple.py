from coldtype import *
from coldtype.time.nle.ascii import AsciiTimeline

at = AsciiTimeline(4, """
                                <
[B   ]    [B       ]
            [A          ]
                [C         ]
                    [wght     ]
""")

@animation((1080, 540), timeline=at)
def ascii(f):
    return (Glyphwise("ABC", lambda g:
        Style(Font.MutatorSans(), 250,
            wdth=at.ki(g.c).io(8),
            wght=at.ki("wght").io(10)))
        .align(f.a.r, tv=1))
