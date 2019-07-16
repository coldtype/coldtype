import os
import sys
import time

dirname = os.path.realpath(os.path.dirname(__file__))
sys.path.append(f"{dirname}/../..")

from fontTools.pens.basePen import BasePen
from fontTools.pens.transformPen import TransformPen
from fontTools.misc.transform import Transform
from coldtype.geometry import Rect, Edge, Point
from coldtype.pens.svgpen import SVGPen
from coldtype.viewer import viewer

import math
try:
    from pyaxidraw import axidraw
except:
    pass

MOVE_DELAY = 0

class AxiDrawPen(BasePen):
    def __init__(self, dat, page):
        super().__init__(None)
        self.dat = dat
        self.page = page
        self.ad = None
        #dat.replay(self)
        self.last_moveTo = None
    
    def _moveTo(self, p):
        self.last_moveTo = p
        time.sleep(MOVE_DELAY)
        self.ad.moveto(*p)
        time.sleep(MOVE_DELAY)

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

    def draw(self, scale=0.01, dry=True):
        if dry:
            with viewer() as v:
                dp = DATPen().record(self.dat).addAttrs(fill=None, stroke=0)
                v.send(SVGPen.Composite([dp], self.page), self.page)
        else:
            self.dat.scale(scale)
            self.page = self.page.scale(scale)
            b = self.dat.bounds()
            if b.x >= 0 and b.y >= 0 and b.w <= 11 and b.h <= 8.5:
                print("Drawing!")
            else:
                print("Too big!", b)
                return False
            ad = axidraw.AxiDraw()
            ad.interactive()
            ad.options.speed_pendown = 110
            ad.options.speed_penup = 110

            ad.connect()
            ad.penup()
            self.ad = ad
            tp = TransformPen(self, (1, 0, 0, -1, 0, self.page.h))

            self.dat.replay(tp)
            time.sleep(MOVE_DELAY)
            ad.penup()
            ad.moveto(0,0)
            ad.disconnect()


if __name__ == "__main__":
    sys.path.insert(0, os.path.realpath("."))
    from coldtype.viewer import viewer
    from coldtype.pens.datpen import DATPen, OpenPathPen, DATPenSet
    from coldtype import Slug, Style
    from coldtype.ufo import UFOStringSetter
    from random import random, randint
    
    def taters_frames():
        r = Rect(0, 0, 340, 100)
        ss = StyledString("Analog", "≈/Taters-Baked-v0.1.otf", 90)
        dp1 = ss.asDAT()
        dp1.removeOverlap()
        dp1.translate(30, 20)
        dp2 = DATPen()
        dp2.rect(r.take(50, "maxy"))
        
        def draw_frame(offset):
            dp3 = DATPen()
            dp3.record(dp2)
            dp3.translate(0, offset)
            dp3.rotate(5)
            dp3 = DATPen().record(dp1).intersection(dp3)
            dp3.flatten(length=1)
            dp3.rect(Rect(10, 10, 10, 10))
            dp3.rect(r.take(10, "maxx").take(10, "maxy").offset(-10, -10))
            return dp3
        
        page = Rect(0, 0, 1500, 1000)
        pens = [draw_frame(x) for x in range(-100, 60, 10)]
        dpp = DATPenSet(pens)
        dpp.align(page.grid(5, 4))
        dp = dpp.asPen().addAttrs(fill=None, stroke="random")
        
        ap = AxiDrawPen(dp, page)
        ap.draw(0.007, dry=True)
    
    def ghz_test():
        r = Rect(0, 0, 500, 500)
        uss = UFOStringSetter("~/Type/drawings/Plotkoch/Plotkoch.ufo")
        dp = uss.getLine("n")
        #ss = StyledString("Ok!", "≈/Nonplus-Black.otf", 100)
        #dp = ss.asDAT()
        #dp.align(r)
        #dp.oval(r.inset(100, 100))
        dp.scaleToRect(r.inset(150, 150))
        dp.flatten(length=1)
        dp.align(r)
        ap = AxiDrawPen(dp, r)
        ap.draw(dry=0)
    
    def splitLine(pt1, pt2, where, isHorizontal):
        pt1x, pt1y = pt1
        pt2x, pt2y = pt2

        ax = (pt2x - pt1x)
        ay = (pt2y - pt1y)

        bx = pt1x
        by = pt1y

        a = (ax, ay)[isHorizontal]

        if a == 0:
            return [(pt1, pt2)]
        t = (where - (bx, by)[isHorizontal]) / a
        if 0 <= t < 1:
            midPt = ax * t + bx, ay * t + by
            return [(pt1, midPt), (midPt, pt2)]
        else:
            return [(pt1, pt2)]
    
    def fill_test():
        def frame(t):
            r = Rect(0, 0, 210, 210)
            ss1 = Slug("Digital", Style("≈/Taters-Baked-v0.1.otf", 55))
            ss0 = Slug("Analog", Style("≈/Nonplus-Black.otf", 45))
            ss2 = Slug("to", Style("≈/ObviouslyVariable.ttf", 50, variations=dict(wdth=1, wght=t, slnt=0), features=dict(ss06=True)))
            dp00 = ss1.asDAT()
            dp00.flatten(length=20)
            dp00.align(r)
            dp00.translate(0, 50)
            dp0 = ss0.asDAT()
            dp0.align(r)
            dp0.translate(0, -50)
            dp0.flatten(length=1)
            dp000 = ss2.asDAT()
            dp000.align(r)
            dp000.translate(0, 0)
            dp000.flatten(length=1)
            dp = DATPen()
            dp.record(dp000)
            dp.record(dp00)
            dp.record(dp0)
            dp.removeOverlap()
            dp.rect(r.inset(4, 4))
            return dp
        
        dps = DATPenSet()
        length = 20
        for i in range(0, length):
            dps.pens.append(frame(i/length))
        r = Rect(0, 0, 1100, 850)
        dps.align(r.inset(30, 20).grid(4, 5))
        ap = AxiDrawPen(dps.asPen(), r)
        ap.draw(dry=0)
    
    def bounds_test():
        r = Rect(0, 0, 1100, 850)
        dp = DATPen().rect(r.inset(10, 10))
        ap = AxiDrawPen(dp, r)
        ap.draw(dry=1)
    
    #taters_frames()
    #ghz_test()
    fill_test()
    #bounds_test()