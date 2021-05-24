from coldtype import *

@renderable((1080, 1080))
def border(r):
    return DP(r).f(None).s(hsl(0.65)).sw(10)

@animation((1080, 1080), timeline=90, composites=1, layer=True)
def interpolation(f):
    return (DPS([
        # f.last_render(lambda p: p
        #     #.translate(1, -2)
        #     #.scale(0.997)
        #     .sk_fill(1)),
        (DP(Rect(200, 200))
            .align(f.a.r.inset(50), "mnx", "mxy")
            #.rotate(f.e("eeio")*-360)
            #.translate(f.a.r.w*0.66*f.e("ceio", 1), 0)
            #.f(0).s(1).sw(10) # invert for phototype
            )])
        #.phototype(f.a.r, fill=hsl(0.9, 0.8), blur=3, cut=131, cutw=30)
        )