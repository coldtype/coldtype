from coldtype import *

@animation((1080, 1080), timeline=Timeline(3500, 24))
def timer(f):
    e = f.a.progress(f.i, easefn="linear").e
    c = f.a.r.inset(50).take(d:=150, "mxx").take(d, "mny")
    cpen = DP().oval(c)
    return DPS([
        (DP(f.a.r.inset(0)).f(None).s(hsl(0.6)).sw(10)),
        (cpen.copy().f(hsl(0.3))),
        (cpen.copy().subsegment(0, e).f(hsl(0.9, 1)).s(hsl(0.9, 1, 0.3)).sw(2)),])
