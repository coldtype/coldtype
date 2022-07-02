from coldtype import *

at = AsciiTimeline(3, 30, """
                            <
    [ss06      ]
           [ss07        ]
""")

@animation((1400, 540), timeline=at, bg=1, render_bg=1)
def scratch(f):
    return (StSt("alter-\nnates", "SFCompactItalic", 200
        , ss06=at.ki("ss06").on()
        , ss07=at.ki("ss07").on())
        .align(f.a.r))
