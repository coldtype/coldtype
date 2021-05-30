from coldtype.test import *
from coldtype.time import *

ra = Rect(1920, 1080)
rb = Rect(500, 500)

def ms(f, fill, **kwargs):
    return (StyledString(chr(65+f.i),
        Style(mutator, 1000, **kwargs))
        .pen()
        .f(fill)
        .align(f.a.r, th=0))

@animation(ra)
def a_default(f):
    return ms(f, hsl(0.5, 1))

@animation(ra, layer=True)
def a_heaviest(f):
    return ms(f, hsl(0.3, a=0.5), wght=1)
    
@animation(ra, layer=True)
def a_middleweight(f):
    return ms(f, hsl(0.9, a=0.5), wght=0.5)

@animation(rb)
def b_default(f):
    return ms(f, hsl(0.3), wght=0).scale(0.5)

@animation(rb, layer=1)
def b_rotate(f):
    return ms(f, hsl(0.7), wght=0).scale(0.5).rotate(90)

@animation(rb, layer=1)
def b_rotate2(f):
    return ms(f, hsl(0.9), wght=0).scale(0.5).rotate(180)