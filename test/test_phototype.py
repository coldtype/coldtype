from coldtype.test import *
from coldtype.midi.controllers import LaunchControlXL

# TODO scale in addition to translate?


@renderable((1000, 1000), rstate=1)
def phototype_shift(r, rs):
    nxl = LaunchControlXL(rs.midi)
    return DATPenSet([
        (DATPen()
            .oval(r.inset(150))
            .f(1)
            .flatten(5)
            .roughen(200)
            .phototype(r, blur=15, cutw=nxl(10)*15, fill=bw(0))
            #.precompose(r)
            .translate(500, 0)),
        (StyledString("FILM", Style(mutator, 300, wght=1))
            .pen()
            .f(1)
            .align(r)
            .phototype(r, blur=nxl(10)*15, fill=hsl(0.9)))])
