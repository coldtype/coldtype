# WARNING

from copy import deepcopy

from fontTools.pens.recordingPen import RecordingPen
from fontTools.pens.reverseContourPen import ReverseContourPen
from coldtype.color import Color, normalize_color

from coldtype.geometry import Rect, Point, txt_to_edge
from coldtype.runon.runon import Runon

from coldtype.runon.scaffold import Scaffold

# IMPORTS

class P(Runon):
    """
    P stands for Path (or Pen)
    """
    def FromPens(pens):
        if hasattr(pens, "_pens"):
            out = P().data(**pens.data)
            for p in pens:
                out.append(P.FromPens(p))
        elif hasattr(pens, "_els") and len(pens._els) > 0:
            out = pens
        elif hasattr(pens, "_val") and pens.val_present():
            out = pens
        else:
            p = pens
            rp = RecordingPen()
            p.replay(rp)
            out = P(rp)
            
            attrs = p.attrs.get("default", {})
            if "fill" in attrs:
                out.f(attrs["fill"])
            if "stroke" in attrs:
                out.s(attrs["stroke"]["color"])
                out.sw(attrs["stroke"]["weight"])

            # TODO also the rest of the styles

            out.data(**pens.data)

            if hasattr(pens, "_frame"):
                out.data(frame=pens._frame)
            if hasattr(pens, "glyphName"):
                out.data(glyphName=pens.glyphName)
        return out
    
    def __init__(self, *vals, **kwargs):
        prenorm = [v.rect if isinstance(v, Scaffold) else v for v in vals]

        super().__init__(*prenorm)

        if isinstance(self._val, RecordingPen):
            pass
        elif isinstance(self._val, Rect):
            r = self._val
            self._val = RecordingPen()
            self.rect(r)
        elif isinstance(self._val, Point):
            p = self._val
            self._val = RecordingPen()
            self.rect(Rect.FromCenter(p, 20))
        else:
            raise Exception("Can’t understand _val", self._val)

        # more backwards compat
        for k, v in kwargs.items():
            if k == "fill":
                self.f(v)
            elif k == "stroke":
                self.s(v)
            elif k == "strokeWidth":
                self.sw(v)
            elif k == "image":
                self.img(**v)
            elif k == "shadow":
                self.shadow(**v)
            else:
                raise Exception("Invalid __init__ kwargs", k)

    def reset_val(self):
        super().reset_val()
        self._val = RecordingPen()
        return self
    
    def val_present(self):
        return self._val is not None and len(self._val.value) > 0
    
    def copy_val(self, val):
        copy = RecordingPen()
        if self.val_present():
            copy.value = deepcopy(self._val.value)
        return copy
    
    def printable_val(self):
        if self.val_present():
            return f"{len(self._val.value)}mvs"
    
    def printable_data(self):
        out = {}
        exclude = ["_last_align_rect", "_notebook_shown"]
        for k, v in self._data.items():
            if k not in exclude:
                out[k] = v
        return out
    
    def normalize_attr_value(self, k, v):
        if k == "fill" and not isinstance(v, Color):
            return normalize_color(v)
        else:
            return super().normalize_attr_value(k, v)

    def style(self, style="_default"):
        """for backwards compatibility with defaults and grouped-stroke-properties"""
        st = {**super().style(style)}
        return self.groupedStyle(st)
    
    def unframe(self):
        def _unframe(el, _, __):
            el.data(frame=None)

        return self.walk(_unframe)
    
    def frame(self, fn_or_rect):
        if isinstance(fn_or_rect, Rect):
            self.data(frame=fn_or_rect)
        elif callable(fn_or_rect):
            self.data(frame=fn_or_rect(self))
        return self
    
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
    
    def down(self):
        return self.pen()
    
    def pens(self):
        if self.val_present():
            return self.ups()
        else:
            return self

    # multi-use overrides
    
    def reverse(self, recursive=False, winding=True):
        """Reverse elements; if pen value present, reverse the winding direction of the pen."""
        if winding and self.val_present():
            if self.unended():
                self.closePath()
            dp = RecordingPen()
            rp = ReverseContourPen(dp)
            self.replay(rp)
            self._val.value = dp.value
            return self

        return super().reverse(recursive=recursive, winding=winding)
    
    def index(self, idx, fn=None):
        if not self.val_present():
            return super().index(idx, fn)
        
        return self.mod_contour(idx, fn)
    
    def indices(self, idxs, fn=None):
        if not self.val_present():
            return super().indices(idxs, fn)

        def apply(idx, x, y):
            if idx in idxs:
                return fn(Point(x, y))
        
        return self.map_points(apply)
    
    def wordPens(self, pred=lambda x: x.glyphName == "space"):
        def _wp(p):
            return (p
                .split(pred)
                .map(lambda x: x
                    .data(word="/".join([p.glyphName for p in x]))
                    .pen()))
        
        d = self.depth()
        if d == 1:
            return _wp(self)
        
        out = type(self)()
        for pen in self:
            out.append(_wp(pen))
        return out
    
    def interpolate(self, value, other, frame=False):
        if len(self.v.value) != len(other.v.value):
            raise Exception("Cannot interpolate / diff lens")
        vl = []
        for idx, (mv, pts) in enumerate(self.v.value):
            ipts = []
            for jdx, p in enumerate(pts):
                pta = Point(p)
                try:
                    ptb = Point(other.v.value[idx][-1][jdx])
                except IndexError:
                    print(">>>>>>>>>>>>> Can’t interpolate", idx, mv, "///", other.v.value[idx])
                    raise IndexError
                ipt = pta.interp(value, ptb)
                ipts.append(ipt)
            vl.append((mv, ipts))
        
        np = type(self)()
        np.v.value = vl

        if frame:
            af = self.data("frame")
            bf = other.data("frame")
            ff = af.interp(value, bf)
            np.data(frame=ff)

        return np
    
    def replaceGlyph(self, glyphName, replacement, limit=None):
        return self.replace(lambda p: p.glyphName == glyphName,
            lambda p: (replacement(p) if callable(replacement) else replacement)
                .translate(*p.ambit().xy()))
    
    def findGlyph(self, glyphName, fn=None):
        return self.find(lambda p: p.glyphName == glyphName, fn)
    
    def _repr_html_(self):
        #if self.data("_notebook_shown"):
        #    return None
        
        from coldtype.notebook import show, DEFAULT_DISPLAY
        self.ch(show(DEFAULT_DISPLAY, tx=1, ty=1))
        return None
    
    def text(self,
        text:str,
        style,
        frame:Rect,
        x="mnx",
        y="mny",
        ):
        self.rect(frame)
        self.data(
            text=text,
            style=style,
            align=(txt_to_edge(x), txt_to_edge(y)))
        return self
    
    # backwards compatibility (questionable if should exist)

    def reversePens(self):
        """for backwards compatibility"""
        return self.reverse(recursive=False)
    
    rp = reversePens

    def vl(self, value):
        self.v.value = value
        return self
    
    @property
    def _pens(self):
        return self._els
    
    @property
    def value(self):
        return self.v.value

    @property
    def glyphName(self):
        return self.data("glyphName")
    
    def ffg(self, glyphName, fn=None, index=0):
        return self.find_({"glyphName":glyphName}, fn, index)
    
    @staticmethod
    def Enumerate(enumerable, enumerator):
        return P().enumerate(enumerable, enumerator)
    
    def addFrame(self, frame):
        return self.data(frame=frame)
    
    def xAlignToFrame(self):
        return self.align(self.data("frame"), y=None)
    
    def pvl(self):
        for idx, (_, pts) in enumerate(self.v.value):
            if len(pts) > 0:
                self.v.value[idx] = list(self.v.value[idx])
                self.v.value[idx][-1] = [Point(p) for p in self.v.value[idx][-1]]
        return self
    
    def dots(self, radius=4):
        """(Necessary?) Create circles at moveTo commands"""
        dp = type(self)()
        for t, pts in self.v.value:
            if t == "moveTo":
                x, y = pts[0]
                dp.oval(Rect((x-radius, y-radius, radius, radius)))
        self.v.value = dp.v.value
        return self

# MIXINS

def runonCast():
    def _runonCast(p):
        return P.FromPens(p)
    return _runonCast

PS = P
DATPens = P
DATPen = P
DPS = P
DP = P