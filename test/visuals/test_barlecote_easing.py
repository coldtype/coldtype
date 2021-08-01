from coldtype.grid import Grid
from coldtype.time.nle.ascii import AsciiTimeline
from coldtype import *

blc_font = Font.Cacheable("~/Downloads/BLC_Animated_Wordmarks.ttf")

at = AsciiTimeline(4, 30, """
[a     ][b  ][c      ][d   ][e  ][f    ]
""")

@animation((1080, 1080), timeline=90, composites=1)
def scratch(f):

    g = Grid(f.a.r,
        "150 100 250 a 100 100",
        areas="a b c d e f")

    #print(at.map(f.a.r))
    
    e1 = (P().define(g, A=1/3, B=2/3)
        .ez(g.r, 0, 1,
            """⌶|95|$b⊢τ$A $c⊢τ$A
            ⌶|75|$d⊢τ$B $e⊢τ$B ⌶|65|$e↗"""))
    
    e1 = (P().define(at.map(f.a.r), A=1/3, B=2/3)
        .ez(f.a.r, 0, 1,
            """⌶|95|$b⊢τ$A $c⊢τ$A
            ⌶|75|$d⊢τ$B $e⊢τ$B ⌶|65|$e↗"""))

    e2 = (P().define(g)
        .ez(g.r, 0, 0,
            "$c↓ ⌶|85|$c↗OX200 $d↗ ⌶|95|$f↘"))
        
    e2 = (P().define(at.map(f.a.r))
        .ez(f.a.r, 0, 0,
            "$c↓ ⌶|65|$c↗ $d↑ ⌶|95|$e↘"))
    
    return PS([
        #e2.all_guides(),
        (StSt("BA L CT", blc_font,
            font_size=f.e(e2, rng=(120, 360)),
            anim=f.e(e1),
            kp={"C/T":-3})
            .align(f.a.r)),
        e1.fssw(None, hsl(0.3, 0.5, a=0.2), 10),
        e2.fssw(None, hsl(0.9, 0.5, a=0.2), 10),
        #e3.fssw(None, hsl(0.5, 0.5, a=0.2), 10),
    ])

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