from coldtype.pens.axidrawpen import AxiDrawPen
from coldtype.runon.path import P
from coldtype.renderable import renderable
from coldtype.geometry import Rect, Point
from time import sleep

try:
    from pyaxidraw import axidraw
except:
    print("Couldn’t import pyaxidraw")
    print("https://axidraw.com/doc/py_api/#installation")
    print("pip install https://cdn.evilmadscientist.com/dl/ad/public/AxiDraw_API.zip")


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


class AxidrawChainable():
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


class axidrawing(renderable):
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
                            fn(AxidrawChainable(ad))
                        return

                    p = p.cond(flatten,
                        lambda p: p.flatten(
                            flatten, segmentLines=False))
                    ap = AxiDrawPen(p, Rect(0, 0, 1100, 850))
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
                print("AXIDRAW TEST")
                print(">", res)
                print("-"*30)
            else:
                ad = axidraw.AxiDraw()
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