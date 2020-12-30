from coldtype.test import *

@test(fmt="svg", rasterizer="skia")
def test_simplest(r):
    return DATPenSet().oval(r).f(hsl(random()))