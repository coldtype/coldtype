from dataclasses import dataclass
from coldtype.interpolation import lerp
from coldtype.pens.draftingpen import DraftingPen
from coldtype.time.easing import ease, ez, applyRange
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
        if not isinstance(easer, str) and not hasattr(easer, "value") and not type(easefn).__name__ == "Glyph":
            try:
                iter(easefn) # is-iterable
                if len(easefn) > self.loop:
                    easer = easefn[self.loop]
                elif len(easefn) == 2:
                    easer = easefn[self.loop % 2]
                elif len(easefn) == 1:
                    easer = easefn[0]
                else:
                    easer = easefn[0]
            except TypeError:
                print("failed")
                pass
        v, tangent = ease(easer, self.loop_t)
        return min(1, max(0, v)), tangent


class Timeable():
    """
    Abstract base class for anything with a concept of `start` and `end`/`duration`

    Implements additional methods to make it easier to work with time-based concepts
    """
    def __init__(self, start, end, index=0, name=None, data={}, timeline=None):
        self.start = start
        self.end = end
        self.index = index
        self.idx = index
        self.i = index
        self.name = name
        self.feedback = 0
        self.data = data
        self.timeline = timeline
    
    @property
    def duration(self):
        return self.end - self.start
    
    def __repr__(self):
        if self.name:
            return f"Timeable('{self.name}', {self.start}, {self.end} ({self.duration}))"
        else:
            return f"Timeable({self.start}, {self.end} ({self.duration}))"
    
    def delay(self, frames_delayed, feedback) -> 'Timeable':
        t = copy(self)
        t.start = t.start + frames_delayed
        t.end = t.end + frames_delayed
        t.feedback = feedback
        t.data = {}
        return t
    
    def retime(self, start=0, end=0, duration=-1):
        self.start = self.start + start
        self.end = self.end + end
        if duration > -1:
            self.end = self.start + duration
        return self
    
    def now(self, i):
        return self.start <= i < self.end

    def _normalize_fi(self, fi):
        if hasattr(self, "timeline") and self.timeline:
            if self.end > self.timeline.duration and fi < self.start:
                return fi + self.timeline.duration
        return fi
    
    def e(self, fi, easefn="eeio", loops=1, rng=(0, 1), cyclic=True, to1=False, out1=False, **kwargs):
        if "ŋ" in kwargs: rng = kwargs["ŋ"]

        if not isinstance(easefn, str):
            loops = easefn
            easefn = "eeio"
        fi = self._normalize_fi(fi)
        t = self.progress(fi, loops=loops, easefn=easefn, cyclic=cyclic, to1=to1, out1=out1)
        e = t.e
        ra, rb = rng
        if ra > rb:
            e = 1 - e
            rb, ra = ra, rb
        return ra + e*(rb - ra)

    def io(self, fi, length, ei="eei", eo="eei", negative=False):
        """
        Somewhat like ``progress()``, but can be used to fade in/out (hence the name (i)n/(o)ut)

        * ``length`` refers to the lenght of the ease, in frames
        * ``ei=`` takes the ease-in mnemonic
        * ``eo=`` takes the ease-out mnemonic
        """
        try:
            length_i, length_o = length
        except:
            length_i = length
            length_o = length
        
        fi = self._normalize_fi(fi)

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
    
    def io2(self, fi, length, easefn="eeio", negative=False):
        try:
            length_i, length_o = length
        except:
            length_i = length
            length_o = length
        
        if isinstance(length_i, float):
            length_i = int(self.duration*(length_i/2))
        if isinstance(length_o, float):
            length_o = int(self.duration*(length_o/2))
        
        if fi < self.start or fi > self.end:
            return 0
        
        try:
            ei, eo = easefn
        except ValueError:
            ei, eo = easefn, easefn

        to_end = self.end - fi
        to_start = fi - self.start
        easefn = None
        in_end = False

        if to_end < length_o and eo:
            in_end = True
            v = to_end/length_o
            easefn = eo
        elif to_start <= length_i and ei:
            v = to_start/length_i
            easefn = ei
        else:
            v = 1

        if v == 1 or not easefn:
            return 1
        else:
            a, _ = ease(easefn, v)
            return a
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
    
    def progress(self, i, loops=0, cyclic=True, negative=False, easefn="linear", to1=False, out1=True) -> Timing:
        """
        Given an easing function (``easefn=``), calculate the amount of progress as a Timing object

        ``easefn=`` takes a mnemonic as enumerated in :func:`coldtype.time.easing.ease`
        """
        if i < self.start:
            return Timing(0, 0, 0, easefn)
        if i > self.end:
            if out1:
                return Timing(1, 1, 0, easefn)
            else:
                return Timing(0, 0, 0, easefn)
        d = self.duration
        if to1:
            d = d - 1
        t = (i-self.start) / d
        if loops == 0:
            return Timing(t, t, 0, easefn)
        else:
            loop_t, loop_index = self._loop(t, times=loops, cyclic=cyclic, negative=negative)
            return Timing(t, loop_t, loop_index, easefn)
    
    def halfover(self, i):
        e = self.progress(i, to1=1).e
        return e >= 0.5
    
    #prg = progress

    def at(self, i) -> "Easeable":
        return Easeable(self, i)


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
    

@dataclass
class EaseableTiming():
    t: float = 0
    i: int = -1


class Easeable():
    def __init__(self,
        t:Timeable,
        i:int
        ):
        if not t:
            raise Exception("T MUST EXIST")
        self.t = t
        self.i = i

        self._ts = False
        if not isinstance(t, Timeable):
            self._ts = True
    
    def __repr__(self) -> str:
        return f"<Easeable@{self.i}:{self.t}/>"
    
    def _normRange(self, rng, **kwargs):
        if "r" in kwargs:
            rng = kwargs["r"]
        if isinstance(rng, (int, float)):
            rng = (0, rng)
        return rng
    
    def _maxRange(self, rng, vs):
        if rng[1] > rng[0]:
            return max(vs)
        else:
            return min(vs)
    
    def tv(self,
        loops=0,
        cyclic=True,
        to1=True,
        choose=max,
        wrap=False,
        find=False
        ):
        if self._ts:
            es = [Easeable(t, self.i).tv(loops, cyclic, to1).t for t in self.t]
            e = choose(es)
            if find is False:
                return EaseableTiming(e)
            else:
                return EaseableTiming(e, es.index(e))

        t, i = self.t, self.i
        if wrap:
            i = i % self.t.duration
        else:
            i = self.i

        if i < t.start:
            return EaseableTiming(0)
        elif i > t.end:
            if loops % 2 == 0:
                return EaseableTiming(1)
            else:
                return EaseableTiming(0)
        else:
            d = t.duration
            v = (i - t.start) / d
            if loops == 0:
                return EaseableTiming(v)
            else:
                loop_t, loop_index = self.t._loop(v, times=loops, cyclic=cyclic, negative=False)
                return EaseableTiming(loop_t)

    def e(self,
        easefn="eeio",
        loops=0,
        rng=(0, 1),
        on=None, # TODO?
        cyclic=True,
        to1=False,
        wrap=False,
        choose=max,
        find=False,
        **kwargs
        ):
        rng = self._normRange(rng, **kwargs)
        
        if not isinstance(easefn, str) and not isinstance(easefn, DraftingPen) and not type(easefn).__name__ == "Glyph":
            loops = easefn
            easefn = "eeio"
        
        tv = self.tv(loops, cyclic, to1, choose, wrap, find=True)
        
        ev = ez(tv.t, easefn, cyclic=cyclic, rng=rng)
        if find:
            return ev, tv.i
        else:
            return ev
    
    def io(self,
        length,
        easefn="eeio",
        negative=False,
        rng=(0, 1),
        **kwargs
        ):
        rng = self._normRange(rng, **kwargs)

        if self._ts:
            es = [Easeable(t, self.i).io(length, easefn, negative, rng) for t in self.t]
            return self._maxRange(rng, es)

        t = self.t
        try:
            length_i, length_o = length
        except:
            length_i = length
            length_o = length
        
        if isinstance(length_i, float):
            length_i = int(t.duration*(length_i/2))
        if isinstance(length_o, float):
            length_o = int(t.duration*(length_o/2))
        
        if self.i < t.start or self.i > t.end:
            return rng[0]
        
        try:
            ei, eo = easefn
        except ValueError:
            ei, eo = easefn, easefn

        to_end = t.end - self.i
        to_start = self.i - t.start
        easefn = None
        in_end = False

        if to_end < length_o and eo:
            in_end = True
            v = to_end/length_o
            easefn = eo
        elif to_start <= length_i and ei:
            v = to_start/length_i
            easefn = ei
        else:
            v = 1

        if v == 1 or not easefn:
            return rng[1]
        else:
            return ez(v, easefn, 0, False, rng)
            #a, _ = ease(easefn, v)
            #return a
            if negative and in_end:
                return -a
            else:
                return a
    
    def adsr(self,
        adsr=[5, 0, 0, 10],
        es=["eei", "qeio", "eeo"],
        rng=(0, 1),
        dv=None, # decay-value
        rs=False, # read-sustain
        **kwargs
        ):
        rng = self._normRange(rng, **kwargs)

        if self._ts:
            es = [Easeable(t, self.i).adsr(adsr, es, rng, dv, rs) for t in self.t]
            return self._maxRange(rng, es)

        if len(adsr) == 2:
            d, s = 0, 0
            a, r = adsr
        elif len(adsr) == 3:
            d = 0
            a, s, r = adsr
        elif len(adsr) == 4:        
            a, d, s, r = adsr
        
        if rs:
            s = self.t.duration
        
        if len(es) == 2:
            de = "qeio"
            ae, re = es
        elif len(es) == 3:
            ae, de, re = es
        
        if dv is None:
            dv = rng[1]
            if d > 0:
                dv = lerp(rng[0], rng[1], 0.5)
        
        i, t = self.i, self.t
        end = t.start + d + s + r
        ds = t.start + d + s

        td = -1
        if t.timeline:
            td = t.timeline.duration

        if i > end and td > -1:
            i = i - td
        
        rv = rng[0]
        if td > -1 and end > td:
            if i < t.start-a:
                i = i + td
            rv = Easeable(Timeable(ds, end), i+td).e(re, rng=(dv, rng[0]), to1=1)

        if i < t.start: # ATTACK
            s = t.start - a
            return self._maxRange(rng, [rv, Easeable(Timeable(t.start-a, t.start), i).e(ae, rng=rng, to1=1)])
        elif i >= t.start:
            if i == t.start:
                return rng[1]
            if i >= ds: # RELEASE
                return Easeable(Timeable(ds, end), i).e(re, rng=(dv, rng[0]), to1=1)
            else:
                if i >= t.start + d: # SUSTAIN
                    return dv
                else: # DECAY
                    return Easeable(Timeable(t.start, ds), i).e(de, rng=(rng[1], dv), to1=1)