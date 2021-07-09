from coldtype import *
from coldtype.time.nle.ascii import AsciiTimeline

nudge = Font.Cacheable("~/Type/fonts/fonts/VCNudge2-Bold.otf")

at = AsciiTimeline(1, """
                                                        <
        [L                                          ]
         [F                              ]
          [H                          ]
""")

@animation(timeline=at)
def officehours(f):
    stx = Style.StretchX(0,
        L=(730*at["L"].io2(f.i, 10, e:="eeio"), 310),
        F=(1220*at["F"].io2(f.i, 10, e), 260),
        H=(1900*at["H"].io2(f.i, 10, e), 250))
    
    txt = (StSt("Coldtype\nOffice\nHours".upper(),
        nudge, 125, ss02=1, mods=stx, leading=20)
        .f(0)
        .align(f.a.r))

    return DPS([
        (DP().roundedRect(txt.copy().ambit().inset(-50), 20, 20)
            .f(bg:=hsl(0.07, 0.8, 0.5, 0.3))),
        txt.f(hsl(0.75, 0.6)),
        (StSt("7/21/2021\n3pm Pacific".upper(),
            nudge, 70, leading=30)
            .align(f.a.r)
            .rotate(10)
            .f(1)
            .a(0))])