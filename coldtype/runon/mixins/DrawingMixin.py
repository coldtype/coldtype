import math

from pathlib import Path
from fontTools.pens.recordingPen import RecordingPen
from coldtype.geometry import Rect, Line, Point, Atom


class DrawingMixin():
    def _normPointSplat(self, p):
        if isinstance(p[0], Point):
            return p[0].xy()
        elif len(p) == 1:
            return p[0]
        else:
            return p

    def moveTo(self, *p):
        p = self._normPointSplat(p)
        self._val.moveTo(p)
        return self
    
    def m(self, *p):
        return self.moveTo(*p)

    def lineTo(self, *p):
        p = self._normPointSplat(p)
        if len(self._val.value) == 0:
            self._val.moveTo(p)
        else:
            self._val.lineTo(p)
        return self
    
    def l(self, *p):
        return self.lineTo(*p)

    def qCurveTo(self, *points):
        self._val.qCurveTo(*points)
        return self
    
    def q(self, *p):
        return self.qCurveTo(*p)

    def curveTo(self, *points):
        self._val.curveTo(*points)
        return self
    
    def c(self, *p):
        return self.curveTo(*p)

    def closePath(self):
        self._val.closePath()
        return self
    
    def cp(self):
        return self.closePath()

    def endPath(self):
        self._val.endPath()
        return self
    
    def ep(self):
        return self.endPath()
    
    def replay(self, pen):
        self._val.replay(pen)

        for el in self._els:
            el.replay(pen)
        return self
    
    def record(self, pen):
        """Play a pen into this pen, meaning that pen will be added to this one’s value."""
        if hasattr(pen, "value"):
            pen.replay(self._val)
            return self

        if len(pen) > 0:
            for el in pen._els:
                self.record(el._val)
        elif pen:
            if isinstance(pen, Path):
                self.withJSONValue(pen)
            else:
                pen.replay(self._val)
        return self
    
    def unended(self):
        if not self.val_present():
            return None

        if len(self._val.value) == 0:
            return True
        elif self._val.value[-1][0] not in ["endPath", "closePath"]:
            return True
        return False
    
    def fully_close_path(self):
        if not self.val_present():
            # TODO log noop?
            return self

        if self._val.value[-1][0] == "closePath":        
            start = self._val.value[0][-1][-1]
            end = self._val.value[-2][-1][-1]

            if start != end:
                self._val.value = self._val.value[:-1]
                self.lineTo(start)
                self.closePath()
        return self
    
    fullyClosePath = fully_close_path

    def rect(self, rect):
        """Rectangle primitive — `moveTo/lineTo/lineTo/lineTo/closePath`"""
        rect = Rect(rect)
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
        if isinstance(rect, Point):
            self.roundedRect(Rect.FromCenter(rect, 20, 20), 0.5, 0.5)
        else:
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
    
    def hull(self, points):
        """Same as `.line` but calls closePath instead of endPath`"""
        self.moveTo(points[0])
        for pt in points[1:]:
            self.lineTo(pt)
        self.closePath()
        return self
    
    def round(self):
        """Round the values of this pen to integer values."""
        return self.round_to(1)

    def round_to(self, rounding):
        """Round the values of this pen to nearest multiple of rounding."""
        def rt(v, mult):
            rndd = float(round(v / mult) * mult)
            if rndd.is_integer():
                return int(rndd)
            else:
                return rndd
        
        rounded = []
        for t, pts in self._val.value:
            _rounded = []
            for p in pts:
                if p:
                    x, y = p
                    _rounded.append((rt(x, rounding), rt(y, rounding)))
                else:
                    _rounded.append(p)
            rounded.append((t, _rounded))
        
        self._val.value = rounded
        return self
    
    # Compound curve mechanics
    
    def interpCurveTo(self, p1, f1, p2, f2, to, inset=0):
        a = Point(self._val.value[-1][-1][-1])
        d = Point(to)
        pl = Line(p1, p2).inset(inset)
        b = Line(a, pl.start).t(f1/100)
        c = Line(d, pl.end).t(f2/100)
        return self.curveTo(b, c, d)
    
    def ioc(self, pt, slope=0, fA=0, fB=85):
        return self.ioEaseCurveTo(pt, slope, fA, fB)

    def ioEaseCurveTo(self, pt, slope=0, fA=0, fB=85):
        a = Point(self._val.value[-1][-1][-1])
        d = Point(pt)
        box = Rect.FromMnMnMxMx([
            min(a.x, d.x),
            min(a.y, d.y),
            max(a.x, d.x),
            max(a.y, d.y)
        ])

        if a.y < d.y:
            line_vertical = Line(box.ps, box.pn)
        else:
            line_vertical = Line(box.pn, box.ps)

        angle = Line(a, d).angle() - line_vertical.angle()

        try:
            fA1, fA2 = fA
        except TypeError:
            fA1, fA2 = fA, fA
        
        try:
            fB1, fB2 = fB
        except TypeError:
            fB1, fB2 = fB, fB

        rotated = line_vertical.rotate(math.degrees(angle*(slope/100)))
        vertical = Line(rotated.intersection(box.es), rotated.intersection(box.en))

        if a.y > d.y:
            vertical = vertical.reverse()

        c1 = Line(a, vertical.start).t(fA1)
        c2 = Line(vertical.mid, vertical.start).t(fA1)
        self.lineTo(c1)
        self.curveTo(
            Line(c1, vertical.start).t(fB1),
            Line(c2, vertical.start).t(fB1),
            c2)
        c1 = Line(vertical.mid, vertical.end).t(fA2)
        c2 = Line(d, vertical.end).t(fA2)
        self.lineTo(c1)
        self.curveTo(
            Line(c1, vertical.end).t(fB2),
            Line(c2, vertical.end).t(fB2),
            c2)
        self.lineTo(d)
        return self
    
    def bxc(self, pt, point, factor=65, po=(0, 0), mods={}, flatten=False):
        return self.boxCurveTo(pt, point, factor, po, mods, flatten)
    
    def boxCurveTo(self, pt, point, factor=65, po=(0, 0), mods={}, flatten=False):
        #print("BOX", point, factor, pt, po, mods)

        if flatten:
            self.lineTo(pt)
            return self
        
        a = Point(self._val.value[-1][-1][-1])
        d = Point(pt)
        box = Rect.FromMnMnMxMx([
            min(a.x, d.x),
            min(a.y, d.y),
            max(a.x, d.x),
            max(a.y, d.y)
        ])

        try:
            f1, f2 = factor
        except TypeError:
            if isinstance(factor, Atom):
                f1, f2 = (factor[0], factor[0])
            else:
                f1, f2 = (factor, factor)

        if isinstance(point, str):
            #print("POINT", point)
            if point == "cx": # ease-in-out
                if a.y < d.y:
                    p1 = box.pse
                    p2 = box.pnw
                elif a.y > d.y:
                    p1 = box.pne
                    p2 = box.psw
                else:
                    p1 = p2 = a.interp(0.5, d)
            elif point == "e": # ease-in
                if a.y < d.y:
                    p1 = p2 = box.pse
                elif a.y > d.y:
                    p1 = p2 = box.pne
                else:
                    p1 = p2 = a.interp(0.5, d)
            elif point == "w": # ease-out
                if a.y < d.y:
                    p1 = p2 = box.pnw
                elif a.y > d.y:
                    p1 = p2 = box.psw
                else:
                    p1 = p2 = a.interp(0.5, d)
            else:
                if "," in point:
                    pt1, pt2 = [x.strip() for x in point.split(",")]
                    p1 = box.point(pt1)
                    p2 = box.point(pt2)
                else:
                    p = box.point(point)
                    p1, p2 = (p, p)
        elif isinstance(point, Point):
            p1, p2 = point, point
        else:
            p1, p2 = point
            p1 = box.point(p1)
            p2 = box.point(p2)
        
        p1 = p1.offset(*po)
        p2 = p2.offset(*po)
        
        b = a.interp(f1, p1)
        c = d.interp(f2, p2)

        mb = mods.get("b")
        mc = mods.get("c")
        if mb:
            b = mb(b)
        elif mc:
            c = mc(c)
        
        self.curveTo(b, c, d)
        return self
    
    def mirror(self, y=0, point=None):
        s = (1, -1) if y else (-1, 1)
        if point == 0:
            point = (0, 0)
        
        return (self.layer(1,
            lambda p: p.scale(*s, point=point or self.ambit().psw)))
    
    def mirrorx(self, point=None):
        return self.mirror(y=0, point=point)
    
    def mirrory(self, point=None):
        return self.mirror(y=1, point=point)
    
    def pattern(self, rect, clip=False):
        dp_copy = self.copy()
        #dp_copy.value = self.value

        for y in range(-1, 1):
            for x in range(-1, 1):
                dpp = type(self)()
                dp_copy.replay(dpp)
                dpp.translate(rect.w*x, rect.h*y)
                dpp.replay(self)
        
        self.translate(rect.w/2, rect.h/2)
        if clip:
            clip_box = type(self)().rect(rect)
            return self.intersection(clip_box)
        return self
    
    def withRect(self, rect, fn):
        r = Rect(rect)
        return fn(r, self).data(frame=r)
    
    def gridlines(self, rect, x=20, y=None, absolute=False):
        """Construct a grid in the pen using `x` and (optionally) `y` subdivisions"""
        xarg = x
        yarg = y or x
        if absolute:
            x = int(rect.w / xarg)
            y = int(rect.h / yarg)
        else:
            x = xarg
            y = yarg
        
        for _x in rect.subdivide(x, "minx"):
            if _x.x > 0 and _x.x > rect.x:
                self.line([_x.point("NW"), _x.point("SW")])
        for _y in rect.subdivide(y, "miny"):
            if _y.y > 0 and _y.y > rect.y:
                self.line([_y.point("SW"), _y.point("SE")])
        return self.f(None).s(0, 0.1).sw(3)
    
    def ez(self, r, start_y, end_y, s):
        self.moveTo(r.edge("W").t(start_y))
        self.gs(s, do_close=False, first_move="lineTo")
        self.lineTo(r.edge("E").t(end_y))
        self.endPath()
        return self
    
    def segments(self, all_curves=False):
        if not self.val_present():
            for idx, el in enumerate(self._els):
                self._els[idx] = el.segments()
            return self
        
        segs = []
        last = None
        for contour in self.copy().explode():
            for mv, pts in contour.v.value:
                if last:
                    if mv == "curveTo":
                        segs.append(type(self)().moveTo(last).curveTo(*pts))
                    if mv == "lineTo":
                        if all_curves:
                            ln = Line(last, pts[0])
                            segs.append(type(self)().moveTo(ln.start).curveTo(ln.t(0.25), ln.t(0.75), ln.end))
                        else:
                            segs.append(type(self)().moveTo(last).lineTo(*pts))
                
                if len(pts) > 0:
                    last = pts[-1]
                else:
                    last = None
        
        self._val = None
        self._els = segs
        return self

    def join(self):
        self._val = RecordingPen()

        self._val.moveTo(self._els[0].v.value[0][-1][-1])
        for el in self._els:
            self._val.value.extend(el.v.value[1:])
        
        self._els = []
        return self
    
    def substructure(self):
        indicators = type(self)()
        def append(p):
            substructure = p.data("substructure")
            if substructure:
                indicators.append(substructure)
        self.mapv(append)
        return indicators