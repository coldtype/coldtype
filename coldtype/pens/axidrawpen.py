import os
import sys
dirname = os.path.realpath(os.path.dirname(__file__))
sys.path.append(f"{dirname}/../..")

from coldtype.geometry import Rect, Edge, Point
from fontTools.pens.basePen import BasePen
from fontTools.pens.transformPen import TransformPen
from fontTools.misc.transform import Transform

import math
try:
    from pyaxidraw import axidraw
except:
    pass


class AxiDrawPen(BasePen):
    def __init__(self, dat, h):
        super().__init__(None)
        self.dat = dat
        self.h = h
        self.ad = None
        #dat.replay(self)
        self.last_moveTo = None
    
    def _moveTo(self, p):
        self.last_moveTo = p
        self.ad.moveto(*p)

    def _lineTo(self, p):
        self.ad.lineto(*p)

    def _curveToOne(self, p1, p2, p3):
        print("CANNOT CURVE")

    def _qCurveToOne(self, p1, p2):
        print("CANNOT CURVE")

    def _closePath(self):
        # can this work?
        if self.last_moveTo:
            self.ad.lineto(*self.last_moveTo)

    def draw(self):
        ad = axidraw.AxiDraw()
        ad.interactive()
        ad.connect()
        ad.penup()
        self.ad = ad
        tp = TransformPen(self, (1, 0, 0, -1, 0, self.h))
        self.dat.replay(tp)
        ad.penup()
        ad.moveto(0,0)
        ad.disconnect()


if __name__ == "__main__":
    sys.path.insert(0, os.path.realpath("."))
    from coldtype.pens.datpen import DATPen, OpenPathPen
    from coldtype import StyledString

    #from defcon import Font
    #f = Font(os.path.expanduser("~/Type/drawings/GhzGong/GhzGong.ufo"))
    
    r = Rect(0, 0, 1000, 500)
    ss = StyledString("BALLPOINT", "≈/infini-regular.otf", 200)
    dp1 = ss.asDAT()
    dp1.removeOverlap()
    #dp1 = DATPen() 
    #ghz = f["goodhertz.gordy.copy_1"]
    #ghz = f["G"]
    #dp0 = DATPen()
    #op = OpenPathPen(dp0)
    #ghz.draw(op)
    #dp1 = DATPen()
    #dp0.scale(0.5)
    #dp1.record(dp0)
    #dp1.rect(r.inset(10, 10))
    #dp1.oval(r.inset(100, 100))
    #dp1.align(r)
    dp1.translate(50, 50)
    #dp1.translate(1, 1)
    dp1.flatten(length=1)
    #dp1.roughen()
    scale = 0.005
    dp1.scale(scale)
    ap = AxiDrawPen(dp1, r.h*scale)
    dpb = dp1.bounds()
    print(">>>>>>", dpb)
    if dpb.x >= 0 and dpb.y >= 0 and dpb.w <= 11 and dpb.h <= 6:
        print("Drawing!")
        ap.draw()
    else:
        print("Too big!")
    #print(bp.splines)