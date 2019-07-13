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
    from coldtype.viewer import viewer
    from coldtype.pens.datpen import DATPen, OpenPathPen, DATPenSet
    from coldtype.pens.svgpen import SVGPen
    from coldtype import StyledString
    from coldtype.ufo import UFOStringSetter

    #from defcon import Font
    #f = Font(os.path.expanduser("~/Type/drawings/GhzGong/GhzGong.ufo"))
    
    r = Rect(0, 0, 300, 100)
    ss = StyledString("Hello", "≈/Taters-Baked-v0.1.otf", 100)
    dp1 = ss.asDAT()
    dp1.removeOverlap()
    dp1.translate(30, 20)
    #dp1.flatten(length=10)

    dp2 = DATPen()
    dp2.rect(r.take(50, "maxy"))
    #for _r in r.inset(-50, -200).subdivide(15, "miny"):
    #    dp2.rect(_r.take(14, "centery"))
    
    #60 -80
    def draw_frame(offset):
        dp3 = DATPen()
        dp3.record(dp2)
        dp3.translate(0, offset)
        #dp2.translate(0, 50)
        dp3.rotate(5)
        dp3 = DATPen().record(dp1).intersection(dp3)
        dp3.flatten(length=1)
        dp3.rect(Rect(10, 10, 10, 10))
        dp3.rect(r.take(10, "maxx").take(10, "maxy").offset(-10, -10))
        return dp3

    #dp1.translate(100, 0)
    
    if False:
        dp1.roughen(amplitude=20)
        points = dp1.skeletonPoints()
        dp1 = DATPen() #.catmull(dp1.skeletonPoints(), close=True)
        for pts in points:
            _pts = [p[-1][-1] for p in pts]
            dp1.catmull(_pts, close=True)
        dp1.flatten(length=2)
    
    if False:
        scale = 0.005
        op = DATPen()
        for x in range(0, 3):
            op.record(draw_frame(-40).translate(x*r.w, 0))
        op.scale(scale)
        ap = AxiDrawPen(op, r.h*scale)
        dpb = op.bounds()
        print(">>>>>>", dpb)
        if dpb.x >= 0 and dpb.y >= 0 and dpb.w <= 11 and dpb.h <= 6:
            print("Drawing!")
            ap.draw()
        else:
            print("Too big!")
        #print(bp.splines)
    else:
        with viewer() as v:
            #dp1.addAttrs(fill=None, stroke=0)
            #dp2.addAttrs(fill=None, stroke="random")
            #dp2.intersection(dp1)
            op = DATPen()
            #pens = [draw_frame()]
            pens = [draw_frame(x).addAttrs(fill=None, stroke="random") for x in range(-60, 90, 10)]
            dpp = DATPenSet(pens)
            dpp.align()
            #for x in range(0, 3):
            #    op.record(draw_frame(-40).translate(x*r.w, 0))
            v.send(SVGPen.Composite(pens, Rect(0, 0, 2000, 100)), Rect(0, 0, 2000, 100))