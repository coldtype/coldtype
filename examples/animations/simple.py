from coldtype import *

@animation(timeline=60)
def simple(f):
    return P(
        (P().rect(f.a.r.inset(f.e("eeio", r=(250, 500))))
            .f(hsl(0.65))),
        #(P(Rect.FromCenter(f.c, 100)))
        )
