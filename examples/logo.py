from coldtype import *
from coldtype.fx.skia import phototype

"""
For instagram
"""

@animation(bg=hsl(0.65, 0.6, 0.45), solo=1, tl=2)
def logo(f):
    circle_guide = P().oval(f.a.r.inset(-20)).fssw(-1, 1, 2)
    if f.i == 0:
        return P(
            circle_guide,
            StSt("COLD\nTYPE", Font.ColdObvi(), 500
                , wdth=0.5
                , tu=-50
                , kp={"P/E":-80}
                , leading=-10)
                .index(0, lambda p: p.translate(-130, 0))
                .reverse(recursive=1)
                .align(f.a.r, tx=1, ty=1)
                .rotate(15)
                .translate(-3, 3)
                .fssw(1, 0, 25, 1)
                .ch(phototype(f.a.r,
                    blur=5,
                    cut=170,
                    cutw=11,
                    fill=bw(1))))
    else:
        return P(
            circle_guide,
            StSt("C", Font.ColdObvi(), 850, wdth=1)
                .align(f.a.r)
                .f(1)
                .rotate(10)
                .translate(-5, -7)
                .ch(phototype(f.a.r,
                    blur=5,
                    cut=150,
                    cutw=15,
                    fill=bw(1))))