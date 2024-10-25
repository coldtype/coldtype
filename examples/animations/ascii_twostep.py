from coldtype import *
from coldtype.timing.nle.ascii import AsciiTimeline

at = AsciiTimeline(1, """
                                                              <
    [s                                                    ]
            [a                               ]
                      [b                     ]
                                [c                        ]
""")

@animation((1080, 540), timeline=at, bg=1, render_bg=1)
def twostep(f):
    return (Glyphwise("COLD\nTYPE", lambda g:
        Style(Font.ColdtypeObviously(), 100,
            wdth=(at.ki("a" if g.l < 1 else "b").io(10)),
            tu=at.ki("c").io(8, r=(0, 500))))
        .lead(10)
        .xalign(f.a.r)
        .align(f.a.r)
        .scale(at.ki("s").io(20)*2)
        .f(0)
        .layer(1,
            lambda p: P()
                .rect(p.ambit(tx=1, ty=1).inset(-50))
                .fssw(-1, 0, 2)
                .___null()))