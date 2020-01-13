import math
from enum import Enum
from copy import deepcopy

from fontTools.pens.boundsPen import ControlBoundsPen, BoundsPen
from fontTools.pens.reverseContourPen import ReverseContourPen
from fontTools.pens.pointInsidePen import PointInsidePen
from fontTools.pens.recordingPen import RecordingPen
from fontTools.pens.transformPen import TransformPen
from fontTools.svgLib.path.parser import parse_path
from fontTools.misc.transform import Transform
from fontPens.flattenPen import FlattenPen
from fontPens.marginPen import MarginPen
from collections import OrderedDict
from random import random, randint
from numbers import Number
from defcon import Glyph

try:
    from noise import pnoise1
except:
    pass


from coldtype.geometry import Rect, Edge, Point, txt_to_edge
from coldtype.beziers import raise_quadratic, CurveCutter
from coldtype.color import Gradient, normalize_color, Color
from coldtype.pens.misc import ExplodingPen, SmoothPointsPen, BooleanOp, calculate_pathop

try:
    from coldtype.pens.outlinepen import OutlinePen
except:
    pass


class DATPenLikeObject():
    def align(self, rect, x=Edge.CenterX, y=Edge.CenterY, th=True, tv=False):
        x = txt_to_edge(x)
        y = txt_to_edge(y)
        b = self.getFrame(th=th, tv=tv)

        xoff = 0
        if x != None:
            if x == Edge.CenterX:
                xoff = -b.x + rect.x + rect.w/2 - b.w/2
            elif x == Edge.MinX:
                xoff = rect.x
            elif x == Edge.MaxX:
                xoff = -b.x + rect.x + rect.w - b.w
        
        yoff = 0
        if y != None:
            if y == Edge.CenterY:
                yoff = -b.y + rect.y + rect.h/2 - b.h/2
            elif y == Edge.MaxY:
                yoff = rect.y + rect.h - b.h
            elif y == Edge.MinY:
                yoff = rect.y
        
        diff = rect.w - b.w
        return self.translate(xoff, yoff)
    
    å = align
    
    def pen(self):
        """Return a single-pen representation of this pen(set)."""
        return self

    def cast(self, _class, *args):
        """Quickly cast to a (different) subclass."""
        return _class(self, *args)

    def copy(self):
        """Make a totally fresh copy; useful given the DATPen’s general reliance on mutable state."""
        dp = DATPen()
        self.replay(dp)
        for tag, attrs in self.attrs.items():
            dp.attr(tag, **attrs)
        dp.glyphName = self.glyphName
        return dp

    def tag(self, tag):
        """For conveniently marking a DATPen(Set) w/o having to put it into some other data structure."""
        self._tag = tag
        return self
    
    def getTag(self):
        """Retrieve the tag (could probably be a real property)"""
        return self._tag
    
    def contain(self, rect):
        """For conveniently marking an arbitrary `Rect` container."""
        self.container = rect
        return self

    def f(self, *value):
        """Set a (f)ill"""
        return self.attr(fill=value)
    
    fill = f
    
    def s(self, *value):
        """Set a (s)troke"""
        return self.attr(stroke=value)
    
    stroke = s
    
    def sw(self, value):
        """Set a (s)troke (w)idth"""
        return self.attr(strokeWidth=value)
    
    strokeWidth = sw
    
    def removeBlanks(self):
        """If this is blank, `return True` (for recursive calls from DATPenSet)."""
        return len(self.value) == 0
    
    def clearFrame(self):
        """Remove the DATPen frame."""
        self.frame = None
        return self
    
    def addFrame(self, frame, typographic=False):
        """Add a new frame to the DATPen, replacing any old frame."""
        self.frame = frame
        if typographic:
            self.typographic = True
        return self
    
    def frameSet(self, th=False, tv=False):
        """Return a new DATPen representation of the frame of this DATPen."""
        return DATPen(fill=("random", 0.25)).rect(self.getFrame(th=th, tv=tv))
    
    def filmjitter(self, doneness, base=0, speed=(10, 20), scale=(2, 3), octaves=16):
        """
        An easy way to make something move in a way reminiscent of misregistered film
        """
        nx = pnoise1(doneness*speed[0], base=base, octaves=octaves)
        ny = pnoise1(doneness*speed[1], base=base+10, octaves=octaves)
        return self.translate(nx * scale[0], ny * scale[1])


class DATPen(RecordingPen, DATPenLikeObject):
    def __init__(self, **kwargs):
        super().__init__()
        self.clearAttrs()
        self.attr("default", **kwargs)
        self.frame = None
        self.typographic = False
        self._tag = "Unknown"
        self.container = None
        self.glyphName = None
    
    def __str__(self):
        return f"<DP(typo:int({self.typographic})({self.glyphName}))>"
    
    def moveTo(self, p0):
        """The standard `RecordingPen.moveTo`, but returns self for chainability."""
        super().moveTo(p0)
        return self

    def lineTo(self, p1):
        """The standard `RecordingPen.lineTo`, but returns self for chainability."""
        super().lineTo(p1)
        return self

    def qCurveTo(self, *points):
        """The standard `RecordingPen.qCurveTo`, but returns self for chainability."""
        super().qCurveTo(*points)
        return self

    def curveTo(self, *points):
        """The standard `RecordingPen.curveTo`, but returns self for chainability."""
        super().curveTo(*points)
        return self

    def closePath(self):
        """The standard `RecordingPen.closePath`, but returns self for chainability."""
        super().closePath()
        return self

    def endPath(self):
        """The standard `RecordingPen.endPath`, but returns self for chainability."""
        super().endPath()
        return self
    
    def clearAttrs(self):
        """Remove all styling."""
        self.attrs = OrderedDict()
        self.attr("default", fill=(1, 0, 0.5))
        return self

    def attr(self, tag="default", field=None, **kwargs):
        """Set a style attribute on the pen."""
        if field: # getting, not setting
            return self.attrs.get(tag).get(field)
        
        attrs = {}
        if tag and self.attrs.get(tag):
            attrs = self.attrs[tag]
        else:
            self.attrs[tag] = attrs
        for k, v in kwargs.items():
            if k == "fill":
                attrs[k] = normalize_color(v)
            elif k == "stroke":
                if not isinstance(v, dict):
                    attrs[k] = dict(color=normalize_color(v))
                else:
                    attrs[k] = dict(weight=v.get("weight", 1), color=normalize_color(v.get("color", 0)))
            elif k == "strokeWidth":
                if "stroke" in attrs:
                    attrs["stroke"]["weight"] = v
                    if attrs["stroke"]["color"].alpha == 0:
                        attrs["stroke"]["color"] = normalize_color((1, 0, 0.5))
                else:
                    attrs["stroke"] = dict(color=normalize_color((1, 0, 0.5)), weight=v)
            elif k == "shadow":
                if "color" in v:
                    v["color"] = normalize_color(v["color"])
                attrs[k] = v
            else:
                attrs[k] = v
        return self
    
    def getFrame(self, th=False, tv=False):
        """For internal use; creates a frame based on calculated bounds."""
        if self.frame:
            if (th or tv) and len(self.value) > 0:
                f = self.frame
                b = self.bounds()
                if th and tv:
                    return b
                elif th:
                    return Rect(b.x, f.y, b.w, f.h)
                else:
                    return Rect(f.x, b.y, f.w, b.h)
            else:
                return self.frame
        else:
            return self.bounds()
    
    def reverse(self):
        """Reverse the winding direction of the pen."""
        dp = DATPen()
        rp = ReverseContourPen(dp)
        self.replay(rp)
        self.value = dp.value
        return self
    
    def map(self, fn):
        for idx, v in enumerate(self.value):
            move, pts = v
            self.value[idx] = (move, fn(idx, pts))
        return self
    
    def map_points(self, fn):
        idx = 0
        for cidx, c in enumerate(self.value):
            move, pts = c
            pts = list(pts)
            for pidx, p in enumerate(pts):
                x, y = p
                result = fn(idx, x, y)
                if result:
                    pts[pidx] = result
                idx += 1
            self.value[cidx] = (move, pts)
        return self
    
    def repeat(self, times=1):
        copy = self.copy()
        copy_0_move, copy_0_data = copy.value[0]
        copy.value[0] = ("lineTo", copy_0_data)
        self.value = self.value[:-1] + copy.value
        if times > 1:
            self.repeat(times-1)
        return self
    
    def transform(self, transform, transformFrame=True):
        """Perform an arbitrary transformation on the pen, using the fontTools `Transform` class."""
        op = RecordingPen()
        tp = TransformPen(op, transform)
        self.replay(tp)
        self.value = op.value
        if transformFrame and self.frame:
            self.frame = self.frame.transform(transform)
        return self
    
    def _pathop(self, otherPen=None, operation=BooleanOp.XOR):
        self.value = calculate_pathop(self, otherPen, operation)
        return self
    
    def difference(self, otherPen):
        """Calculate and return the difference of this shape and another."""
        return self._pathop(otherPen=otherPen, operation=BooleanOp.Difference)
    
    def union(self, otherPen):
        """Calculate and return the union of this shape and another."""
        return self._pathop(otherPen=otherPen, operation=BooleanOp.Union)
    
    def xor(self, otherPen):
        """Calculate and return the XOR of this shape and another."""
        return self._pathop(otherPen=otherPen, operation=BooleanOp.XOR)
    
    def reverseDifference(self, otherPen):
        """Calculate and return the reverseDifference of this shape and another."""
        return self._pathop(otherPen=otherPen, operation=BooleanOp.ReverseDifference)
    
    def intersection(self, otherPen):
        """Calculate and return the intersection of this shape and another."""
        return self._pathop(otherPen=otherPen, operation=BooleanOp.Intersection)
    
    def removeOverlap(self):
        """Remove overlaps within this shape and return itself."""
        return self._pathop(otherPen=DATPen(), operation=BooleanOp.Union)
    
    def translate(self, x, y):
        """Translate this shape by `x` and `y` (pixel values)."""
        return self.transform(Transform(1, 0, 0, 1, x, y))
    
    def scale(self, scaleX, scaleY=None, center=None):
        """Scale this shape by a percentage amount (1-scale)."""
        t = Transform()
        if center != False:
            point = self.bounds().point("C") # maybe should be getFrame()?
            t = t.translate(point.x, point.y)
        t = t.scale(scaleX, scaleY or scaleX)
        if center != False:
            t = t.translate(-point.x, -point.y)
        return self.transform(t)
    
    def scaleToRect(self, rect):
        """Scale this shape into a `Rect`."""
        bounds = self.bounds()
        h = rect.w / bounds.w
        v = rect.h / bounds.h
        scale = h if h < v else v
        return self.scale(scale)
    
    def skew(self, x=0, y=0, unalign=True):
        t = Transform()
        if unalign != False:
            point = self.bounds().point("SW") # maybe should be getFrame()?
            t = t.translate(point.x, point.y)
        t = t.skew(x, y)
        if unalign != False:
            t = t.translate(-point.x, -point.y)
        return self.transform(t)
    
    def rotate(self, degrees, point=None):
        """Rotate this shape by a degree (in 360-scale, counterclockwise)."""
        t = Transform()
        if not point:
            point = self.bounds().point("C") # maybe should be getFrame()?
        t = t.translate(point.x, point.y)
        t = t.rotate(math.radians(degrees))
        t = t.translate(-point.x, -point.y)
        return self.transform(t, transformFrame=False)

    def bounds(self):
        """Calculate the bounds of this shape; mostly for internal use."""
        try:
            cbp = BoundsPen(None)
            self.replay(cbp)
            mnx, mny, mxx, mxy = cbp.bounds
            return Rect((mnx, mny, mxx - mnx, mxy - mny))
        except:
            return Rect(0, 0, 0, 0)

    def round(self, rounding):
        """Round the values of this pen to integer values."""
        rounded = []
        for t, pts in self.value:
            rounded.append(
                (t,
                [(round(x, rounding), round(y, rounding)) for x, y in pts]))
        self.value = rounded
        return self

    def simplify(self):
        """DO NOT USE"""
        import numpy as np
        last = None
        times = 0
        nv = []
        for idx, (t, pts) in enumerate(self.value):
            if last == t and t == "qCurveTo":
                print("hello")
                continue
                p0 = np.array(self.value[idx-2][-1][-1])
                p1, p2, p3 = [np.array(p) for p in self.value[idx-1][-1]]
                q0 = np.array(self.value[idx-1][-1][-1])
                q1, q2, q3 = [np.array(p) for p in pts]
                r0 = p0
                kp = 2
                kq = 2
                r1 = p0 + kp * (p1 - p0)
                r2 = q3 + kq * (q2 - q3)
                r3 = q3
                nv.pop()
                nv.append([t, [r1.tolist(), r2.tolist(), r3.tolist()]])
                times += 1
            else:
                nv.append([t, pts])
            last = t
        #self.value = nv
        return self

    def record(self, pen):
        """Play a pen into this pen, meaning that pen will be added to this one’s value."""
        pen.replay(self)
        return self
    
    def glyph(self, glyph):
        """Play a glyph (like from `defcon`) into this pen."""
        glyph.draw(self)
        return self
    
    def to_glyph(self, name=None):
        """
        Create a glyph (like from `defcon`) using this pen’s value.
        *Warning: be sure to call endPath or closePath on your pen or this call will silently do nothing
        """
        bounds = self.bounds()
        glyph = Glyph()
        glyph.name = name
        glyph.width = bounds.w
        sp = glyph.getPen()
        self.replay(sp)
        print(glyph._contours)
        return glyph

    def flatten(self, length=10):
        """
        Runs a fontTools `FlattenPen` on this pen
        """
        if length == 0:
            return self
        dp = DATPen()
        fp = FlattenPen(dp, approximateSegmentLength=length, segmentLines=True)
        self.replay(fp)
        self.value = dp.value
        return self
    
    def addSmoothPoints(self, length=100):
        """WIP"""
        rp = RecordingPen()
        fp = SmoothPointsPen(rp)
        self.replay(fp)
        self.value = rp.value
        return self
    
    def smooth(self):
        """Runs a catmull spline on the datpen, useful in combination as flatten+roughen+smooth"""
        dp = DATPen()
        for pts in self.skeletonPoints():
            _pts = [p[-1][-1] for p in pts]
            dp.catmull(_pts, close=True)
        self.value = dp.value
        return self
    
    def pixellate(self, rect, increment=50, inset=0):
        """WIP"""
        x = -200
        y = -200
        dp = DATPen()
        while x < 1000:
            while y < 1000:
                #print(x, y)
                pen = PointInsidePen(None, (x, y))
                self.replay(pen)
                isInside = pen.getResult()
                if isInside:
                    dp.rect(Rect(x, y, increment, increment).inset(inset))
                y += increment
            x += increment
            y = -200
        self.value = dp.value
        return self
    
    def scanlines(self, rect, sample=40, width=20, threshold=10):
        """WIP"""
        dp = DATPen()
        #print(">>>", rect)
        for y in range(min(-300, rect.y), max(1000, rect.h), sample): # 500 should be calc'ed from box right?
            mp = MarginPen(None, y, isHorizontal=True)
            self.replay(mp)
            xs = mp.getAll()
            if len(xs) > 1:
                for i in range(0, len(xs), 2):
                    try:
                        x1 = xs[i]
                        x2 = xs[i+1]
                        if abs(x2 - x1) > threshold:
                            dp.line([(x1, y), (x2, y)])
                    except:
                        pass
        self.value = dp.value
        return self.outline(width)
    
    def roughen(self, amplitude=10, threshold=10):
        """Randomizes points in skeleton"""
        try:
            randomized = []
            _x = 0
            _y = 0
            for t, pts in self.value:
                if t == "lineTo" or t == "curveTo":
                    jx = pnoise1(_x) * amplitude # should actually be 1-d on the tangent!
                    jy = pnoise1(_y) * amplitude
                    jx = randint(0, amplitude) - amplitude/2
                    jy = randint(0, amplitude) - amplitude/2
                    randomized.append([t, [(x+jx, y+jy) for x, y in pts]])
                    _x += 0.2
                    _y += 0.3
                else:
                    randomized.append([t, pts])
            self.value = randomized
        except:
            print("noise not installed")
            pass
        return self

    def outline(self, offset=1, drawInner=True, drawOuter=True):
        """AKA expandStroke"""
        op = OutlinePen(None, offset=offset, optimizeCurve=True, cap="square")
        self.replay(op)
        op.drawSettings(drawInner=drawInner, drawOuter=drawOuter)
        g = op.getGlyph()
        p = DATPen()
        g.draw(p)
        self.value = p.value
        return self
    
    def dots(self, radius=4):
        """(Necessary?) Create circles at moveTo commands"""
        dp = DATPen()
        for t, pts in self.value:
            if t == "moveTo":
                x, y = pts[0]
                dp.oval(Rect((x-radius, y-radius, radius, radius)))
        self.value = dp.value
        return self
    
    def catmull(self, points, close=False):
        """Run a catmull spline through a series of points"""
        p0 = points[0]
        p1, p2, p3 = points[:3]
        pts = [p0]
        i = 1
        while i < len(points):
            pts.append([
                ((-p0[0] + 6 * p1[0] + p2[0]) / 6),
                ((-p0[1] + 6 * p1[1] + p2[1]) / 6),
                ((p1[0] + 6 * p2[0] - p3[0]) / 6),
                ((p1[1] + 6 * p2[1] - p3[1]) / 6),
                p2[0],
                p2[1]
            ])
            p0 = p1
            p1 = p2
            p2 = p3
            try:
                p3 = points[i + 2]
            except:
                p3 = p3
            i += 1
        self.moveTo(pts[0])
        for p in pts[1:]:
            self.curveTo((p[0], p[1]), (p[2], p[3]), (p[4], p[5]))
        if close:
            self.closePath()
        return self
    
    def pattern(self, rect, clip=False):
        """WIP — maybe not long for this earth"""
        dp_copy = DATPen()
        dp_copy.value = self.value

        for y in range(-1, 1):
            for x in range(-1, 1):
                dpp = DATPen()
                dp_copy.replay(dpp)
                dpp.translate(rect.w*x, rect.h*y)
                dpp.replay(self)
        
        self.translate(rect.w/2, rect.h/2)
        if clip:
            clip_box = DATPen().rect(rect)
            return self.intersection(clip_box)
        return self
    
    def rect(self, rect, *args):
        """Rectangle primitive — `moveTo/lineTo/lineTo/lineTo/closePath`"""
        if isinstance(rect, Rect):
            self.moveTo(rect.point("SW").xy())
            self.lineTo(rect.point("SE").xy())
            self.lineTo(rect.point("NE").xy())
            self.lineTo(rect.point("NW").xy())
            self.closePath()
        elif isinstance(rect, Number):
            return self.rect(Rect(rect, args[0], args[1], args[2]))
        elif isinstance(rect[0], Rect):
            for r in rect:
                self.rect(r)
        else:
            self.rect(Rect(rect))
        return self

    def roundedRect(self, rect, hr, vr):
        """Rounded rectangle primitive"""
        l, b, w, h = rect
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
    
    def oval(self, rect):
        """Oval primitive"""
        self.roundedRect(rect, 0.5, 0.5)
        return self
    
    def circle(self, r, ext):
        qr = r.w/4
        n, e, s, w = r.cardinals()
        return self.moveTo(n).curveTo(n.offset(-qr-ext, 0), w.offset(0, qr+ext), w).curveTo(w.offset(0, -qr-ext), s.offset(-qr-ext, 0), s).curveTo(s.offset(qr+ext, 0), e.offset(0, -qr-ext), e).curveTo(e.offset(0, qr+ext), n.offset(qr+ext, 0), n).closePath()
    
    def semicircle(self, r, center, ext):
        n, e, s, w = r.cardinals()
        ne, se, sw, nw = r.intercardinals()
        qe = r.h/2+ext
        # if center == "minx":
        #     pts = sw, e, nw
        # elif center == "maxx":
        #     pts = ne, w, se
        # elif center == "maxy":
        #     pts = nw, s, ne
        # elif center == "miny":
        #     pts = se, n, sw
        # p1, p2, p3 = pts
        if center == "minx":
            return self.moveTo(sw).curveTo(sw.offset(r.w/2+ext, 0), e.offset(0, -(r.h/2+ext)), e).curveTo(e.offset(0, r.h/2+ext), nw.offset(r.w/2+ext, 0), nw).closePath()
        elif center == "miny":
            return self.moveTo(sw).lineTo(se).curveTo(se.offset(0, qe), n.offset(qe, 0), n).curveTo(n.offset(-qe, 0), sw.offset(0, qe), sw).closePath()
        elif center == "maxy":
            return self.moveTo(ne).lineTo(nw).curveTo(nw.offset(0, -qe), s.offset(-qe, 0), s).curveTo(s.offset(qe, 0), ne.offset(0, -qe), ne).closePath()
        else:
            raise Exception("Not implemented")

    def line(self, points):
        """Syntactic sugar for `moveTo`+`lineTo`(...)+`endPath`; can have any number of points"""
        self.moveTo(points[0])
        for p in points[1:]:
            self.lineTo(p)
        self.endPath()
        return self
    
    def hull(self, points):
        """Same as `DATPen.line` but calls closePath instead of endPath`"""
        self.moveTo(points[0])
        for pt in points[1:]:
            self.lineTo(pt)
        self.closePath()
        return self
    
    def polygon(self, sides, rect):
        """Polygon primitive; WIP"""
        radius = rect.square().w / 2
        c = rect.center()
        one_segment = math.pi * 2 / sides
        points = [(math.sin(one_segment * i) * radius, math.cos(one_segment * i) * radius) for i in range(sides)]
        dp = DATPen()
        points.reverse()
        dp.moveTo(points[0])
        for p in points[1:]:
            dp.lineTo(p)
        dp.closePath()
        dp.align(rect)
        self.record(dp)
        return self
    
    def quadratic(self, a, b, c, lineTo=False):
        """WIP"""
        a, b, c = [p.xy() if isinstance(p, Point) else p for p in [a, b, c]]
        dp = DATPen()
        if lineTo:
            dp.lineTo(a)
        else:
            dp.moveTo(a)
        dp.curveTo(*raise_quadratic(a, b, c))
        self.record(dp)
        return self
    
    def sine(self, r, periods):
        """Sine-wave primitive"""
        dp = DATPen()
        pw = r.w / periods
        p1 = r.point("SW")
        end = r.point("SE")
        dp.moveTo(p1)
        done = False
        up = True
        while not done:
            h = r.h if up else -r.h
            c1 = p1.offset(pw/2, 0)
            c2 = p1.offset(pw/2, h)
            p2 = p1.offset(pw, h)
            dp.curveTo(c1, c2, p2)
            p1 = p2
            if p1.x >= end.x:
                done = True
            else:
                done = False
            up = not up
        self.record(dp)
        return self
    
    def svg(self, file, gid, rect=Rect(0, 0, 0, 100)):
        """WIP; attempt to read an svg file into the pen"""
        from bs4 import BeautifulSoup
        with open(file, "r") as f:
            soup = BeautifulSoup(f.read(), features="lxml")
            tp = TransformPen(self, (1, 0, 0, -1, 0, rect.h))
            for path in soup.find(id=gid).find_all("path"):
                parse_path(path.get("d"), tp)
        return self
    
    def explode(self, into_set=False):
        """Read each contour into its own DATPen (or DATPenSet if `into_set` is True); returns a DATPenSet"""
        dp = RecordingPen()
        ep = ExplodingPen(dp)
        self.replay(ep)
        dps = DATPenSet()
        for p in ep.pens:
            dp = DATPen()
            dp.value = p
            dp.attrs = deepcopy(self.attrs)
            if into_set:
                dps.append(DATPenSet([dp]))
            else:
                dps.append(dp)
        return dps
    
    def openAndClosed(self):
        """Explode and then classify group each contour into open/closed pens; (what is this good for?)"""
        dp_open = DATPen()
        dp_closed = DATPen()
        for pen in self.explode().pens:
            if pen.value[-1][0] == "closePath":
                dp_closed.record(pen)
            else:
                dp_open.record(pen)
        return dp_open, dp_closed
    
    def subsegment(self, start=0, end=1):
        """Return a subsegment of the pen based on `t` values `start` and `end`"""
        cc = CurveCutter(self)
        start = 0
        end = end * cc.calcCurveLength()
        pv = cc.subsegment(start, end)
        self.value = pv
        return self
    
    def point_t(self, t=0.5):
        """Get point value for time `t`"""
        cc = CurveCutter(self)
        start = 0
        tv = t * cc.calcCurveLength()
        p, tangent = cc.subsegmentPoint(start=0, end=tv)
        return p, tangent
    
    def points(self):
        """Returns a list of points grouped by contour from the DATPen’s original contours; useful for drawing bezier skeletons; does not modify the DATPen"""
        contours = []
        for contour in self.skeletonPoints():
            _c = []
            for step, pts in contour:
                for pt in pts:
                    _c.append(pt)
            contours.append(_c)
        return contours
    
    def flatpoints(self):
        """Returns a flat list of points from the DATPen’s original contours; does not modify the DATPen"""
        points = []
        for contour in self.skeletonPoints():
            for step, pts in contour:
                for pt in pts:
                    if len(points) == 0 or points[-1] != pt:
                        points.append(pt)
        return points
    
    def lines(self):
        """Returns lines connecting point-representation of `flatpoints`"""
        ls = []
        pts = self.flatpoints()
        for idx, pt in enumerate(pts):
            if idx > 0:
                ls.append([pts[idx-1], pts[idx]])
        if len(ls) > 1:
            ls.append([pts[-1], pts[0]])
        return ls

    def skeletonPoints(self):
        """WIP"""
        all_points = []
        points = []
        for idx, (t, pts) in enumerate(self.value):
            if t == "moveTo":
                points.append(("moveTo", pts))
            elif t == "curveTo":
                p0 = self.value[idx-1][-1][-1]
                points.append(("curveTo", [p0, *pts]))
            elif t == "lineTo":
                p0 = self.value[idx-1][-1][-1]
                points.append(("lineTo", [p0, *pts]))
            elif t == "closePath":
                all_points.append(points)
                points = []
                #points.append(("closePath", [None]))
        if len(points) > 0:
            all_points.append(points)
        return all_points
    
    def skeleton(self, scale=1, returnSet=False):
        """Vector-editing visualization"""
        dp = DATPen()
        moveTo = DATPen(fill=("random", 0.5))
        lineTo = DATPen(fill=("random", 0.5))
        curveTo_on = DATPen(fill=("random", 0.5))
        curveTo_off = DATPen(fill=("random", 0.25))
        curveTo_bars = DATPen(fill=None, stroke=dict(color=("random", 0.5), weight=1*scale))
        for idx, (t, pts) in enumerate(self.value):
            if t == "moveTo":
                r = 12*scale
                x, y = pts[0]
                moveTo.rect(Rect((x-r/2, y-r/2, r, r)))
            elif t == "curveTo":
                r = 6*scale
                x, y = pts[-1]
                curveTo_on.oval(Rect((x-r/2, y-r/2, r, r)))
                r = 4*scale
                x, y = pts[1]
                curveTo_off.oval(Rect((x-r/2, y-r/2, r, r)))
                x, y = pts[0]
                curveTo_off.oval(Rect((x-r/2, y-r/2, r, r)))
                p0 = self.value[idx-1][-1][-1]
                curveTo_bars.line((p0, pts[0]))
                curveTo_bars.line((pts[1], pts[2]))
            elif t == "lineTo":
                r = 6*scale
                x, y = pts[0]
                lineTo.rect(Rect((x-r/2, y-r/2, r, r)))
        
        all_pens = [moveTo, lineTo, curveTo_on, curveTo_off, curveTo_bars]
        if returnSet:
            return all_pens
        else:
            for _dp in all_pens:
                dp.record(_dp)
            self.value = dp.value
            return self
    
    def gridlines(self, rect, x=20, y=None):
        """Construct a grid in the pen using `x` and (optionally) `y` subdivisions"""
        for _x in rect.subdivide(x, "minx"):
            if _x.x > 0:
                self.line([_x.point("NW"), _x.point("SW")])
        for _y in rect.subdivide(y or x, "miny"):
            if _y.y > 0:
                self.line([_y.point("SW"), _y.point("SE")])
        return self.f(None).s(0, 0.1).sw(3)


class DATPenSet(DATPenLikeObject):
    """
    A set of DATPen’s; behaves like a list
    """
    def __init__(self, *pens):
        self.pens = []
        self.extend(pens)
        self.typographic = True
        self.layered = False
        self._tag = "Unknown"
        self.container = None
    
    def __str__(self):
        return f"<DPS:pens:{len(self.pens)}>"
    
    def __len__(self):
        return len(self.pens)
    
    def copy(self):
        dps = DATPenSet()
        for p in self.pens:
            dps.append(p.copy())
        return dps
    
    def __getitem__(self, index):
        return self.pens[index]
    
    def indexed_subset(self, indices):
        dps = DATPenSet()
        for idx, p in enumerate(self.pens):
            if idx in indices:
                dps.append(p.copy())
        return dps
    
    def __setitem__(self, index, pen):
        self.pens[index] = pen
    
    def insert(self, index, pen):
        if pen:
            self.pens.insert(index, pen)
        return self
    
    def append(self, pen):
        if pen:
            self.pens.append(pen)
        return self
    
    def extend(self, pens):
        if isinstance(pens, DATPenSet):
            self.append(pens)
        else:
            for p in pens:
                if p:
                    if hasattr(p, "value"):
                        self.append(p)
                    else:
                        self.extend(p)
        
    def reversePens(self):
        """Reverse the order of the pens; useful for overlapping glyphs from the left-to-right rather than right-to-left (as is common in OpenType applications)"""
        self.pens = list(reversed(self.pens))
        return self
    
    def removeBlanks(self):
        """Remove blank pens from the set"""
        nonblank_pens = []
        for pen in self.pens:
            if not pen.removeBlanks():
                nonblank_pens.append(pen)
        self.pens = nonblank_pens
        return self
    
    def clearFrames(self):
        for p in self.pens:
            p.clearFrame()
        return self
    
    def addFrame(self, frame, typographic=False):
        for p in self.pens:
            p.addFrame(frame, typographic=typographic)
        return self
    
    def getFrame(self, th=False, tv=False):
        try:
            union = self.pens[0].getFrame(th=th, tv=tv)
            for p in self.pens[1:]:
                union = union.union(p.getFrame(th=th, tv=tv))
            return union
        except Exception as e:
            return Rect(0,0,0,0)
    
    def replay(self, pen):
        self.pen().replay(pen)
    
    def pen(self):
        dp = DATPen()
        fps = self.flatten()
        for p in fps.pens:
            dp.record(p)
        if len(fps.pens) > 0:
            for k, attrs in fps.pens[0].attrs.items():
                dp.attr(tag=k, **attrs)
        dp.addFrame(self.getFrame())
        return dp
    
    def attr(self, key="default", field=None, **kwargs):
        if field: # getting, not setting
            return self.pens[0].attr(key=key, field=field)
        for p in self.pens:
            p.attr(key, **kwargs)
        return self
    
    def removeOverlap(self):
        for p in self.pens:
            p.removeOverlap()
        return self
    
    def transform(self, t):
        for p in self.pens:
            p.transform(t)
        return self
    
    def translate(self, x, y):
        for p in self.pens:
            p.translate(x, y)
        return self
    
    def rotate(self, degrees):
        for p in self.pens:
            p.rotate(degrees)
        return self
    
    def scale(self, scaleX, scaleY=None, center=None):
        for p in self.pens:
            p.scale(scaleX, scaleY=scaleY, center=center)
        return self
    
    def skew(self, x=0, y=0):
        for p in self.pens:
            p.skew(x, y)
        return self
    
    def round(self, rounding):
        for p in self.pens:
            p.round(rounding)
        return self
    
    def map(self, fn):
        for idx, p in enumerate(self.pens):
            result = fn(idx, p)
            if result:
                self.pens[idx] = result
        return self
    
    def mmap(self, fn):
        for idx, p in enumerate(self.pens):
            fn(idx, p)
        return self
    
    def filter(self, fn):
        dps = DATPenSet()
        for idx, p in enumerate(self.pens):
            if fn(idx, p):
                dps.append(p)
        #self.pens = dps.pens
        #return self
        return dps
    
    def mfilter(self, fn):
        self.pens = self.filter(fn)
        return self
    
    def flatten(self, levels=100):
        pens = []
        for p in self.pens:
            if isinstance(p, DATPenSet) and levels > 0:
                pens.extend(p.flatten(levels=levels-1).pens)
            else:
                pens.append(p)
        dps = DATPenSet(pens)
        if self.layered:
            dps.layered = True
        return dps
    
    def frameSet(self, th=False, tv=False):
        dps = DATPenSet()
        for p in self.pens:
            if p.frame:
                dps.append(p.frameSet(th=th, tv=tv))
        return dps
    
    def alignToRects(self, rects, x=Edge.CenterX, y=Edge.CenterY):
        for idx, p in enumerate(self.pens):
            p.align(rects[idx], x, y)
    
    def distribute(self):
        x_off = 0
        for p in self.pens:
            frame = p.getFrame()
            #x_off += s.margin[0]
            p.translate(x_off, 0)
            x_off += frame.w
            #x_off += s.margin[1]
        return self
        
    def distributeOnPath(self, path, offset=0, cc=None):
        if cc:
            cutter = cc
        else:
            cutter = CurveCutter(path)
        limit = len(self.pens)
        for idx, p in enumerate(self.pens):
            f = p.getFrame()
            bs = f.y
            ow = offset + f.x + f.w / 2
            if ow > cutter.length:
                limit = min(idx, limit)
            else:
                _p, tangent = cutter.subsegmentPoint(end=ow)
                x_shift = bs * math.cos(math.radians(tangent))
                y_shift = bs * math.sin(math.radians(tangent))
                t = Transform()
                t = t.translate(_p[0] + x_shift - f.x, _p[1] + y_shift - f.y)
                t = t.translate(f.x, f.y)
                t = t.rotate(math.radians(tangent-90))
                t = t.translate(-f.x, -f.y)
                t = t.translate(-f.w*0.5)
                p.transform(t)

        if limit < len(self.pens):
            self.pens = self.pens[0:limit]
        return self
    
    def interleave(self, style_fn, direction=-1, recursive=True):
        """Provide a callback-lambda to interleave new DATPens between the existing ones; useful for stroke-ing glyphs, since the stroked glyphs can be placed behind the primary filled glyphs."""
        pens = []
        for idx, p in enumerate(self.pens):
            if recursive and isinstance(p, DATPenSet):
                _p = p.interleave(style_fn, direction=direction, recursive=True)
                pens.append(_p)
            else:
                try:
                    np = style_fn(idx, p.copy())
                except TypeError:
                    np = style_fn(p.copy())
                if isinstance(np, DATPen) or isinstance(np, DATPenSet):
                    np = [np]
                if direction < 0:
                    pens.extend(np)
                pens.append(p)
                if direction > 0:
                    pens.extend(np)

        self.pens = pens
        return self
    
    def addOverlaps(self, idx1, idx2, which, outline=3, scale=1, xray=0):
        c1 = self[idx1]
        c2 = self[idx2]
        c2_upscale = c2.copy().scale(scale)
        if outline != None:
            c2_upscale.record(c2_upscale.copy().outline(outline+1).reverse()).removeOverlap()
        
        overlaps = c1.copy().intersection(c2_upscale).explode().indexed_subset(which)
        if outline and outline > 0:
            all_outlined = c1.copy().f(0).outline(outline).intersection(c2).explode()

        for ol in overlaps:
            olb = ol.bounds().inset(0)
            if outline and outline > 0:
                for idx, ool in enumerate(all_outlined):
                    oolb = ool.bounds().inset(0)
                    if oolb.intersects(olb):
                        self.append(ool.tag(f"overlap_outline_{idx1}"))#.f(1, 0, 0.5))
                        if xray and False:
                            self.append(DATPen().f(0, 0.5, 1, 0.2).rect(olb))
                            self.append(DATPen().f(0.5, 0, 1, 0.2).rect(oolb))
                    else:
                        if xray and False:
                            self.append(DATPen().f(None).s(0, 0.5, 1, 0.2).rect(olb))
                            self.append(DATPen().f(None).s(0.5, 0, 1, 0.2).rect(oolb))
            self.append(ol.tag(f"overlap_{idx1}"))#.f(1, 0, 0.5, 0.5))
            #self.append(overlaps.copy().f(0, 1, 0, 0.1))

    def overlapPair(self, gn1, gn2, which, outline=3):
        for idx, dp in enumerate(self):
            if dp.glyphName == gn2:
                try:
                    next_dp = self[idx+1]
                    if next_dp.glyphName == gn1:
                        self.addOverlaps(idx, idx+1, which, outline)
                except IndexError:
                    pass
        return self
    
    def overlapPairs(self, pairs, outline=3):
        for pair, which in pairs.items():
            self.overlapPair(pair[0], pair[1], which, outline=outline)
        return self