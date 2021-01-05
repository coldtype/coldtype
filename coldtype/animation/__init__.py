from coldtype.helpers import loopidx, interp_dict
from coldtype.animation.timeable import Timing, Timeable, TimeableSet
from coldtype.animation.timeline import Timeline
from coldtype.animation.loop import Loop, LoopPhase

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