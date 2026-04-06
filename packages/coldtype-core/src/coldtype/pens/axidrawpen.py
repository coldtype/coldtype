import time, math

from fontTools.pens.basePen import BasePen
from fontTools.pens.transformPen import TransformPen
from coldtype.geometry import Rect, Point

try:
    from pyaxidraw import axidraw
except:
    print("Couldn’t import pyaxidraw")
    pass

class AxiDrawPen(BasePen):
    def __init__(self, dat, page, move_delay=0):
        super().__init__(None)
        self.dat = dat
        self.page = page
        self.ad = None
        self.move_delay = move_delay
        #dat.replay(self)
        self.last_moveTo = None
    
    def _moveTo(self, p):
        self.last_moveTo = p
        time.sleep(self.move_delay)
        self.ad.moveto(*p)
        time.sleep(self.move_delay)

    def _lineTo(self, p):
        time.sleep(self.move_delay)
        self.ad.lineto(*p)

    def _curveToOne(self, p1, p2, p3):
        print("! CANNOT CURVE !")

    def _qCurveToOne(self, p1, p2):
        print("! CANNOT CURVE !")

    def _closePath(self):
        # can this work?
        if self.last_moveTo:
            self.ad.lineto(*self.last_moveTo)

    def draw(self,
        scale=0.01,
        cm=False,
        ad=None,
        move_delay=0,
        zero=True,
        ):

        self.dat.scale(scale, point=Point(0, 0))
        page = self.page.scale(scale)
        bounds = self.dat.bounds()

        limits = Rect(0, 0, 11, 8.5)
        if cm:
            limits = limits.scale(2.54)
        
        def small_enough(r):
            return (r.mnx >= 0
                and r.mny >= 0
                and r.mxx <= limits.w
                and r.mxy <= limits.h)

        if small_enough(page) and small_enough(bounds):
            print("Drawing!")
        else:
            print("Too big!", page, bounds)
            return False
        
        own_ad = False
        if not ad:
            own_ad = True
            ad = axidraw.AxiDraw()
            ad.interactive()
            ad.options.units = 1 if cm else 0
            ad.options.speed_pendown = 50
            ad.options.speed_penup = 50
            ad.options.pen_rate_raise = 50

        if own_ad:
            ad.connect()
        ad.penup()
        self.ad = ad
        self.move_delay = move_delay

        tp = TransformPen(self,
            (1, 0, 0, -1, 0, page.h))
        
        self.dat.replay(tp)
        ad.penup()
        time.sleep(move_delay)
        ad.penup()
        
        if zero:
            ad.moveto(0,0)
        if own_ad:
            ad.disconnect()