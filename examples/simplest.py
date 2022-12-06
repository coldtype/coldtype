from coldtype import *

@renderable(rect=(1200, 340), bg=0)
def render(r):
    return (StSt("COLDTYPE", Font.MutatorSans(), 200)
        .align(r)
        .f(1))