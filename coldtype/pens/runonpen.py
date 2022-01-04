
from fontTools.pens.recordingPen import RecordingPen

from coldtype.geometry import Rect
from coldtype.runon.runon import Runon

from coldtype.pens.mixins.StylingMixin import StylingMixin
from coldtype.pens.mixins.LayoutMixin import LayoutMixin

class RunonPen(Runon,
    StylingMixin,
    LayoutMixin
    ):
    def FromPens(pens):
        if hasattr(pens, "_pens"):
            out = RunonPen()
            for p in pens:
                rp = RecordingPen()
                p.replay(rp)
                rrp = RunonPen(rp)
                if p._frame:
                    rrp.data(frame=p._frame)
                out.append(rrp)
        else:
            out = RunonPen(pens)
            if hasattr(pens, "_frame"):
                out.data(frame=pens._frame)
        return out
    
    def __init__(self,
        value=None,
        els=None,
        data=None,
        attrs=None
        ):
        r = None
        if isinstance(value, Rect):
            r = value
            value = None
        
        super().__init__(value=value, els=els, data=data, attrs=attrs)

        if r:
            self.rect(r)
    
    def printable_val(self):
        if self._val:
            return f"RecordingPen({len(self._val.value)})"

    def style(self, style="_default"):
        st = {**super().style(style)}
        return self.groupedStyle(st)