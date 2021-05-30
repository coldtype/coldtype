from coldtype.test import *

@test((1000, 100))
def test_wider(r):
    return []

@test((500, 500))
def test_no_clip(r):
    return (DATPen()
        .oval(r.inset(50))
        .f(hsl(0.3))
        .translate(-300, 0))

@test((500, 500), clip=True)
def test_yes_clip(r):
    return (DATPen()
        .oval(r.inset(50))
        .f(hsl(0.5))
        .translate(300, 0))