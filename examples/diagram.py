from coldtype import *
import coldtype.fx.diagram as d

r1 = random_series(seed=5)

@renderable((1080, 540), bg=1)
def d1(r):
    return (P().oval(Rect(120))
        .layer(3).spread(70)
        .layer(2).stack(60)
        .mapv(lambda i, p: p.f(hsl(r1[i], 0.7, 0.7)))
        .index(0, lambda p: p.ch(d.interconnect()))
        .index(1, lambda p: p.reverse()
            .ch(d.interconnect("←→←")))
        .append(lambda p: d.ujoin(p[0], p[1], "→", 50, "-←"))
        .append(lambda p: d.ujoin(p[1], p[0], "←", 50, "-→"))
        .align(r))
