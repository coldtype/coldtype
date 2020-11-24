from coldtype import *

@renderable()
def phototype_shift(r):
    return (DATPen()
        .oval(r.inset(150))
        .f(1)
        .flatten(5)
        .roughen(200)
        .phototype(SkiaPen, r, blur=15, cutw=15, context=__CONTEXT__, fill=bw(0))
        #.precompose(SkiaPen, r)
        .translate(500, 50))
