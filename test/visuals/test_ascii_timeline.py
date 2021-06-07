from coldtype.time import loop
from coldtype.test import *
from coldtype.time.nle.ascii import AsciiTimeline
from coldtype.text.composer import Glyphwise

at = AsciiTimeline(2, """
                            |
[a          ]
        [b          ]
                [c          ]
            ]           [d      
""")

@animation(timeline=at)
def test_ascii(f):
    return (Glyphwise("TYPE", lambda i, c:
        Style(co, 300, wdth=f.te(i, "eeio", 1)))
        .align(f.a.r)
        .f(hsl(0.65)))