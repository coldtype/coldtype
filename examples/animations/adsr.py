from coldtype import *
from coldtype.timing.nle.ascii import AsciiTimeline

at = AsciiTimeline(2, 30, """
                               <
[0       ]
    [1   ]
                [2 ]
                        [3 ]
            snare
""")

@animation((1080, 1080), timeline=at, bg=1, render_bg=1)
def adsr(f):
    # line1 is a "standard" Glyphwise application
    # where the position of the letters is constantly
    # changing, since the variations are changing

    line1 = (Glyphwise("COLD", lambda g:
        Style(Font.MutatorSans(), 350
            , wght=at.ki(f"{g.i}").adsr([5, 10], ["sei", "ceo"])
            , wdth=at.ki(f"{g.i}").adsr([5, 50], ["eei", "eeo"])))
        .align(f.a.r.take(0.5, "N"), tx=1))
    
    # line2 is non-standard, in that two values are
    # returned in the Glyphwise lambda: a "base" style
    # and a dict of modifications, so that the base
    # style is used to position the letters, and then
    # the modifications change the letters without
    # repositioning them
    
    line2 = (Glyphwise("TYPE", lambda g:
        [Style(Font.MutatorSans(), 350), dict(
            wght=at.ki(f"{g.i}").adsr([5, 30], ["sei", "ceio"], dv=1, rs=1),
            wdth=at.ki(f"{g.i}").adsr([5, 30], ["eei", "eeio"], dv=0.25, rs=1))])
        .align(f.a.r.take(0.5, "S"), tx=0)
        .removeOverlap())
    
    # now we can put them together
    # and add a center line

    return (P(line1, line2)
        .append(P(f.a.r
            .take(at
                .ki("snare")
                .adsr(rng=(4, 100)), "CY")
            .inset(-20, 0)))
        .fssw(-1, 0, 2))