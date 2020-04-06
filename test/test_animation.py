from coldtype import *
from coldtype.animation import *

@animation()
def render(f):
    return DATPen().oval(f.a.r.inset(50)).f("random")