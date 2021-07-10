from coldtype.time import loop
from coldtype.test import *
from coldtype.time.nle.ascii import AsciiTimeline
from coldtype.text.composer import Glyphwise

fnt = Font.Cacheable("~/Type/fonts/fonts/CheeeVariable.ttf")

at = AsciiTimeline(1, """
                                                              <
          [a                                 ]
                      [b                     ]
                                [c                   ]
""")

@animation((1080, 540), timeline=at)
def test_ascii(f):
    io = at.io2(f.i, 20, "eeio")
    word = (Glyphwise("ASCII", lambda i, c:
        Style(fnt, 100,
            grvt=(at[i > 1].io2(f.i, 10, "eeio")),
            yest=at["c"].io2(f.i, 8, "eeio")))
        .align(f.a.r)
        .scale(io*2))
    
    return DPS([
        DP(word.ambit(tv=1).inset(-50)).f(hsl(0.07, 1, 0.8, a=0.5)),
        word])