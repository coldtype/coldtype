from coldtype.helpers import loopidx, interp_dict
from coldtype.time.timeable import Timing, Timeable, TimeableSet
from coldtype.time.timeline import Timeline
from coldtype.time.loop import Loop, LoopPhase

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
    
    def e(self, easefn="eeio", loops=0, cyclic=True):
        if not isinstance(easefn, str):
            loops = easefn
            easefn = "eeio"
        return self.a.progress(self .i, loops=loops, easefn=easefn, cyclic=cyclic, to1=True).e
    
    def last_render(self, modfn=lambda p: p):
        if not self.a.composites:
            raise Exception("set `composites=1` on your @animation")
        if self.a.last_result:
            return modfn(self.a.last_result.copy())
        else:
            return None