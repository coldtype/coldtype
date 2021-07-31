from coldtype import *

@animation((1080, 1080), timeline=60, composites=1)
def scratch(f):
    a, b, c, d, e = f.a.r.subdivide(5, "⊢")
    ec = (DP()
        .define(r=f.a.r, a=a, b=b, c=c, d=d, e=e)
        .gs("$a↙ ↘↖|75|$a→ $b→ ↘↖|75|$c↗ ↗↙|95|$d↘ $e↘ ɜ"))
    
    sc = (DP()
        .define(r=f.a.r, a=a, b=b, c=c, d=d, e=e)
        .gs("$a↙ $a↘ ↘↖|95|$b↗ $c↗ ↗↙|95|$d↘ $e↘ ɜ"))
    
    txt = (StSt("COLD", Font.ColdtypeObviously(),
        f.e(sc, 0, rng=(500, 300)),
        100,
        wdth=f.e(ec, 0),
        ro=1)
        .align(f.a.r))
    
    if False:
        return DPS([
            f.last_render(),
            DP(f.a.r).f(1, 0.05),
            DP(Rect(10, 10)).translate(f.i/f.a.duration*f.a.r.w, f.a.r.h/4 + f.e(sc, 0)*f.a.r.h/2),
        ])

    return DPS([
        ec.copy().scale(0.95).fssw(None, hsl(0.6), 5),
        sc.copy().scale(0.95).fssw(None, hsl(0.7), 5),
        txt.fssw(hsl(0.2), 0, 0)
    ])