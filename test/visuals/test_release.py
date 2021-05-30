from coldtype import *


@renderable((500, 500))
def r1(r):
    return DATPen().oval(r.inset(130)).f(hsl(random()))

@renderable((500, 500))
def r2(r):
    return DATPen().rect(r.inset(150)).rotate(10).f(hsl(random()))


def release(passes):
    for p in passes:
        print(p)