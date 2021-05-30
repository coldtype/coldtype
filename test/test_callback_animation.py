from coldtype.test import *

from coldtype.time.easing import ease
from time import time, sleep

class Animator():
    def __init__(self, factor):
        self.start = time()
        self.factor = 1/factor
    
    def now(self, rs, easefn="linear"):
        ee = (time() - self.start) * self.factor
        if ee < 1:
            rs.callback = 0.1 # factor?
        return ease(easefn, min(1, max(0, ee)))[0]


class oneshot(animation):
    def __call__(self, func):
        self._start_time = time()
        self._last_frame = -1
        return super().__call__(func)
    
    def run(self, rp, rs):
        seconds = self.timeline.duration / self.timeline.fps
        ee = (time() - self._start_time) * (1/seconds)
        ee = min(1, max(0, ee))
        frame = int(self.timeline.duration * ee)
        if frame != self._last_frame:
            #self._last_frame = frame
            if self.rstate:
                res = rp.fn(Frame(frame, self), rs)
            else:
                res = rp.fn(Frame(frame, self))

            #res = super().run(rp, rs)
            if ee < 1:
                rs.callback = 0.1
            return res

anim = Animator(0.5)

@renderable((500, 500), rstate=1)
def callback(r, rs):
    return (DATPen()
        .oval(r.inset(50+anim.now(rs, "eeo")*100))
        .f(None)
        .s(hsl(anim.now(rs)))
        .sw(20))

tl = Timeline(60, 60)

@oneshot((1000, 500), timeline=tl)
def callback2(f):
    e = f.a.progress(f.i, easefn="eeo").e
    return (StyledString("COLD",
        Style(co, 800-e*650, wdth=e, ro=1))
        .pen()
        .align(f.a.r)
        .f(0)
        .s(1).sw(3))
