from coldtype import *
from coldtype.time.nle.ascii import AsciiTimeline

fnt = Font.Find("CheeeV")

at = AsciiTimeline(1, """
                                                              <
          [a                                 ]
                      [b                     ]
                                [c                   ]
""")

@animation((1080, 540), timeline=at, bg=1)
def test_ascii(f):
    io = at.io2(f.i, 20, "eeio")
    word = (Glyphwise("ASCII", lambda g:
        Style(fnt, 100,
            grvt=(at[g.i > 1].io2(f.i, 10, "eeio")),
            yest=at["c"].io2(f.i, 8, "eeio")))
        .align(f.a.r)
        .scale(io*2))
    
    return PS([
        P(word.ambit(tv=1).inset(-50)).fssw(-1, 0, 2),
        word.f(0)])