from coldtype import *
from functools import partial

testicon = partial(svgicon, prefix="svgicon", custom_folder="icons")

@testicon()
def circle(r):
    return DATPen().oval(r.inset(50)).f("hr", 0.5, 0.5)

@testicon()
def square(r):
    return DATPen().rect(r.inset(110)).f("hr", 0.5, 0.5)

@testicon()
def diamond(r):
    return DATPen().rect(r.inset(170)).f("hr", 0.5, 0.5).rotate(45)