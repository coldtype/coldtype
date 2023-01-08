from coldtype import *
from coldtype.timing.nle.ascii import AsciiTimeline

at = AsciiTimeline(1, """
                                                                <
        [L                                   ]
                    [Er             ]
                     [F                                     ]
               [H                 ]             
""")

@animation(timeline=at)
def officehours(f):
    stx = Style.StretchX(0,
        L=(730*at.ki("L").io(10, "eeio"), 210),
        F=(1220*at.ki("F").io(10, ["qeio", "eleio"]), 260),
        H=(1900*at.ki("H").io(10, "ceio"), 250))
    
    txt = (StSt("Coldtype\nOffice\nHours".upper()
        , ["MDNichrome.*Dark", Font.MutatorSans()]
        , fontSize=125
        , ss03=1
        , mods=stx
        , leading=20)
        .f(1)
        .xalign(f.a.r)
        .align(f.a.r)
        .t(0, 150))

    bg = (P(txt.ambit().inset(-50))
            .f(hsl(0.35, 0.8, 0.3)))

    # after bg, so it doesn't effect bounds 
    txt.index([0, -1], lambda p: p
        .rotate(at.ki("Er").e("ceio", 0, r=(0, -360*2))))
    
    date = (StSt("X/X, XX:00 UTC", "MDNichrome.*R", 80)
        .align(f.a.r.take(0.3, "S")))

    return P(
        bg.copy().translate(5, -5).f(0),
        bg,
        txt,
        P(date.ambit().inset(-20)).f(0),
        date.f(1))