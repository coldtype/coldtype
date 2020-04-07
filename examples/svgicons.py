from coldtype import *
from coldtype.renderable import svgicon

@svgicon()
def circle(r):
    return DATPen().oval(r.inset(50)).f("hr", 0.5, 0.5)

@svgicon(hide=1)
def square(r):
    return DATPen().rect(r.inset(110)).f("hr", 0.5, 0.5)