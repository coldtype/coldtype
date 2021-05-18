from coldtype import *

@renderable(rect=(1920, 1080))
def render(r):
    return DPS([
        DP(r).f(0),
        (StyledString("COLDTYPE",
            Style("assets/MutatorSans.ttf", 300, wght=1))
            .pen()
            .align(r, tv=1)
            .f(hsl(0.85, l=1)))])