from coldtype import *

@renderable((500, 500))
def layer1(r):
    return P().oval(r.inset(10)).f(hsl(0.3))

@renderable((500, 500), layer=1)
def layer2(r):
    return P().rect(r.inset(150)).rotate(45).f(hsl(0.6))
