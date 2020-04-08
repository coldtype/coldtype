from coldtype import *
from coldtype.renderable import svgicon

@svgicon()
def circle(r):
    return DATPen().oval(r.inset(50)).f("hr", 0.5, 0.5)

@svgicon()
def square(r):
    return DATPen().rect(r.inset(110)).f("hr", 0.5, 0.5)

@svgicon()
def diamond(r):
    return DATPen().rect(r.inset(170)).f("hr", 0.5, 0.5).rotate(45)