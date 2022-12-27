from coldtype import *

at = AsciiTimeline(6, 30, """
                                              <
[0   ][1   ][2     ][3  ][4         ]
  [0w                                  ]
        [1w                            ]
               [2w                     ]
                      [3w              ]
                              [4w      ]
                                      [z    ]
                                      [o   ]
""")

@animation((1080, 1080), timeline=at, bg=1, render_bg=1)
def casual1(f):
    letter = at.ki(list("012345"))
    li, lidx = letter.e(find=1)
    
    z = at.ki("z")
    o = at.ki("o")

    return (Glyphwise("Dicey", lambda g:
        Style("Casual", 100
            , opsz=o.e("eeo", 1, r=(1, 0))
                if o.on()
                    else at.ki(g.i).e("eeio", 1, r=(1, 0))
            , wght=z.e("eeo", 0, r=(1, 0))
                if z.on()
                    else at.ki(f"{g.i}w").io([8, 8], "eeo")))
        .align(f.a.r)
        .centerPoint(f.a.r, (lidx, "txtyC"), i=li)
        .cond(True,
            lambda p: p
                .scale(letter.io([15, 5], r=(1,10)), pt=(lidx, "tyC"))
                .scale(z.io([10, 15], ["eeo", "eei"], r=(1, 5))),
            lambda p: p
                .scale(letter.e(r=(1,10)), pt=(lidx, "tyC"))
                .scale(z.e("eeio", r=(1, 5))))
        .f(0))

release = casual1.export("h264", loops=3)