from coldtype import *

@renderable(rect=(1200, 340), bg=0)
def render(r):
    return (StSt("COLDTYPE", "assets/MutatorSans.ttf", 300)
        .align(r, tv=1)
        .f(1))