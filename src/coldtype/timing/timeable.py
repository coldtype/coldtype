from dataclasses import dataclass
from coldtype.interpolation import lerp, interp_dict
from coldtype.runon.path import P
from coldtype.timing.easing import ease, ez, applyRange
from copy import copy
import math


class Timeable():
    """
    Abstract base class for anything with a concept of `start` and `end`/`duration`

    Implements additional methods to make it easier to work with time-based concepts
    """
    def __init__(self,
        start,
        end,
        index=0,
        name=None,
        data={},
        timeline=None,
        track=None,
        ):
        self.start = start
        self.end = end
        self.idx = index
        self.name = name
        self.feedback = 0
        self.data = data
        self.timeline = timeline
        self.track = int(track) if track else 0
    
    @property
    def duration(self):
        return self.end - self.start
    
    def __repr__(self):
        if hasattr(self, "name") and self.name:
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
        if self.start == self.end:
            return i == self.start
        else:
            return self.start <= i < self.end

    def _normalize_fi(self, fi):
        if hasattr(self, "timeline") and self.timeline:
            if self.end > self.timeline.duration and fi < self.start:
                return fi + self.timeline.duration
        return fi

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

    def at(self, i, every=None) -> "Easeable":
        if every:
            i = (i//every)*every
        return Easeable(self, i)


@dataclass
class EaseableTiming():
    t: float = 0
    i: int = -1
    loopidx: int = 0


class Easeable():
    def __init__(self,
        t:Timeable,
        i:int
        ):
        self.t:Timeable = t
        self.i:int = i

        self._ts = False
        if not isinstance(t, Timeable):
            self._ts = True
    
    @property
    def autowrap(self):
        return False
    
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
    
    def every(self, i) -> "Easeable":
        self.i = (self.i//i)*i
        return self
    
    def inset(self, start=0, end=0) -> "Easeable":
        return Easeable(Timeable(
            start=self.t.start + start,
            end=self.t.end - end,
            name=self.t.name,
            data=self.t.data,
            track=self.t.track,
            timeline=self.t.timeline,
        ), self.i)
    
    @property
    def name(self):
        if self._ts:
            return "/".join([t.name for t in self.t])
        else:
            return self.t.name
    
    @property
    def idx(self):
        if self._ts:
            if len(self.t) > 0:
                return self.t[0].idx
            else:
                return -1
        else:
            return self.t.idx
    
    def index(self):
        if self._ts:
            return sum([self.i >= t.start for t in self.t]) - 1
        else:
            return int(self.i >= self.t.start) - 1
        
    def on(self, end=None):
        if self._ts:
            return bool(max([Easeable(t, self.i).on(end=end) for t in self.t]))
        
        if end is None:
            end = self.t.end

        if self.t.start == end:
            return self.i == self.t.start
        else:
            return self.t.start <= self.i < end
    
    def now(self):
        if not self._ts:
            if self.on():
                return self
            else:
                return None
        
        for t in self.t:
            e = Easeable(t, self.i)
            if e.on():
                return e
        
        return None
    
    def past(self):
        return self.on(end=10000000000)
    
    def tv(self,
        loops=0,
        cyclic=True,
        to1=True,
        choose=max,
        wrap=None,
        find=False,
        clip=True
        ):
        if wrap is None and self.autowrap:
            wrap = True

        if self._ts:
            es = [Easeable(t, self.i).tv(loops, cyclic, to1).t for t in self.t]
            if len(es) == 0:
                e = 0
            else:
                e = choose(es)
            if find is False:
                return EaseableTiming(e)
            else:
                try:
                    return EaseableTiming(e, es.index(e))
                except:
                    return EaseableTiming(e, -1)
                # chosen = [(i, 1 if x == e else 0) for i, x in enumerate(es)]
                # if e > 0:
                #     return EaseableTiming(e, chosen[-1][0])
                # else:
                #     return EaseableTiming(e, chosen[0][0])

        t, i = self.t, self.i
        if wrap:
            i = i % self.t.duration
        else:
            i = self.i

        if clip and i < t.start:
            return EaseableTiming(0)
        elif clip and i > t.end:
            if loops % 2 == 0:
                return EaseableTiming(1)
            else:
                return EaseableTiming(0)
        else:
            d = t.duration
            if to1:
                d = d - 1
            
            v = (i - t.start) / d
            if loops == 0:
                return EaseableTiming(max(0, min(1, v)) if clip else v)
            else:
                loop_t, loop_index = self.t._loop(v, times=loops, cyclic=cyclic, negative=False)
                return EaseableTiming(max(0, min(1, loop_t)) if clip else v, -1, loop_index)

    def e(self,
        easefn="eeio",
        loops=1,
        rng=(0, 1),
        on=None, # TODO?
        cyclic=True,
        to1=False,
        wrap=None,
        choose=max,
        find=False,
        loop_info=False,
        **kwargs
        ):
        rng = self._normRange(rng, **kwargs)
        
        if (not isinstance(easefn, str)
            and not isinstance(easefn, P)
            and not type(easefn).__name__ == "Glyph"):
            loops = easefn
            easefn = "eeio"
        
        tv = self.tv(loops, cyclic, to1, choose, wrap, find=True)
        
        ev = ez(tv.t, easefn, cyclic=cyclic, rng=rng)
        if find:
            return ev, tv.i
        elif loop_info:
            return ev, tv.loopidx
        else:
            return ev
    
    def ec(self, easefn="eeio", rng=(0, 1)):
        """
        (e)asing-(c)umulative — for performing partial
        animations that accumulate over time, i.e. keys
        on a timeline `[0 ]   [0   ]` will be added together,
        so the "final" value of those 0's (`.ki(0).ec("l")`)
        will be 2, not 1; use `rng` to define accumulation;
        max of range refers to max of each phase, not max
        of entire accumulation
        """
        if self._ts:
            _ec = 0
            for t in self.t:
                _ec += Easeable(t, self.i).e(easefn, 0, rng=rng)
            return _ec
        return self.e(easefn, 0, rng=rng)
    
    def interpDict(self, dicts, easefn, loops=0):
        v = self.tv(loops=loops).t
        vr = v*(len(dicts)-1)
        vf = math.floor(vr)
        v = vr-vf
        try:
            a, b = dicts[vf], dicts[vf+1]
            return interp_dict(ez(v, easefn), a, b)
        except IndexError:
            return dicts[vf]
    
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
        adsr=(5, 0, 0, 10),
        es=("eei", "qeio", "eeo"),
        rng=(0, 1),
        dv=None, # decay-value
        rs=False, # read-sustain
        find=False,
        **kwargs
        ):
        rng = self._normRange(rng, **kwargs)

        if self._ts:
            es = [Easeable(t, self.i).adsr(adsr, es, rng, dv, rs) for t in self.t]
            mx = self._maxRange(rng, es)
            if find:
                return mx, es.index(mx)
            else:
                return mx

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
            rv = Easeable(Timeable(ds, end), i+td).e(re, 0, rng=(dv, rng[0]), to1=1)

        if i < t.start: # ATTACK
            s = t.start - a
            out = self._maxRange(rng, [rv, Easeable(Timeable(t.start-a, t.start), i).e(ae, 0, rng=rng, to1=0)])
        elif i >= t.start:
            if i == t.start:
                out = rng[1]
            if i >= ds: # RELEASE
                out = Easeable(Timeable(ds, end), i).e(re, 0, rng=(dv, rng[0]), to1=1)
            else:
                if i >= t.start + d: # SUSTAIN
                    out = dv
                else: # DECAY
                    out = Easeable(Timeable(t.start, ds), i).e(de, 0, rng=(rng[1], dv), to1=1)
        
        if find:
            return out, 0
        else:
            return out