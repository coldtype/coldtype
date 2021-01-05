from coldtype.test import *

@test(fmt="svg", rasterizer="skia")
def test_simplest(r):
    return DATPens().oval(r).f(hsl(random()))