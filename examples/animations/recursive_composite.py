from coldtype import *

@animation((1200, 800), timeline=90, composites=1, solo=1)
def interpolation(f):
    return (DATPens([
        f.last_render(lambda p: p.translate(2, -2).sk_fill(1)),
        (DP(Rect(100, 100))
            .align(f.a.r, "mnx", "mxy")
            .rotate(f.e()*-360)
            .translate(50+f.a.r.w*0.66*f.e("ceio", 1), -50)
            .f(0).s(1).sw(10)
            #.f(hsl(0.8))
            )
        ]).phototype(f.a.r, fill=0, blur=3, cut=130, cutw=25))