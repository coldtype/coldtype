from coldtype.time import loop
from coldtype.test import *
from coldtype.time.nle.ascii import AsciiTimeline
from coldtype.text.composer import Glyphwise

fnt = Font.Cacheable("~/Type/fonts/fonts/CheeeVariable.ttf")
#fnt = Font.Cacheable("~/Type/fonts/fonts/Blimey-VO3-Variable.ttf")

at = AsciiTimeline(1, """
                                                         <
  [a              ]
                 [b                ]
[e                                         ]
""")

@animation(timeline=at)
def test_ascii(f):
    io = at[-1].io2(f.i, 10, "eeio")
    return (Glyphwise("ASCII", lambda i, c:
        Style(fnt, 1+200*io,
            grvt=(e:=at[i > 1].io2(f.i, 9, "eeio")),
            yest=e,
            fill=hsl(0.5+e*0.3)))
        .align(f.a.r)
        .rotate((1-io)*180))