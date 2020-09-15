from coldtype.animation.easing import ease
from copy import copy
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
    def __init__(self, start, end, index=0, name=None, data={}):
        self.start = start
        self.end = end
        self.index = index
        self.name = name
        self.feedback = 0
        self.data = data
    
    @property
    def duration(self):
        return self.end - self.start
    
    def __repr__(self):
        return f"Timeable({self.start}, {self.end} ({self.duration}))"
    
    def delay(self, frames_delayed, feedback) -> 'Timeable':
        t = copy(self)
        t.start = t.start + frames_delayed
        t.end = t.end + frames_delayed
        t.feedback = feedback
        t.data = {}
        return t
    
    def retime(self, start=0, end=0, duration=-1):
        "Relative start/end adjustments, or hard-set duration"
        self.start = self.start + start
        self.end = self.end + end
        if duration > -1:
            self.end = self.start + duration
        return self
    
    def now(self, i):
        return self.start <= i < self.end

    def io(self, fi, length, ei="eei", eo="eei", negative=False):
        try:
            length_i, length_o = length
        except:
            length_i = length
            length_o = length
        if fi < self.start:
            return 1
        if fi > self.end:
            return 0
        to_end = self.end - fi
        to_start = fi - self.start
        easefn = None
        in_end = False
        if to_end < length_o and eo:
            in_end = True
            v = 1-to_end/length_o
            easefn = eo
        elif to_start <= length_i and ei:
            v = 1-to_start/length_i
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


class TimeableView(Timeable):
    def __init__(self, timeable, value, svalue, count, index, position, start, end):
        self.timeable = timeable
        self.value = value
        self.svalue = svalue
        self.count = count
        self.index = index
        self.position = position
        self.start = start
        self.end = end
        super().__init__(start, end)
    
    def ease(self, eo="eei", ei="eei"):
        return ease(eo, self.value)[0]
    
    def __repr__(self):
        return f"<TimeableView:{self.timeable}/>"


class TimeableSet():
    def __init__(self, timeables, name=None, start=-1, end=-1, data={}):
        self.timeables = timeables
        self.name = name
        self._start = start
        self._end = end
        self.data = data
    
    def flat_timeables(self):
        ts = []
        for t in self.timeables:
            if isinstance(t, TimeableSet):
                ts.extend(t.flat_timeables())
            else:
                ts.append(t)
        return ts

    def constrain(self, start, end):
        self._start = start
        self._end = end
    
    @property
    def start(self):
        if self._start > -1:
            return self._start
        _start = -1
        for t in self.timeables:
            ts = t.start
            if _start == -1:
                _start = ts
            elif ts < _start:
                _start = ts
        return _start

    @property
    def end(self):
        if self._end > -1:
            return self._end
        _end = -1
        for t in self.timeables:
            te = t.end
            if _end == -1:
                _end = te
            elif te > _end:
                _end = te
        return _end
    
    def __getitem__(self, index):
        return self.timeables[index]
    
    def current(self, frame):
        for idx, t in enumerate(self.flat_timeables()):
            t:Timeable
            if t.start <= frame and frame < t.end:
                return t
    
    def fv(self, frame, filter_fn=None, reverb=[0,5], duration=-1, accumulate=0):
        pre, post = reverb
        count = 0
        timeables_on = []

        ts_duration = self.end - self.start

        for idx, t in enumerate(self.flat_timeables()):
            if filter_fn and not filter_fn(t):
                continue
            t_start = t.start
            t_end = t.end
            if duration > -1:
                t_end = t_start + duration
            pre_start = t_start - pre
            post_end = t_end + post

            t_index = count
            if frame >= pre_start: # correct?
                count += 1
            
            value = 0
            pos = 0
            fi = frame

            if frame >= t_start and frame <= t_end: # truly on
                pos = 0
                value = 1
            else:
                if post_end > ts_duration and frame < pre_start:
                    fi = frame + ts_duration
                elif pre_start < 0 and frame > post_end:
                    fi = frame - ts_duration
                if fi < t_start and fi >= pre_start:
                    pos = 1
                    value = (fi - pre_start) / pre
                elif fi > t_end and fi < post_end:
                    pos = -1
                    value = (post_end - fi) / post
            
            if value > 0:
                timeables_on.append(TimeableView(t, value, -1, count, idx, pos, pre_start, post_end))
            else:
                pass
        
        if accumulate:
            return timeables_on
        else:
            if len(timeables_on) == 0:
                return TimeableView(None, 0, 0, count, -1, 0, 0, 0)
            else:
                return max(timeables_on, key=lambda tv: tv.value)

    def __repr__(self):
        return "<TimeableSet ({:s}){:04d}>".format(self.name if self.name else "?", len(self.timeables))