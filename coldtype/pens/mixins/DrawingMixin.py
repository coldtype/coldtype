import math

from pathlib import Path
from json import loads, dumps

from coldtype.geometry import Rect, Line, Point


class DrawingMixin():
    def moveTo(self, p0):
        self._val.moveTo(p0)
        return self

    def lineTo(self, p1):
        if len(self._val.value) == 0:
            self._val.moveTo(p1)
        else:
            self._val.lineTo(p1)
        return self

    def qCurveTo(self, *points):
        self._val.qCurveTo(*points)
        return self

    def curveTo(self, *points):
        self._val.curveTo(*points)
        return self

    def closePath(self):
        self._val.closePath()
        return self

    def endPath(self):
        self._val.endPath()
        return self
    
    def replay(self, pen):
        self._val.replay(pen)
        return self
    
    def record(self, pen):
        """Play a pen into this pen, meaning that pen will be added to this one’s value."""
        if len(pen) > 0:
            for el in pen._els:
                self.record(el._val)
        elif pen:
            if isinstance(pen, Path):
                self.withJSONValue(pen)
            else:
                pen.replay(self._val)
        return self
    
    def withJSONValue(self, path):
        self._val.value = loads(Path(path)
            .expanduser()
            .read_text())
        return self

    def rect(self, rect):
        """Rectangle primitive — `moveTo/lineTo/lineTo/lineTo/closePath`"""
        self.moveTo(rect.point("SW").xy())
        self.lineTo(rect.point("SE").xy())
        self.lineTo(rect.point("NE").xy())
        self.lineTo(rect.point("NW").xy())
        self.closePath()
        return self
    
    r = rect
    
    def roundedRect(self, rect, hr, vr=None):
        """Rounded rectangle primitive"""
        if vr is None:
            vr = hr
        l, b, w, h = Rect(rect)
        r, t = l + w, b + h
        K = 4 * (math.sqrt(2)-1) / 3
        circle = hr == 0.5 and vr == 0.5
        if hr <= 0.5:
            hr = w * hr
        if vr <= 0.5:
            vr = h * vr
        self.moveTo((l + hr, b))
        if not circle:
            self.lineTo((r - hr, b))
        self.curveTo((r+hr*(K-1), b), (r, b+vr*(1-K)), (r, b+vr))
        if not circle:
            self.lineTo((r, t-vr))
        self.curveTo((r, t-vr*(1-K)), (r-hr*(1-K), t), (r-hr, t))
        if not circle:
            self.lineTo((l+hr, t))
        self.curveTo((l+hr*(1-K), t), (l, t-vr*(1-K)), (l, t-vr))
        if not circle:
            self.lineTo((l, b+vr))
        self.curveTo((l, b+vr*(1-K)), (l+hr*(1-K), b), (l+hr, b))
        self.closePath()
        return self
    
    rr = roundedRect
    
    def oval(self, rect):
        """Oval primitive"""
        self.roundedRect(rect, 0.5, 0.5)
        return self
    
    o = oval

    def line(self, points, moveTo=True, endPath=True):
        """Syntactic sugar for `moveTo`+`lineTo`(...)+`endPath`; can have any number of points"""
        if isinstance(points, Line):
            points = list(points)
        if len(points) == 0:
            return self
        if len(self._val.value) == 0 or moveTo:
            self.moveTo(points[0])
        else:
            self.lineTo(points[0])
        for p in points[1:]:
            self.lineTo(p)
        if endPath:
            self.endPath()
        return self
    
    l = line
    
    def hull(self, points):
        """Same as `DraftingPen.line` but calls closePath instead of endPath`"""
        self.moveTo(points[0])
        for pt in points[1:]:
            self.lineTo(pt)
        self.closePath()
        return self