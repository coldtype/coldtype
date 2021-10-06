from coldtype import *

@animation()
def scratch(f):
    return (P()
        .rect(f.a.r.inset(150))
        .rotate(f.e("ceio", 1, rng=(-0.5, 0.5)))
        .f(hsl(0.65)))
