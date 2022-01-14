from coldtype.time.timeable import Timeable, Easeable
from coldtype.time.timeline import Timeline


class Frame(Easeable):
    """
    Container for information about a frame

    Frame is the type of the first argument passed to all @animation rendering functions, usually abbreviated as ``f``, i.e.

    .. code:: python

        @animation()
        def render(f:Frame):
            pass
    
    (where `Frame` is an optional type-hint if you're looking to leverage autocomplete in your editor)
    """
    def __init__(self, i, anim):
        if isinstance(anim, Timeline):
            self.i = i % anim.duration
        else:
            self.i = i % anim.t.duration
        self.a = anim
    
    def adj(self, off):
        return Frame(self.i+off, self.a)
    
    # Easeable interface

    @property
    def t(self) -> Timeline: return self.a.t if hasattr(self.a, "t") else self.a
    
    @property
    def _ts(self): return None

    @property
    def autowrap(self): return True
    
    def last_render(self, modfn=lambda p: p):
        if not self.a.composites:
            raise Exception("set `composites=1` on your @animation")
        if self.a.last_result:
            return modfn(self.a.last_result.copy())
        else:
            return None
    
    lastRender = last_render