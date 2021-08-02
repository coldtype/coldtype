from coldtype import *

@animation(timeline=60, write_start=30)
def scratch(f):
    p = DP().With1000(lambda r, p: p
        .moveTo(r.psw)
        .ioEaseCurveTo(r.pne, 5, 50)
        .connect(DP()
            .moveTo(r.psw)
            .ioEaseCurveTo(r.pne, 15, 50)
            .scale(1, -1)))
    
    return PS([
        DP(f.a.r).f(1),
        DP(f.a.r.take(80, "mxy").take(f.e("l"), "W")).f(0, 0.1),
        PS([
            p.copy().fssw(None, hsl(0.9), 3),
            p.copy().skeleton().fssw(None, hsl(0.3), 3)
        ]).scaleToWidth(f.a.r.w).align(f.a.r),
        StSt("COLD", Font.ColdtypeObviously(), 300,
            wdth=f.e(p, 0)).align(f.a.r).f(0, 0.5)])

release = scratch.export("h264", loops=4)