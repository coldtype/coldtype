from coldtype.test import *

@test()
def test_minus(r):
    return (DATPen()
        .oval(r.inset(10))
        .rect(r.inset(50))
        .f(hsl(0.5))
        .s(0))