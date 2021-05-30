import time, math

from fontTools.pens.basePen import BasePen
from fontTools.pens.transformPen import TransformPen
from drafting.geometry import Rect

try:
    from pyaxidraw import axidraw
except:
    print("Couldn’t import pyaxidraw")
    pass

MOVE_DELAY = 2

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

    def draw(self, scale=0.01, cm=False):
        self.dat.scale(scale, point=False)
        self.page = self.page.scale(scale)
        b = self.dat.bounds()
        limits = Rect(0, 0, 11, 8.5)
        if cm:
            limits = limits.scale(2.54)
        if b.x >= 0 and b.y >= 0 and b.w <= limits.w and b.h <= limits.h:
            print("Drawing!")
        else:
            print("Too big!", b)
            return False
        
        ad = axidraw.AxiDraw()
        ad.interactive()
        ad.options.units = 1 if cm else 0
        ad.options.speed_pendown = 10
        ad.options.speed_penup = 50
        ad.options.pen_rate_raise = 10

        ad.connect()
        ad.penup()
        self.ad = ad
        tp = TransformPen(self, (1, 0, 0, -1, 0, self.page.h))
        self.dat.replay(tp)
        time.sleep(MOVE_DELAY)
        ad.penup()
        ad.moveto(0,0)
        ad.disconnect()