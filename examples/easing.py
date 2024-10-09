from coldtype import *

@renderable((1080, 540), bg=1)
def easing(r):
    sq = Rect(50, 50)
    return (P().oval(sq)
        .outline(4)
        .layer(17)
        .spread(4)
        .mape(lambda e, p: p
            .f(hsl(0.65+ez(e, "ceio"), 0.9, 0.5))
            .t(0, ez(e, "eeio", r=(0, 300))))
        .align(r))