from coldtype import *

# inspired by https://mauricemeilleur.net/truchet_tiles

rs = random_series(0, 3)
rs2 = random_series()

tr = Rect(100)
tn = 8

at = AsciiTimeline(10, 30, """
            <
[0 ]    [0 ]
""")

@animation((tr.w*tn, tr.w*tn), tl=at, bg=1)
def truchet1(f):
    def rotate(i, p):
        #row, col = i//tn, i%tn
        (p.rotate(90*int(rs[i]))
            .rotate(f.t.ki(0).ec("eeio", rng=(0, 90)))
            .f(hsl(rs2[i]))
            .blendmode(BlendMode.Cycle(11)))

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