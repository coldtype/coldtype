from coldtype import *

@animation((1080, 540), 60, bg=1)
def scratch(f):
    ex = f.e("cei", r=(0, 60))
    rs = random_series(-ex, ex, f.i)

    return (P()
        .rect(Rect(100, 100))
        .difference(P(Rect(100, 100))
            .t(-50, -50)
            .rotate(20))
        .layer(5).spread(spacing:=-20)
        .layer(3).stack(spacing)
        .fssw(hsl(0.8, 1, a=0.3), 0, 1)
        .align(f.a.r)
        .mapv(lambda i, p: p.rotate(rs[i])))
