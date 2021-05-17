from coldtype import *
from coldtype.warping import warp_fn

@renderable(rect=(1200, 300))
def render(r):
    return (StyledString("COLDTYPE",
        Style("assets/MutatorSans.ttf", 200, wght=1))
        .pen()
        .align(r, tv=1)
        .f(None)
        .s(hsl(0.95, 1))
        .sw(5)
        .translate(0, 20)
        #.flatten(3)
        #.nlt(warp_fn(0, 0, mult=100))
        )