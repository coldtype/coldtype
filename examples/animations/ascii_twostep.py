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
def test_ascii(f):
    return (Glyphwise("TYPE", lambda g:
        Style(Font.ColdtypeObviously(), 100,
            wdth=(at.ki("a" if g.i <= 1 else "b").io(10)),
            tu=at.ki("c").io(8, r=(0, 500))))
        .align(f.a.r)
        .scale(at.ki("s").io(20)*2)
        .f(0)
        .layer(
            lambda p: p.layerv(1,
                lambda g: P()
                    .rect(g.ambit(tx=1).inset(-20))
                    .fssw(-1, 0, 2)
                    .null()),
            lambda p: P()
                .rect(p.ambit(tx=1, ty=1).inset(-50))
                .fssw(-1, 0, 2)
                ._null()))