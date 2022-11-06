from coldtype import *
from random import Random

# inspired by https://mauricemeilleur.net/truchet_tiles

rs = random_series(0, 3, seed=4)
rs2 = random_series()

tr = Rect(100)
tn = 8

at = AsciiTimeline(4, 30, """
<
[0 ]                                [1 ]
  [1    ]           [0  ]     
             [2  ]                  [2  ]
                     [3 ]             [3  ]
                      [4 ]         [4 ]
            [5         ]                [5  ]
             [6  ]                    [6  ]
""")

rnd = Random()
rnd.seed(4)
ridxs = list(range(0, tn*tn))
rnd.shuffle(ridxs)

@animation((tr.w*tn, tr.w*tn), tl=at, bg=1)
def truchet1(f):
    def rotate(i, p):
        ri = ridxs[i]
        (p.rotate(90*int(rs[i]))
            .rotate(f.t.ki(str(ri)).ec("beo", (0, 90))))

    return (P(tr)
        .difference(P()
            .append(P().oval(tr).t(tr.w/2))
            .append(P().oval(tr).t(-tr.w/2)))
        .f(0)
        .data(frame=tr)
        .layer(tn)
        .spread()
        .layer(tn)
        .stack()
        .mapv(rotate))