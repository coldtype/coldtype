from coldtype import *

# inspired by https://mauricemeilleur.net/truchet_tiles

rs = random_series(0, 3)
rs2 = random_series()

tr = Rect(100)
tn = 8

at = AsciiTimeline(8, 30, """
                            <
[0 ]        [0 ]  
[1  ]          [1  ]
[2 ]              [2 ]  
""")

eases = ["beo", "eeo", "ceo"]
colors = [hsl(0.17, 0.8), hsl(0.6, 0.8), hsl(0.95, 0.8)]

@animation((tr.w*tn, tr.w*tn), tl=at, bg=0)
def truchet1(f):
    def rotate(i, p):
        #row, col = i//tn, i%tn
        (p.rotate(90*int(rs[i]))
            .rotate(f.t.ki(i%3).ec(eases[i%3], rng=(0, 90))))

    return (P(tr)
        .intersection(P()
            .append(P().oval(tr).t(tr.w/2))
            .append(P().oval(tr).t(-tr.w/2))
            .outline(1)
            )
        .f(1)
        .data(frame=tr)
        .layer(tn)
        .spread()
        .layer(tn)
        .stack()
        .mapv(rotate))

def release(passes):
    from coldtype.renderable.animation import gifski
    gifski(truchet1, passes)
    print("/release")