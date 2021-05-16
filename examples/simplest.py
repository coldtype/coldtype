from coldtype import *

@renderable(rect=(1200, 300))
def render(r):
    return (StyledString("COLDTYP",
        Style("assets/MutatorSans.ttf", 300))
        .pens()
        .align(r, tv=1)
        .f(hsl(0.95)))