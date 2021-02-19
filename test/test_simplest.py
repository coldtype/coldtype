from coldtype.test import *

@test(fmt="svg", rasterizer="skia")
def test_simplest(r):
    return (DATPens()
        .oval(r.inset(10).take(0.5, "mnx"))
        .align(r)
        .f(hsl(random())))