from coldtype.grid import Grid
from coldtype.time.nle.ascii import AsciiTimeline
from coldtype import *

blc_font = Font.Cacheable("~/Downloads/BLC_Animated_Wordmarks.ttf")

at = AsciiTimeline(2, 30, """
[a  ][b ][c  ][d       ][e  ][f  ][g  ][h   ]
""")

@animation((1080, 1080), timeline=at, composites=1)
def scratch(f):
    e1 = (P().define(at.rmap(f.a.r), A=1/3, B=2/3)
        .ez(f.a.r, 0, 1,
            """⌶|75|$b⊢τ$A $c⊢τ$A
            ⌶|55|$d⊢τ$B $e⊢τ$B ⌶|65|$e↗
            ⊢|65|$g⊢τ0.85 ⌶|65|$g↗"""))
    
    e2 = (P().define(at.rmap(f.a.r))
        .ez(f.a.r, 0, 0,
            "$c↓ ⌶|65|$c↗OX150 $d↗ ⌶|80|$f↘"))
    
    #e2 = (P().define(at.rmap(f.a.r))
    #    .ez(f.a.r, 0, 0,
    #        "$b↘ ⌶|65|$c↗ $d↗ ⌶|95|$g↘"))
    
    return PS([
        e2.all_guides(sw=1),
        # (StSt("CDEL", Font.ColdtypeObviously(),
        #     f.e(e2, 0, rng=(120, 360)),
        #     wdth=f.e(e1, 1)
        #     )
        #     .align(f.a.r)),
        (StSt("BA L CT", blc_font,
            font_size=f.e(e2, rng=(120, 360)),
            anim=f.e(e1),
            kp={"C/T":-3})
            .align(f.a.r)),
        e1.fssw(None, hsl(0.3, 0.5, a=0.2), 10),
        e2.fssw(None, hsl(0.9, 0.5, a=0.2), 10)])