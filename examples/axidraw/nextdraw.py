from coldtype import *

from coldtype.runon.path import P
from coldtype.renderable import renderable
from coldtype.geometry import Rect, Point
from time import sleep

import time
from fontTools.pens.basePen import BasePen
from fontTools.pens.transformPen import TransformPen
from coldtype.geometry import Rect, Point

try:
    from nextdraw import NextDraw
except:
    print("Couldn’t import nextdraw_api")
    print("https://bantam.tools/nd_py/#installation")
    print("uv pip install https://software-download.bantamtools.com/nd/api/nextdraw_api.zip")


class NextDrawPen(BasePen):
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
            ad = NextDraw()
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


def aximeta(fn):
    def _aximeta(pen:P):
        pen.data(aximeta=dict(fn=fn))
    return _aximeta

def dip_pen(seconds=1, location=(0, 0)):
    return (P()
        .ch(aximeta(lambda ad: ad
            .moveto(*location)
            .pendown()
            .sleep(seconds)
            .penup()
            .moveto(0, 0))))


class NextDrawChainable():
    def __init__(self, ad):
        self.ad = ad
    
    def moveto(self, x, y):
        self.ad.moveto(x, y)
        return self
    
    def penup(self):
        self.ad.penup()
        return self
    
    def pendown(self):
        self.ad.pendown()
        return self
    
    def sleep(self, t):
        sleep(t)
        return self


class nextdrawing(renderable):
    def __init__(self,
        vertical=False,
        flatten=10,
        **kwargs
        ):
        self.flatten = flatten
        self.vertical = vertical
        
        if self.vertical:
            super().__init__(rect=(850, 1100), **kwargs)
        else:
            super().__init__(rect=(1100, 850), **kwargs)
    
    def runpost(self, result, render_pass, renderer_state, config):
        def normalize(p, pos, data):
            if pos != 0:
                return
            
            if self.flatten:
                p.flatten(self.flatten, segmentLines=False)
            
            s = p.s()
            if not s or (s and s.a == 0):
                p.fssw(-1, 0, 3)
            else:
                p.fssw(-1, s, 3)
        
        res = (super()
            .runpost(result, render_pass, renderer_state, config)
            .walk(normalize))
        return res
    
    def draw(self,
        tag=None,
        flatten=None,
        frame=0,
        test=False,
        speed_pendown=100,
        speed_penup=100,
        pen_rate_raise=100,
        pen_rate_lower=100,
        pen_delay_down=0,
        move_delay=0,
        ):
        def _draw(_):
            ad = None

            def walker(p:P, pos, _):
                if pos == 0:
                    ameta = p.data("aximeta")
                    if ameta:
                        fn = ameta.get("fn")
                        if fn:
                            fn(NextDrawChainable(ad))
                        return

                    p = p.cond(flatten,
                        lambda p: p.flatten(
                            flatten, segmentLines=False))
                    ap = NextDrawPen(p, Rect(0, 0, 1100, 850))
                    ap.draw(ad=ad,
                        move_delay=move_delay,
                        zero=False)

            res = self.frame_result(frame, post=True)
            if self.vertical:
                res = res.copy().rotate(90, point=Point(0, 0)).translate(1100, 0)
            if tag is not None:
                if isinstance(tag, int):
                    res = res[tag].copy(with_data=True)
                else:
                    res = res.find_(tag).copy(with_data=True)
            
            if test:
                print("-"*30)
                print("NEXTDRAW TEST")
                print(">", res)
                print("-"*30)
            else:
                ad = NextDraw()
                ad.interactive()
                ad.options.units = 0
                ad.options.speed_pendown = speed_pendown
                ad.options.speed_penup = speed_penup
                ad.options.pen_rate_raise = pen_rate_raise
                ad.options.pen_rate_lower = pen_rate_lower
                ad.options.pen_delay_down = pen_delay_down
                ad.connect()
                print("connected/")
                ad.penup()
                ad.moveto(0,0)
                try:
                    res.walk(walker)
                except Exception as e:
                    print(">>>", e)
                finally:
                    ad.penup()
                    ad.moveto(0,0)
                    ad.disconnect()
                    print("/disconnected")
        
        return _draw


##########################
### Actual custom code ###
##########################


@nextdrawing(flatten=50) # <- tweak this value; lower for better precision
def plot(r:Rect):
    return (P()
        .oval(r.inset(200).square())
        .tag("circle"))


numpad = {
    1: plot.draw("circle")
}
