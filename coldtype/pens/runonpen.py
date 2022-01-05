from collections.abc import Iterable

from fontTools.pens.recordingPen import RecordingPen

from coldtype.geometry import Rect
from coldtype.pens.mixins.PathopsMixin import PathopsMixin
from coldtype.runon.runon import Runon

from coldtype.pens.mixins.StylingMixin import StylingMixin
from coldtype.pens.mixins.LayoutMixin import LayoutMixin
from coldtype.pens.mixins.DrawingMixin import DrawingMixin

class RunonPen(Runon,
    StylingMixin,
    LayoutMixin,
    DrawingMixin,
    PathopsMixin,
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
    
    def __init__(self, *vals):
        # r = None

        # if isinstance(value, RunonPen):
        #     els = [value]
        #     value = RecordingPen()
        # elif isinstance(value, Iterable):
        #     els = value
        #     value = RecordingPen()
        # elif isinstance(value, Rect):
        #     r = value
        #     value = None
        # elif value is None:
        #     value = RecordingPen()
        
        super().__init__(*vals)

        # if r:
        #     self.rect(r)

    def reset_val(self):
        self._val = RecordingPen()
        return self
    
    def normalize_val(self, val):
        return val
    
    def val_present(self):
        return self._val and len(self._val.value) > 0
    
    def printable_val(self):
        if self.val_present():
            return f"RecordingPen({len(self._val.value)})"
    
    def printable_data(self):
        out = {}
        exclude = ["_last_align_rect"]
        for k, v in self._data.items():
            if k not in exclude:
                out[k] = v
        return out

    def style(self, style="_default"):
        """for compatibility with defaults and grouped-stroke-properties from DATPen"""
        st = {**super().style(style)}
        return self.groupedStyle(st)
    
    def pen(self):
        """collapse and combine into a single vector"""
        if len(self) == 0:
            return self
        
        frame = self.ambit()
        self.collapse()

        for el in self._els:
            el._val.replay(self._val)
            #self._val.record(el._val)

        self._attrs = {**self._els[0]._attrs, **self._attrs}
            
        self.data(frame=frame)
        self._els = []
        return self

def runonCast():
    def _runonCast(p):
        return RunonPen.FromPens(p)
    return _runonCast