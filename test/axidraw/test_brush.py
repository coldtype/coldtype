from coldtype import *
from coldtype.pens.axidrawpen import AxiDrawPen

"""
https://axidraw.com/doc/py_api/#installation
--> pip install https://cdn.evilmadscientist.com/dl/ad/public/AxiDraw_API.zip
"""

@renderable((1100, 850))
def brush1(r):
    return (RunonPen()
        .define(
            r=r.inset(100),
            ri="$rTX=460",
            i="$riTX-220",
            b="$riTY-70OY-20")
        #.oval(r.inset(250))
        .gs("""$i↖ ↗|75|$i↑OY-(iy:=50)
            $i↓OYiy ↙|75|$i↘OX10 ɜ""")
        -.gs("""$i↓OX-5OYiy*4 $i↓OX-5OYiy ↘|75|$i↙OX-5 ɜ""")
        -.gs("""$bＨ∩$i⌶OX50 $b→ $b↗OY50 ɜ""")
        -.gs("""$i↗ ↖|65|$i↑OY-iy $i↑OY-iy*4 ɜ""")
        .scale(0.65)
        .translate(-260, 140)
        .flatten(5)
        .f(None).s(0).sw(10)
        #.skeleton()
        #.repeat(2)
        )

def release(_):
    pen = brush1.func(brush1.rect)
    ap = AxiDrawPen(pen, brush1.rect)
    ap.draw()