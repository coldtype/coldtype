import math

from fontTools.pens.boundsPen import BoundsPen
from fontTools.misc.transform import Transform
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.recordingPen import RecordingPen

from coldtype.geometry import Point, Rect, align
from coldtype.interpolation import norm


class LayoutMixin():
    def bounds(self):
        """Calculate the exact bounds of this shape, using a BoundPen"""
        b = Rect(0, 0, 0, 0)
        if self._val:
            try:
                cbp = BoundsPen(None)
                self._val.replay(cbp)
                mnx, mny, mxx, mxy = cbp.bounds
                b = Rect((mnx, mny, mxx - mnx, mxy - mny))
            except:
                pass
        
        if len(self._els) > 0:
            b = self._els[0].bounds()
            for el in self._els[1:]:
                b = b.union(el.bounds())
        
        return b
    
    def _normT(self, th, tv, t):
        if t is not None:
            th = bool(int(t))
            if th:
                tv = int((t-1)*10) == 1
            else:
                tv = int(t)*10 == 1
        else:
            th, tv = th, tv
        return th, tv
    
    def empty(self):
        return len(self._val.value) == 0
    
    def ambit(self, th=False, tv=False, t=None):
        """Get the calculated rect boundary;
        `th` means `(t)rue (h)orizontal`;
        `ty` means `(t)rue (v)ertical`;
        passing either ignores a non-bounds-derived frame
        in either dimension"""
        
        th, tv = self._normT(th, tv, t)
        f = self._data.get("frame", None)

        # true bounds
        if th and tv:
            return self.bounds()
        
        # true no-bounds
        elif not th and not tv and f:
            return f
        
        # partial bounds
        elif f and self._val:
            if self.empty():
                if th:
                    f = f.setw(0)
                elif tv:
                    f = f.seth(0)
                return f
            else:
                b = self.bounds()
                if th:
                    return Rect(b.x, f.y, b.w, f.h)
                else:
                    return Rect(f.x, b.y, f.w, b.h)
        
        # pass-to-els
        elif len(self._els) > 0:
            try:
                union = self._els[0].ambit(th=th, tv=tv)
                for p in self._els[1:]:
                    a = p.ambit(th=th, tv=tv)
                    if a.x == 0 and a.y == 0 and a.w == 0 and a.h == 0:
                        continue
                    union = union.union(a)
                return union
            except Exception as _:
                return Rect(0,0,0,0)
        
        # catch-all
        return self.bounds()
        
        # if f or self._val:
        #     if (th or tv) and not self.empty():
        #         b = self.bounds()
        #         if th and tv:
        #             return b
        #         elif th:
        #             return Rect(b.x, f.y, b.w, f.h)
        #         else:
        #             return Rect(f.x, b.y, f.w, b.h)
        #     else:
        #         if self.empty():
        #             if th:
        #                 f = f.setw(0)
        #             elif tv:
        #                 f = f.seth(0)
        #             return f
        #         return f
        # elif :
        #     return self.bounds()
    
    def align(self,
        rect,
        x="mdx",
        y="mdy",
        th=True,
        tv=False,
        transformFrame=True,
        h=None,
        return_offset=False
        ):
        """Align this pen to another rect, defaults to the center;
        `th` means true-horizontal (i.e. will disregard any invisible 'frame'
        set on the pen (as in the case of glyphs returned from StSt/Glyphwise));
        `tv` means true-vertical, which is the same but for the vertical dimension"""
        
        r = self.ambit(th, tv)

        if h is not None:
            r = r.seth(h)
        
        self.data(_last_align_rect=rect)
        
        offset = align(r, rect, x, y)
        self.translate(*offset,
            transformFrame=transformFrame)
        
        if return_offset:
            return offset
        else:
            return self
    
    å = align

    def xalign(self, rect=None, x="centerx", th=1, tv=0):
        if callable(rect):
            rect = rect(self)
        self.align(rect, x=x, y=None, th=th, tv=tv)
        return self
    
    xå = xalign

    def _normPoint(self, point=None, th=0, tv=0, **kwargs):
        th, tv = self._normT(th, tv, kwargs.get("t"))

        if "pt" in kwargs:
            point = kwargs["pt"]
        
        a = self.ambit(th=th, tv=tv)
        if point is None:
            return a.pc
        elif point == 0:
            return a.psw
        elif point is False:
            return Point(0, 0)
        elif isinstance(point, str):
            if point.startswith("th"):
                a = self.ambit(th=1, tv=0)
                point = point[2:]
            elif point.startswith("tv"):
                a = self.ambit(th=0, tv=1)
                point = point[2:]
            elif point.startswith("t"):
                a = self.ambit(th=1, tv=1)
                point = point[1:]
            return a.point(point)
        elif not (isinstance(point[1], int) or isinstance(point[1], float)) and hasattr(self, "_pens"):
            return self[point[0]]._normPoint(point[1])
        else:
            return Point(point)
    
    def transform(self, transform, transformFrame=True):
        """Perform an arbitrary transformation on the pen, using the fontTools `Transform` class."""

        if self._val:
            op = RecordingPen()
            tp = TransformPen(op, transform)
            self._val.replay(tp)
            self._val.value = op.value
        
        f = self._data.get("frame")
        if transformFrame and f:
            self.data(frame=f.transform(transform))
        
        for p in self._els:
            p.transform(transform, transformFrame=transformFrame)
        
        img = self.img()
        if img:
            img["rect"] = img["rect"].transform(transform)
        
        return self
    
    def translate(self, x, y=None, transformFrame=True):
        """Translate this shape by `x` and `y` (pixel values)."""
        if y is None:
            y = x
        return self.transform(Transform(1, 0, 0, 1, x, y), transformFrame=transformFrame)
    
    offset = translate
    t = translate
    
    def zero(self, th=0, tv=0):
        x, y, _, _ = self.ambit(th=th, tv=tv)
        self.translate(-x, -y)
        return self
    
    def centerPoint(self, rect, pt, interp=1, th=1, tv=0, **kwargs):
        if "i" in kwargs:
            interp = kwargs["i"]
        
        x, y = self._normPoint(pt, th=th, tv=tv, **kwargs)
        return self.translate(norm(interp, 0, rect.w/2-x), norm(interp, 0, rect.h/2-y))
    
    def skew(self, x=0, y=0, point=None, th=1, tv=0, **kwargs):
        t = Transform()
        px, py = self._normPoint(point, th, tv, **kwargs)
        t = t.translate(px, py)
        t = t.skew(x, y)
        t = t.translate(-px, -py)
        return self.transform(t)
    
    def rotate(self, degrees, point=None, th=1, tv=1, **kwargs):
        """Rotate this shape by a degree (in 360-scale, counterclockwise)."""
        t = Transform()
        x, y = self._normPoint(point, th, tv, **kwargs)
        t = t.translate(x, y)
        t = t.rotate(math.radians(degrees))
        t = t.translate(-x, -y)
        return self.transform(t, transformFrame=False)
    
    rt = rotate
    
    def scale(self, scaleX, scaleY=None, point=None, th=1, tv=0, **kwargs):
        """Scale this shape by a percentage amount (1-scale)."""
        t = Transform()
        x, y = self._normPoint(point, th, tv, **kwargs)
        if point is not False:
            t = t.translate(x, y)
        t = t.scale(scaleX, scaleY or scaleX)
        if point is not False:
            t = t.translate(-x, -y)
        return self.transform(t)
    
    def scaleToRect(self, rect, preserveAspect=True, shrink_only=False):
        """Scale this shape into a `Rect`."""
        bounds = self.bounds()
        h = rect.w / bounds.w
        v = rect.h / bounds.h
        if preserveAspect:
            scale = h if h < v else v
            if shrink_only and scale >= 1:
                return self
            return self.scale(scale)
        else:
            if shrink_only and (h >= 1 or v >= 1):
                return self
            return self.scale(h, v)
    
    def scaleToWidth(self, w, shrink_only=False):
        """Scale this shape horizontally"""
        b = self.bounds()
        if shrink_only and b.w < w:
            return self
        else:
            return self.scale(w / self.bounds().w, 1)
    
    def scaleToHeight(self, h, shrink_only=False):
        """Scale this shape horizontally"""
        b = self.bounds()
        if shrink_only and b.h < h:
            return self
        return self.scale(1, h / self.bounds().h)