from coldtype import *

@renderable(rect=(1200, 340), bg=0)
def render(r):
    return (StSt("COLDTYPE", Font.MutatorSans(), 300)
        .align(r, ty=1)
        .f(1))