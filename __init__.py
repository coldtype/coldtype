from coldtype import *

@renderable((1080, 540/2), bg=hsl(0.8))
def example(r):
    return (StSt("EXAMPLE", Font.MuSan(), 100, wght=1)
        .align(r, ty=1)
        .f(1))