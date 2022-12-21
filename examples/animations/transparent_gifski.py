from coldtype import *
#from coldtype.renderable.animation import gifski

@animation((1080, 540), timeline=30, bg=1)
def scratch(f):
    return (StSt("COLD", Font.ColdObvi(), 500
        , wdth=f.e("eeio"))
        .align(f.a.r)
        .f(hsl(0.7)))

release = scratch.gifski(open=True)