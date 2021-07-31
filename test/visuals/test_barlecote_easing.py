from coldtype.grid import Grid
from coldtype import *

blc_font = Font.Cacheable("~/Downloads/BLC_Animated_Wordmarks.ttf")

@animation((1080, 1080), timeline=320, composites=1)
def scratch(f):
    g = Grid(f.a.r, 4, 3)

    e2 = (DP().define(Grid(f.a.r, 4, 3))
        .gs("""$ca↙ ⌶|95|$ca↗ ⌶|95|$bb• ⌶|75|$bb↗
            $bc↗ ⌶|95|$ad• ⌶|95|$ad↗ ɜ"""))
    
    e3 = (DP().define(Grid(f.a.r, 4, 1))
        .gs("$a↙ $b↓ ⌶|95|$b↗ $c↗ ⌶|65|$d↓ $d↘ ɜ"))
    
    return DPS([
        e2.fssw(None, 0, 2),
        e3.fssw(None, hsl(0.3), 2),
        DP(f.a.r.take(f.e("l"), "mnx")).f(0, 0.1),
        (StSt("BA L CT", blc_font,
            font_size=f.e(e3, rng=(120, 300)),
            #font_size=200,
            anim=f.e(e2))
            .align(f.a.r))
    ])
    
    print(g.keyed["k"])

    ec = (DP()
        .define(Grid(f.a.r, 5, 1))
        .gs("$a↙ ⌶|95|$a→ $b→ ⌶|75|$c↑ ⌶|95|$d↓ $e↘ ɜ"))
    
    sc = (DP()
        .define(Grid(f.a.r, 5, 1))
        .gs("$a↖ $a↗ ⌶|85|$b↘ $c↘ ⌶|95|$d↗ $e↗ ɜ"))
    
    txt = (StSt("COLD", Font.ColdtypeObviously(),
        f.e(sc, 0, rng=(300, 500)),
        #300,
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
        ec.copy().scale(1, 0.5).fssw(None, hsl(0.6), 5),
        sc.copy().scale(1, 0.5).fssw(None, hsl(0.7), 5),
        txt.fssw(bw(1, 0.9), hsl(0.9), 5),
        DP(f.a.r.take(f.e("l"), "mnx")).f(0, 0.1),
    ])