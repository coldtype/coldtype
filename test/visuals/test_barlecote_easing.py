from coldtype.grid import Grid
from coldtype.time.nle.ascii import AsciiTimeline
from coldtype import *

blc_font = Font.Cacheable("~/Downloads/BLC_Animated_Wordmarks.ttf")

at = AsciiTimeline(2, 30, """
[a  ][b ][c  ][d       ][e  ][f  ][g  ][h   ]
""")

atr = at.rmap(Rect(1080, 1080))

@animation((1080, 1080), timeline=at, composites=1)
def scratch(f):
    e1 = (P().define(at.rmap(f.a.r), A=1/3, B=2/3)
        .ez(f.a.r, 0, 1,
            """$b⊢τ$A|⌶|75 $c⊢τ$A
            $d⊢τ$B|⌶|55 $e⊢τ$B $e↗|⌶|65
            $g⊢τ0.85|⊢|65 $g↗|⌶|65"""))
    
    e2 = (P().define(at.rmap(f.a.r))
        .ez(f.a.r, 0, 0,
            "$c↓ $c↗OX150|∫|0|0 $d↗ $f↘|∫"))
    
    return PS([
        e2.all_guides(sw=1),
        (StSt("CDEL", Font.ColdtypeObviously(),
            f.e(e2, 0, rng=(120, 300)),
            wdth=f.e(e1, 1)
            )
            .align(f.a.r)),
        # (StSt("BA L CT", blc_font,
        #     font_size=f.e(e2, rng=(120, 360)),
        #     anim=f.e(e1),
        #     kp={"C/T":-3})
        #     .align(f.a.r)),
        e1.fssw(None, hsl(0.3, 0.5, a=0.2), 10),
        e2.fssw(None, hsl(0.9, 0.5, a=0.2), 10)])