from coldtype import *
from coldtype.time.nle.ascii import AsciiTimeline

nudge = Font.Cacheable("~/Type/fonts/fonts/VCNudge2-Bold.otf")

at = AsciiTimeline(1, """
    [L                      ]
           [F                          ]
                        [H                              ]                           <
""")

@animation(timeline=at)
def officehours(f):    
    stx = Style.StretchX(0,
        L=(730*at["L"].io2(f.i, 10, "eeo"), 310),
        F=(1000*at["F"].io2(f.i-10, [11, 5], ["qeio", "eei"]), 260),
        H=(1800*at["H"].io2(f.i+20, 6, "eeio"), 250),
        )
    
    txt = (StSt("Coldtype\nOffice\nHours".upper(),
        nudge, 200, ss02=1, mods=stx, leading=20)
        .align(f.a.r)
        .collapse()
        .pen()
        .f(0))

    return DPS([
        #txt.copy().translate(5, -5).f(hsl(0.37, 1)),
        txt.f(hsl(0.75, 0.6))
    ])