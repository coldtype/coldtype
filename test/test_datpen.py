from coldtype import *

@renderable(bg=0.15)
def test_projection(r):
    shape = DATPen().rect(500, 500).difference(DATPen().oval((-150, -150, 500, 500)))
    return DATPenSet([
        shape.copy().castshadow(-45, 300).f("hr", 0.65, 0.25),
        shape.copy().project(-45, 300).f("hr", 0.5, 0.5),
        shape.f("hr", 0.75, 0.75)
    ]).align(r)