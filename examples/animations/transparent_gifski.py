from coldtype import *
from coldtype.renderable.animation import gifski

@animation((1080, 1080), timeline=30, bg=None)
def scratch(f):
    return (StSt("COLD", Font.ColdObvi(), 500
        , wdth=f.e("eeio"))
        .align(f.a.r)
        .f(hsl(0.7)))

def release(passes):
    gifski(scratch, passes)
    print("/release")