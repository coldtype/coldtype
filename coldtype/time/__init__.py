from coldtype.time.timeable import Timing, Timeable, TimeableSet
from coldtype.time.timeline import Timeline
from coldtype.time.loop import Loop, LoopPhase
from coldtype.time.clip import Clip

class Frame():
    """
    Container for information about a frame

    Frame is the type of the first argument passed to all @animation rendering functions, usually abbreviated as ``f``, i.e.

    .. code:: python

        @animation()
        def render(f:Frame):
            pass
    
    (where `Frame` is an optional type-hint if you're looking to leverage autocomplete in your editor)
    """
    def __init__(self, i, animation):
        self.i = i #: index of the frame
        self.a = animation #: the animation (or subclass of animation) associated with the frame
    
    def adj(self, off):
        return Frame(self.i+off, self.a)
    
    def e(self, easefn="eeio", loops=0, rng=(0, 1), on=None, cyclic=True, to1=False):
        if not isinstance(easefn, str):
            loops = easefn
            easefn = "eeio"
        t = self.a.progress(self.i%self.a.duration, loops=loops, easefn=easefn, cyclic=cyclic, to1=to1)
        tl = t.loop // (2 if cyclic else 1)
        e = t.e
        if on:
            if tl not in on:
                e = 0
        ra, rb = rng
        if ra > rb:
            e = 1 - e
            rb, ra = ra, rb
        return ra + e*(rb - ra)
    
    def ce(self, clip_idx, easefn="eeio", loops=0, rng=(0, 1), cyclic=True, to1=False, out1=False):
        if not isinstance(easefn, str):
            loops = easefn
            easefn = "eeio"
        try:
            clip:Clip = self.a.t[clip_idx]
        except:
            return 0
        t = clip.progress(self.i%self.a.duration, loops=loops, easefn=easefn, cyclic=cyclic, to1=to1, out1=out1)
        e = t.e
        ra, rb = rng
        if ra > rb:
            e = 1 - e
            rb, ra = ra, rb
        return ra + e*(rb - ra)
    
    def ie(self, *args, **kwargs):
        return self.e(*args, **kwargs, rng=(1, 0))
    
    def last_render(self, modfn=lambda p: p):
        if not self.a.composites:
            raise Exception("set `composites=1` on your @animation")
        if self.a.last_result:
            return modfn(self.a.last_result.copy())
        else:
            return None