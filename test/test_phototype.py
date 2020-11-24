from coldtype import *

# TODO scale in addition to translate?


@renderable()
def phototype_shift(r):
    return (DATPen()
        .oval(r.inset(150))
        .f(1)
        .flatten(5)
        .roughen(200)
        .phototype(r, blur=15, cutw=15, fill=bw(0))
        #.precompose(r)
        .translate(150, 50))
