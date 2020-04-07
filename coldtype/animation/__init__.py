import math
from coldtype.geometry import Rect
from coldtype.animation.easing import ease
from coldtype.renderable import renderable, RenderPass


class Frame():
    def __init__(self, i, animation):
        self.i = i
        self.a = animation

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


class Loop(Timeable):
    def __init__(self, duration, segment_count, transition_length, loop=1):
        self.start = 0
        self.end = duration
        self.duration = duration
        self.timeables = []
        self.transitions = []

        idx = 0
        segment_count = int(math.floor(segment_count))
        segment_length = duration / segment_count
        segment_frames = int(math.floor(segment_length))
        leftover = duration % segment_frames

        for x in range(0, self.duration, segment_frames):
            if idx >= segment_count:
                continue

            start = x
            end = x + segment_frames
            if idx == segment_count-1:
                end += leftover
            
            self.timeables.append(Timeable(start, end, index=idx))

            if idx < segment_count - 1:
                tstart = end-transition_length
                tend = end+transition_length
                self.transitions.append(Timeable(tstart, tend, index=idx))
            
            idx += 1
        
        if loop:
            self.transitions.insert(0, Timeable(-transition_length, transition_length, index=-1))
            self.transitions.append(Timeable(self.duration-transition_length, self.duration+transition_length, index=idx-1))
    
    def current_clip(self, i):
        for t in self.timeables:
            if t.now(i):
                return t

    def current_transition(self, i):
        for t in self.transitions:
            if t.now(i):
                return t

    def current(self, i):
        clip = self.current_clip(i)
        transition = self.current_transition(i)
        if transition:
            return True, transition
        else:
            return False, clip

    def current_on_loop(self, i):
        if i < 0:
            i = self.duration + i
        is_transition, timeable = self.current(i)
        return is_transition, i, timeable


class animation(renderable, Timeable):
    def __init__(self, rect=(1080, 1080), duration=10, storyboard=[0], **kwargs):
        super().__init__(**kwargs)
        self.rect = Rect(rect)
        self.r = self.rect
        self.start = 0
        self.end = duration
        self.duration = duration
        self.storyboard = storyboard
    
    def __call__(self, func):
        self.func = func
        return self
    
    def folder(self):
        return self.func.__name__ # TODO necessary?
    
    def passes(self, mode):
        frames = self.storyboard
        if mode == "all":
            frames = list(range(0, self.duration))
        return [RenderPass(self.func, "{:04d}".format(i), [Frame(i, self)]) for i in frames]