from coldtype import *
from coldtype.time.nle.ascii import AsciiTimeline

at = AsciiTimeline(1, """
                                                              <
            [a                               ]
                      [b                     ]
                                [c                        ]
""")

@animation((1080, 540), timeline=at, bg=1)
def test_ascii(f):
    return (Glyphwise("TYPE", lambda g:
        Style(Font.ColdtypeObviously(), 100,
            wdth=(at.ki("a" if g.i <= 1 else "b", f.i).io(10)),
            tu=at.ki("c", f.i).io(8, rng=(0, 500))
            ))
        .align(f.a.r)
        .scale(f.io(20)*2)
        .f(0)
        .layer(1,
            lambda p: P()
                .rect(p.ambit(tv=1).inset(-50))
                .fssw(-1, 0, 2)))