from coldtype.test import *

@test((500, 500))
def test_h(r):
    return (DATPen()
        .oval(r.inset(50))
        .f(Gradient.H(r, hsl(0.3), hsl(0.8))))

@test((500, 500), solo=1)
def test_v(r):
    ri = r.inset(50).take(0.5, "mxy")
    return (DATPen()
        .oval(ri)
        .f(Gradient.V(ri, hsl(0.3), hsl(0.8))))