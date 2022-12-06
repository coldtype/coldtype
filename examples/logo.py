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
                , r=1
                , kp={"P/E":-100}
                , leading=-10)
                .index(0, lambda p: p.translate(-130, 0))
                .reverse()
                .align(f.a.r, th=1, tv=1)
                .rotate(15)
                .translate(-3, 3)
                .fssw(1, 0, 25, 1)
                .ch(phototype(f.a.r,
                    blur=2+5,
                    cut=50+150,
                    cutw=1+6,
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
                    cutw=25,
                    fill=bw(1))))