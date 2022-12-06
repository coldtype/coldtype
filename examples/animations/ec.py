from coldtype import *

at = AsciiTimeline(2, """
                                            <
[A    ]   [A  ]     [A        ]     [A  ]
            [B              ]
""")

@animation((540, 540), tl=at)
def scratch(f):
    return (StSt("I", Font.MuSan(), 300
        , wdth=f.t.ki("B").e("eeio")
        )
        .align(f.a.r, ty=0)
        .unframe()
        .rotate(f.t.ki("A").ec("eeio", rng=(0, 90)))
        .f(0))
