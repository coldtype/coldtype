from coldtype import *
from coldtype.time.nle.ascii import AsciiTimeline

nudge = Font.Cacheable("~/Type/fonts/fonts/VCNudge2-Bold.otf")

at = AsciiTimeline(1, """
                                                        <
        [L                                   ]
                     [F                              ]
               [H                 ]             
""")

@animation(timeline=at)
def officehours(f):
    stx = Style.StretchX(0,
        L=(730*at["L"].io2(f.i, 10, e:=["eeo", "eeio"]), 310),
        F=(1220*at["F"].io2(f.i, 10, ["eei", "eeo"]), 260),
        H=(1900*at["H"].io2(f.i, 10, e), 250))
    
    txt = (StSt("Coldtype\nOffice\nHours".upper(),
        nudge, 125, ss02=1, mods=stx, leading=20)
        .f(1)
        .align(f.a.r))
    
    bg = (DP(txt.copy().ambit().inset(-50))
            .f(hsl(0.35, 0.8, 0.3)))

    # after bg, so it doesn't effect bounds 
    txt.index([0, 2], lambda p: p.rotate(f.e(0, cyclic=0, rng=(0, 360))))

    return DPS([
        bg.copy().translate(5, -5).f(0),
        bg,
        txt])