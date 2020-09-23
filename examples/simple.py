from coldtype import *

mu = Font("assets/MutatorSans.ttf")

@renderable()
def render(r):
    return (StyledString("COLDTYPE",
        Style(mu, 250, wdth=0, wght=1, tu=-350, r=1))
        .pens()
        .align(r)
        .f("hr", 0.8, 0.7)
        .understroke())