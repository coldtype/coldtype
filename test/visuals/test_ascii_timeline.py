from coldtype.test import *
from coldtype.time.ascii import AsciiTimeline
from coldtype.text.composer import Glyphwise

at = AsciiTimeline(2, """
                                    |
[a          ]
        [b          ]
                [c          ]
                        [d          ]
""")

@animation(timeline=at)
def test_ascii(f):
    return (Glyphwise("TYPE", lambda i, c:
        Style(co, 300, wdth=f.ce(i, "eeio", 1)))
        .align(f.a.r)
        .f(hsl(0.65)))