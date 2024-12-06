from coldtype import *
from coldtype.fx.skia import phototype

# inspired by https://mauricemeilleur.net/truchet_tiles

at = AsciiTimeline(8, 30, """
                            <
[0 ]        [0 ]  
[1  ]          [1  ]
[2 ]              [2 ]  
""")

eases = ["beo", "eeo", "ceo"]
colors = [hsl(0.17, 0.8), hsl(0.6, 0.8), hsl(0.95, 0.8)]

rs = random_series(0, 3)
rs2 = random_series()


@animation(Rect(1000, 1000), tl=at, bg=0)
def truchet1(f):
    s = Scaffold(f.a.r).numeric_grid(8)

    def rotate(i, p):
        (p.rotate(90*int(rs[i])) # initial
            .rotate(f.t.ki(i%3).ec(eases[i%3], rng=(0, 90))))
    
    return (P(cr:=s[0].r)
        .difference(P().oval(cr).t(+cr.w/2).outline(1))
        .difference(P().oval(cr).t(-cr.w/2).outline(1))
        .xor(P(cr))
        .f(1)
        .replicate(s.cells())
        .map(rotate)
        .ch(phototype(f.a.r, blur=5, cut=20, cutw=6)))


def release(passes):
    from coldtype.renderable.animation import gifski
    gifski(truchet1, passes)
    print("/release")