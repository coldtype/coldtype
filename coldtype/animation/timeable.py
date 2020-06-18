from coldtype.animation.easing import ease
import math


class Timing():
    def __init__(self, t, loop_t, loop, easefn):
        self.t = t
        self.loop_t = loop_t
        self.loop = loop
        self.loop_phase = int(loop%2 != 0)
        self.e, self.s = self.ease(easefn)
    
    def ease(self, easefn):
        easer = easefn
        if not isinstance(easer, str):
            try:
                iter(easefn) # is-iterable
                if len(easefn) > self.loop:
                    easer = easefn[self.loop]
                elif len(easefn) == 2:
                    easer = easefn[self.loop % 2]
                elif len(easefn) == 1:
                    easer = easefn[0]
            except TypeError:
                pass
        v, tangent = ease(easer, self.loop_t)
        return min(1, max(0, v)), tangent


class Timeable():
    def __init__(self, start, end, index=0):
        self.start = start
        self.end = end
        self.duration = (end-start)
        self.index = index
    
    def __repr__(self):
        return f"Timeable({self.start}, {self.end} ({self.duration}))"
    
    def now(self, i):
        return self.start <= i < self.end

    def io(self, fi, length, ei="eei", eo="eei", negative=False):
        if fi < self.start:
            return 1
        if fi > self.end:
            return 0
        to_end = self.end - fi
        to_start = fi - self.start
        easefn = None
        in_end = False
        if to_end < length and eo:
            in_end = True
            v = 1-to_end/length
            easefn = eo
        elif to_start < length and ei:
            v = 1-to_start/length
            easefn = ei
        else:
            v = 0
        if v == 0 or not easefn:
            return 0
        else:
            a, _ = ease(easefn, v)
            if negative and in_end:
                return -a
            else:
                return a

    def _loop(self, t, times=1, cyclic=True, negative=False):
        lt = t*times*2
        ltf = math.floor(lt)
        ltc = math.ceil(lt)
        if False:
            if ltc % 2 != 0: # looping back
                lt = 1 - (ltc - lt)
            else: # looping forward
                lt = ltc - lt
        lt = lt - ltf
        if cyclic and ltf%2 == 1:
            if negative:
                lt = -lt
            else:
                lt = 1 - lt
        return lt, ltf
    
    def progress(self, i, loops=0, cyclic=True, negative=False, easefn="linear"):
        if i < self.start:
            return Timing(0, 0, 0, easefn)
        if i > self.end:
            return Timing(1, 1, 0, easefn)
        t = (i-self.start) / self.duration
        if loops == 0:
            return Timing(t, t, 0, easefn)
        else:
            loop_t, loop_index = self._loop(t, times=loops, cyclic=cyclic, negative=negative)
            return Timing(t, loop_t, loop_index, easefn)
    
    prg = progress