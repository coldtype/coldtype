from coldtype import *
from coldtype.time.nle.ascii import AsciiTimeline

fnt = Font.ColdtypeObviously()

at = AsciiTimeline(1, """
                                                              <
          [a                                 ]
                      [b                     ]
                                [c                   ]
""")

@animation((1080, 540), timeline=at, bg=1)
def test_ascii(f):
    io = at.io2(f.i, 20, "eeio")
    word = (Glyphwise("TYPE", lambda g:
        Style(fnt, 100,
            wdth=(at[g.i > 1].io2(f.i, 10, "eeio")),
            tu=at.ki("c", f.i).io(8, rng=(100, 500))))
        .align(f.a.r)
        .scale(io*2))
    
    return PS([
        P(word.ambit(tv=1).inset(-50)).fssw(-1, 0, 2),
        word.f(0)])