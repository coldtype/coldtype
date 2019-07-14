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

    def draw(self, scale=0.005, dry=True):
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
    from coldtype import StyledString
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
        from fontPens.marginPen import MarginPen
        from fontTools.pens.pointInsidePen import PointInsidePen
        r = Rect(0, 0, 300, 300)
        ss1 = StyledString("Digital", "≈/Taters-Baked-v0.1.otf", 70)
        ss0 = StyledString("Analog", "≈/Nonplus-Black.otf", 70)
        ss2 = StyledString("to", "≈/ObviouslyVariable.ttf", 30, variations=dict(wdth=1, wght=1, slnt=1), features=dict(ss06=True))
        dp00 = ss1.asDAT()
        dp00.flatten(length=20)
        dp00.align(r)
        dp00.translate(0, 60)
        dp0 = ss0.asDAT()
        dp0.align(r)
        dp0.translate(0, -60)
        dp0.flatten(length=1)
        dp0.removeOverlap()

        dp000 = ss2.asDAT()
        dp000.align(r)
        dp000.flatten(length=1)

        dp = DATPen()

        import pyclipper
        
        if False:
            for y in range(0, 100, 6):
                mp = MarginPen(dict(), y, isHorizontal=True)
                dp0.replay(mp)
                intersections = mp.getAll()
                pairs = zip(intersections[::2], intersections[1::2])
                for x1, x2 in pairs:
                    dp.line([(x1, y), (x2, y)])
        elif False:
            dp1 = DATPen()
            for p in range(0, 4):
                dp1 = DATPen()
                dp1.line([
                    (0, randint(r.y, r.h)),
                    (r.w, randint(r.y, r.h))
                    #(0, 100),
                    #(500, 100)
                    ])

                pc = pyclipper.Pyclipper()

                for contour in dp0.points():
                    pc.AddPath(contour, pyclipper.PT_SUBJECT, True)
                
                for contour in dp1.points():
                    pc.AddPath(contour, pyclipper.PT_SUBJECT, False)
                
                solution = pc.Execute2(pyclipper.CT_UNION, pyclipper.PFT_NONZERO, pyclipper.PFT_NONZERO)

                allSolutionPoints = []
                for contour in pyclipper.OpenPathsFromPolyTree(solution)[:]:
                    print(">>>")
                    for x, y in contour:
                        print(contour)
                        if (x,y) in allSolutionPoints:
                            print("nope")
                        else:
                            allSolutionPoints.append((x, y))
                
                pairs = zip(allSolutionPoints[1::2], allSolutionPoints[2::2])
                #print(list(pairs))
                #for idx, p1 in enumerate(allSolutionPoints[1::2]):
                #    print(p1)
                #    p2 = allSolutionPoints[idx+1]
                for p1 in list(allSolutionPoints)[1:-1]:
                    #dp.line([p1, p2])
                    dp.rect(Rect(p1[0], p1[1], 1, 1))
            
            #for contour in pyclipper.ClosedPathsFromPolyTree(solution):
            #    for x, y in contour:
            #        allSolutionPoints.add((x, y))
            
            #for pts in dp0.skeletonPoints():
            #    print(pts[1])
            #dp2 = dp1.intersection(dp0)
            #dp1.replay(dp)
            #for y in range(0, 100, 6):
            #    #mp = MarginPen(dict(), y, isHorizontal=True)
            #    dp0.replay(mp)
            #    intersections = mp.getAll()
            #    pairs = zip(intersections[::2], intersections[1::2])
            #    for x1, x2 in pairs:
            #        dp.line([(x1, y), (x2, y)])
        else:
            dp000.replay(dp)
            dp00.replay(dp)
            dp0.replay(dp)
            #dp.flatten(30)
        
        #dp0.replay(dp)
        #dp.rect(r.inset(10, 10))
        #dp.flatten(length=1)
        ap = AxiDrawPen(dp, r)
        ap.draw(dry=0)
    
    #taters_frames()
    #ghz_test()
    fill_test()