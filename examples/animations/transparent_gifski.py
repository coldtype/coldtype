from coldtype import *
from coldtype.renderable.animation import gifski

@animation((600, 250), timeline=30, bg=None)
def scratch(f):
    return (StSt("COLD", Font.ColdObvi(), 200
        , wdth=f.e("eeio"))
        .align(f.a.r)
        .f(hsl(0.7)))

def release(passes):
    os.system(f"open {str(gifski(scratch, passes).parent)}")