
from fontTools.pens.recordingPen import RecordingPen

from coldtype.geometry import Rect
from coldtype.runon.runon import Runon

from coldtype.pens.mixins.StylingMixin import StylingMixin
from coldtype.pens.mixins.LayoutMixin import LayoutMixin
from coldtype.pens.mixins.DrawingMixin import DrawingMixin

class RunonPen(Runon,
    StylingMixin,
    LayoutMixin,
    DrawingMixin
    ):
    def FromPens(pens):
        if hasattr(pens, "_pens"):
            out = RunonPen()
            for p in pens:
                out.append(RunonPen.FromPens(p))
        else:
            p = pens
            rp = RecordingPen()
            p.replay(rp)
            out = RunonPen(rp)
            
            attrs = p.attrs.get("default", {})
            if "fill" in attrs:
                out.f(attrs["fill"])
            if "stroke" in attrs:
                out.s(attrs["stroke"]["color"])
                out.sw(attrs["stroke"]["weight"])

            # TODO also the rest of the styles

            if hasattr(pens, "_frame"):
                out.data(frame=pens._frame)
            if hasattr(pens, "glyphName"):
                out.data(glyphName=pens.glyphName)
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
        elif value is None:
            value = RecordingPen()
        
        super().__init__(value=value, els=els, data=data, attrs=attrs)

        if r:
            self.rect(r)
    
    def printable_val(self):
        if self._val:
            return f"RecordingPen({len(self._val.value)})"

    def style(self, style="_default"):
        """for compatibility with defaults and grouped-stroke-properties from DATPen"""
        st = {**super().style(style)}
        return self.groupedStyle(st)


def runonCast():
    def _runonCast(p):
        return RunonPen.FromPens(p)
    return _runonCast