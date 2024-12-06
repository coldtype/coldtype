from coldtype import *
from coldtype.blender import *
from random import Random

# inspired by https://mauricemeilleur.net/truchet_tiles

rs = random_series(0, 3, seed=0)
rs2 = random_series()
rs3 = random_series(0.5, 3.5)

tn = 8

at = AsciiTimeline(10, 30, """
<
[0 ]                           [1 ]
  [1    ]           [0  ]
             [2  ]             [2  ]
                     [3 ]        [3  ]
                      [4 ]    [4 ]
            [5         ]           [5  ]   <
             [6  ]               [6  ]
    [7  ]                [7  ]
      [8  ]                     [8  ]
        [9  ]      [9  ]
""")

spins = []
for t in at.timeables:
    spins.append(Timeable(t.start+6, t.end-6, name=f"{t.name}_spin"))

t2 = Timeline(timeables=[*at.timeables, *spins])

rnd = Random()
rnd.seed(4)
ridxs = list(range(0, tn*tn))
rnd.shuffle(ridxs)

@b3d_runnable()
def setup(bw:BpyWorld):
    (bw.deletePrevious(materials=False))

@b3d_animation(Rect(1000), tl=at, bg=None)
def truchet1(f):
    t2.hold(f.i)

    def rotate(i, p):
        ri = ridxs[i]//6
        (p.rotate(90*int(rs[i]))
            .rotate(t2.ki(f"{ri}_spin")
                .ec("eeio", (0, 90)))
            .ch(b3d(lambda bp: bp
                .extrude(0.25)
                .locate(z=t2.ki(f"{ri}")
                    .e("eeio", rng=(0, rs3[i]))))))
    
    s = Scaffold(f.a.r).numeric_grid(tn)

    return (P(tr:=s[0].r.inset(0.05, 0.05))
        .difference(P()
            .append(P().oval(tr).t(tr.w/2))
            .append(P().oval(tr).t(-tr.w/2)))
        .f(0)
        .replicate(s.cells())
        .map(rotate))