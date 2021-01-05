import math, tempfile, pickle, inspect
from enum import Enum
from copy import deepcopy
from pathlib import Path
from time import sleep

from typing import Optional
from typing import Callable
#from collections.abc import Callable

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
from noise import pnoise1

import coldtype.pens.drawbot_utils as dbu

from coldtype.geometry import Rect, Edge, Point, txt_to_edge
from coldtype.beziers import raise_quadratic, CurveCutter, splitCubicAtT, calcCubicArcLength
from coldtype.color import Gradient, normalize_color, Color
from coldtype.pens.misc import ExplodingPen, SmoothPointsPen, BooleanOp, calculate_pathop

from coldtype.pens.outlinepen import OutlinePen
from coldtype.pens.translationpen import TranslationPen, polarCoord

from coldtype.pens.datpenlikeobject import DATPenLikeObject


def listit(t):
    return list(map(listit, t)) if isinstance(t, (list, tuple)) else t


class DATPen(RecordingPen, DATPenLikeObject):
    """
    Main vector representation in Coldtype
    
    DATPen is a subclass of fontTools ``RecordingPen``
    """
    def __init__(self, **kwargs):
        """**kwargs support is deprecated, should not accept any arguments"""
        super().__init__()
        self.single_pen_class = DATPen
        self._current_attr_tag = "default"
        self.clearAttrs()
        self.attr("default", **kwargs)
        self.frame = None
        self.typographic = False
        self._tag = "?"
        self._alpha = 1
        self._parent = None
        self.container = None
        self.glyphName = None
        self.data = {}
        self.visible = True
    
    def __str__(self):
        v = "" if self.visible else "ø-"
        return f"<{v}DP(typo:int({self.typographic})({self.glyphName}))——tag:{self._tag}/data:{self.data}>"
    
    def __len__(self):
        return len(self.value)
    
    def __bool__(self):
        return bool(len(self) > 0 or self.frame)
    
    def __add__(self, item):
        return DATPens([self, item])
    
    def __sub__(self, item):
        return DATPens([self])
    
    def to_code(self):
        t = None
        if self._tag and self._tag != "?":
            t = self._tag
        out = "(DATPen()"
        if t:
            out += f"\n    .tag(\"{t}\")"

        if self.data:
            out += f"\n    .add_data({repr(self.data)})"

        for mv, pts in self.value:
            out += "\n"
            if len(pts) > 0:
                spts = ", ".join([f"{(x, y)}" for (x, y) in pts])
                out += f"    .{mv}({spts})"
            else:
                out += f"    .{mv}()"
        for k, v in self.attrs.get("default").items():
            if v:
                if k == "fill":
                    out += f"\n    .f({v.to_code()})"
                elif k == "stroke":
                    out += f"\n    .s({v['color'].to_code()})"
                    out += f"\n    .sw({v['weight']})"
                else:
                    print("No code", k, v)
        out += ")"
        return out
    
    def vl(self, value):
        self.value = value
        return self
    
    def take(self, slice):
        self.value = self.value[slice]
        return self
    
    def ups(self):
        dps = DATPens()
        dps.append(self.copy())
        return dps
    
    as_set = ups
    
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
    
    def allStyledAttrs(self, style=None):
        if style and style in self.attrs:
            attrs = self.attrs[style]
        else:
            attrs = self.attrs["default"]
        return attrs

    def attr(self, tag=None, field=None, **kwargs):
        """Set a style attribute on the pen."""
        if not tag:
            if hasattr(self, "_current_attr_tag"): # TODO temporary for pickled pens
                tag = self._current_attr_tag
            else:
                tag = "default"

        if field: # getting, not setting
            return self.attrs.get(tag).get(field)
        
        attrs = dict(shadow=None)
        if tag and self.attrs.get(tag):
            attrs = self.attrs[tag]
        else:
            self.attrs[tag] = attrs
        for k, v in kwargs.items():
            if v:
                if k == "fill":
                    attrs[k] = normalize_color(v)
                elif k == "stroke":
                    existing = attrs.get("stroke", {})
                    if not isinstance(v, dict):
                        attrs[k] = dict(color=normalize_color(v), weight=existing.get("weight", 1))
                    else:
                        attrs[k] = dict(weight=v.get("weight", existing.get("weight", 1)), color=normalize_color(v.get("color", 0)))
                elif k == "strokeWidth":
                    if "stroke" in attrs:
                        attrs["stroke"]["weight"] = v
                        #if attrs["stroke"]["color"].a == 0:
                        #    attrs["stroke"]["color"] = normalize_color((1, 0, 0.5))
                    else:
                        attrs["stroke"] = dict(color=normalize_color((1, 0, 0.5)), weight=v)
                elif k == "shadow":
                    if "color" in v:
                        v["color"] = normalize_color(v["color"])
                    attrs[k] = v
                else:
                    attrs[k] = v
        return self
    
    def lattr(self, tag, fn: Callable[["DATPen"], Optional["DATPen"]]):
        was_tag = self._current_attr_tag
        self._current_attr_tag = tag
        fn(self)
        self._current_attr_tag = was_tag
        return self
    
    def calc_alpha(self):
        a = self._alpha
        p = self._parent
        while p:
            a = a * p._alpha
            p = p._parent
        return a
    
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
    
    def bounds(self):
        """Calculate the bounds of this shape; mostly for internal use."""
        try:
            cbp = BoundsPen(None)
            self.replay(cbp)
            mnx, mny, mxx, mxy = cbp.bounds
            return Rect((mnx, mny, mxx - mnx, mxy - mny))
        except:
            return Rect(0, 0, 0, 0)
    
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
    
    def nudge(self, lookup):
        def nudger(i, x, y):
            if lookup.get(i):
                nx, ny = lookup.get(i)
                return (x+nx, y+ny)
        return self.map_points(nudger)
    
    def repeat(self, times=1):
        copy = self.copy()
        copy_0_move, copy_0_data = copy.value[0]
        copy.value[0] = ("lineTo", copy_0_data)
        self.value = self.value[:-1] + copy.value
        if times > 1:
            self.repeat(times-1)
        return self
    
    def repeatx(self, times=1):
        w = self.getFrame(th=1).point("SE").x
        copy = self.copy().translate(w, 0)
        copy_0_move, copy_0_data = copy.value[0]
        copy.value[0] = ("lineTo", copy_0_data)
        self.value = self.value[:-1] + copy.value
        if times > 1:
            self.repeatx(times-1)
        return self
    
    def nonlinear_transform(self, fn):
        for idx, (move, pts) in enumerate(self.value):
            if len(pts) > 0:
                _pts = []
                for _pt in pts:
                    x, y = _pt
                    _pts.append(fn(x, y))
                self.value[idx] = (move, _pts)
        return self
    
    nlt = nonlinear_transform
    
    def bend(self, curve, tangent=True):
        cc = CurveCutter(curve)
        ccl = cc.length
        dpl = self.bounds().point("SE").x
        xf = ccl/dpl
        def bender(x, y):
            p, tan = cc.subsegmentPoint(end=x*xf)
            px, py = p
            if tangent:
                a = math.sin(math.radians(180+tan)) * y
                b = math.cos(math.radians(180+tan)) * y
                return (px+a, py+b)
                #return (px, y+py)
            else:
                return (px, y+py)
        return self.nonlinear_transform(bender)
    
    def bend2(self, curve, tangent=True, offset=(0, 1)):
        bw = self.bounds().w
        a = curve.value[0][-1][0]
        b, c, d = curve.value[-1][-1]
        def bender(x, y):
            c1, c2 = splitCubicAtT(a, b, c, d, offset[0] + (x/bw)*offset[1])
            _, _a, _b, _c = c1
            if tangent:
                tan = math.degrees(math.atan2(_c[1] - _b[1], _c[0] - _b[0]) + math.pi*.5)
                ax = math.sin(math.radians(90-tan)) * y
                by = math.cos(math.radians(90-tan)) * y
                return _c[0]+ax, (y+_c[1])+by
            return _c[0], y+_c[1]
        return self.nonlinear_transform(bender)
    
    def bend3(self, curve, tangent=False, offset=(0, 1)):
        a = curve.value[0][-1][0]
        b, c, d = curve.value[-1][-1]
        bh = self.bounds().h
        
        def bender(x, y):
            c1, c2 = splitCubicAtT(a, b, c, d, offset[0] + (y/bh)*offset[1])
            _, _a, _b, _c = c1
            if tangent:
                tan = math.degrees(math.atan2(_c[1] - _b[1], _c[0] - _b[0]) + math.pi*.5)
                ax = math.sin(math.radians(90-tan)) * y
                by = math.cos(math.radians(90-tan)) * y
                return x+_c[0]+ax, (y+_c[1])+by
            return x+_c[0], _c[1]
        return self.nonlinear_transform(bender)
    
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
        return self._pathop(otherPen=None, operation=BooleanOp.Simplify)

    def round(self, rounding):
        """Round the values of this pen to integer values."""
        rounded = []
        for t, pts in self.value:
            _rounded = []
            for p in pts:
                if p:
                    x, y = p
                    _rounded.append((round(x, rounding), round(y, rounding)))
                else:
                    _rounded.append(p)
            rounded.append((t, _rounded))
        self.value = rounded
        return self

    def round_to(self, rounding):
        """Round the values of this pen to nearest multiple of rounding."""
        def rt(v, mult):
            rndd = float(round(v / mult) * mult)
            if rndd.is_integer():
                return int(rndd)
            else:
                return rndd
        
        rounded = []
        for t, pts in self.value:
            _rounded = []
            for p in pts:
                if p:
                    x, y = p
                    _rounded.append((rt(x, rounding), rt(y, rounding)))
                else:
                    _rounded.append(p)
            rounded.append((t, _rounded))
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
    
    def to_glyph(self, name=None, width=None):
        """
        Create a glyph (like from `defcon`) using this pen’s value.
        *Warning*: be sure to call endPath or closePath on your pen or this call will silently do nothing
        """
        bounds = self.bounds()
        glyph = Glyph()
        glyph.name = name
        glyph.width = width or bounds.w
        sp = glyph.getPen()
        self.replay(sp)
        return glyph
    
    def collapse(self):
        """For compatibility with calls to a DATPens"""
        return DATPens([self])

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
    
    def roughen(self, amplitude=10, threshold=10, ignore_ends=False):
        """Randomizes points in skeleton"""
        randomized = []
        _x = 0
        _y = 0
        for idx, (t, pts) in enumerate(self.value):
            if idx == 0 and ignore_ends:
                randomized.append([t, pts])
                continue
            if idx == len(self.value) - 1 and ignore_ends:
                randomized.append([t, pts])
                continue
            if t == "lineTo" or t == "curveTo":
                jx = pnoise1(_x) * amplitude # should actually be 1-d on the tangent (maybe? TODO)
                jy = pnoise1(_y) * amplitude
                jx = randint(0, amplitude) - amplitude/2
                jy = randint(0, amplitude) - amplitude/2
                randomized.append([t, [(x+jx, y+jy) for x, y in pts]])
                _x += 0.2
                _y += 0.3
            else:
                randomized.append([t, pts])
        self.value = randomized
        return self

    def outline(self, offset=1, drawInner=True, drawOuter=True, cap="square"):
        """AKA expandStroke"""
        op = OutlinePen(None, offset=offset, optimizeCurve=True, cap=cap)
        self.replay(op)
        op.drawSettings(drawInner=drawInner, drawOuter=drawOuter)
        g = op.getGlyph()
        p = DATPen()
        g.draw(p)
        self.value = p.value
        return self
    
    def project(self, angle, width):
        offset = polarCoord((0, 0), math.radians(angle), width)
        self.translate(offset[0], offset[1])
        return self

    def castshadow(self, angle=-45, width=100, ro=1, fill=1):
        out = DATPen()
        tp = TranslationPen(out, frontAngle=angle, frontWidth=width)
        self.replay(tp)
        if fill:
            out.record(self.copy().project(angle, width))
        if ro:
            out.removeOverlap()
        self.value = out.value
        return self

    def grow(self, outline=10):
        out = self.copy().outline(outline)
        return self.record(out.reverse())
    
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
            if len(args) == 1:
                return self.rect(Rect(rect, args[0]))
            else:
                return self.rect(Rect(rect, args[0], args[1], args[2]))
        elif isinstance(rect[0], Rect):
            for r in rect:
                self.rect(r)
        else:
            self.rect(Rect(rect))
        return self

    def roundedRect(self, rect, hr, vr):
        """Rounded rectangle primitive"""
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
    
    def oval(self, rect):
        """Oval primitive"""
        self.roundedRect(rect, 0.5, 0.5)
        return self
    
    def semicircle(self, r, center, fext=0.5, rext=0.5):
        """
        Not really a semicircle
        `fext` controls extension from the standard on the "flat" edge
        `rext` controls extension from the standard on the "round" edge
        """
        sc = DATPen()
        n, e, s, w = r.cardinals()
        ne, se, sw, nw = r.intercardinals()
        cedge = txt_to_edge(center)

        if cedge in [Edge.MinX, Edge.MaxX]:
            fqe = r.w*fext
            rqe = r.h*rext
            sc.moveTo(sw).curveTo(sw.offset(fqe, 0), e.offset(0, -rqe), e).curveTo(e.offset(0, rqe), nw.offset(fqe, 0), nw).closePath()
            if cedge == Edge.MaxX:
                sc.rotate(180)
        elif cedge in [Edge.MinY, Edge.MaxY]:
            fqe = r.h*fext
            rqe = r.w*rext
            sc.moveTo(se).curveTo(se.offset(0, fqe), n.offset(rqe, 0), n).curveTo(n.offset(-rqe, 0), sw.offset(0, fqe), sw).closePath()
            if cedge == Edge.MaxY:
                sc.rotate(180)
        return self.record(sc)

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
    
    def standingwave(self, r, periods, direction=1):
        """Standing-wave primitive"""
        dp = DATPen()
        pw = r.w / periods

        blocks = r.subdivide(periods, "minx")
        for idx, block in enumerate(blocks):
            n, e, s, w = block.take(1, "centery").cardinals()
            if idx == 0:
                dp.moveTo(w)
            if direction == 1:
                if idx%2 == 0:
                    dp.lineTo(n)
                else:
                    dp.lineTo(s)
            else:
                if idx%2 == 0:
                    dp.lineTo(s)
                else:
                    dp.lineTo(n)
            if idx == len(blocks) - 1:
                dp.lineTo(e)
        dp.endPath().smooth()
        dp.value = dp.value[:-1]
        dp.endPath()
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
    
    def explode(self):
        """Read each contour into its own DATPen; returns a DATPens"""
        dp = RecordingPen()
        ep = ExplodingPen(dp)
        self.replay(ep)
        dps = DATPens()
        for p in ep.pens:
            dp = DATPen()
            dp.value = p
            dp.attrs = deepcopy(self.attrs)
            dps.append(dp)
        return dps
    
    def mod_contour(self, contour_index, mod_fn):
        exploded = self.explode()
        mod_fn(exploded[contour_index])
        self.value = exploded.implode().value
        return self
    
    def filter_contours(self, filter_fn):
        exploded = self.explode()
        keep = []
        for idx, c in enumerate(exploded):
            if filter_fn(idx, c):
                keep.append(c)
        self.value = DATPens(keep).implode().value
        return self
    
    def slicec(self, contour_slice):
        self.value = DATPens(self.explode()[contour_slice]).implode().value
        #print(exploded.pens[contour_slice])
        #self.value = DATPens(exploded[contour_slice]).implode().value
        return self
    
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
        print(">", start, end)
        self.value = pv
        return self
    
    def point_t(self, t=0.5):
        """Get point value for time `t`"""
        cc = CurveCutter(self)
        start = 0
        tv = t * cc.calcCurveLength()
        p, tangent = cc.subsegmentPoint(start=0, end=tv)
        return p, tangent
    
    def length(self, t=1):
        """Get the length of the curve for time `t`"""
        cc = CurveCutter(self)
        start = 0
        tv = t * cc.calcCurveLength()
        return tv
    
    def points(self):
        """Returns a list of points grouped by contour from the DATPen’s original contours; useful for drawing bezier skeletons; does not modify the DATPen"""
        contours = []
        for contour in self.skeletonPoints():
            _c = []
            for step, pts in contour:
                for pt in pts:
                    _c.append(Point(pt))
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
    
    def points_lookup(self):
        self.value = listit(self.value)
        lookup = []
        vi = 0
        while vi < len(self.value):
            pv = self.value[vi]
            t = pv[0]
            pvpts = self.value[vi][-1]
            for i, pt in enumerate(self.value[vi][-1]):
                lookup.append(dict(pt=Point(pt), vi=vi, i=i, t=t))
            vi += 1
        return lookup
    
    def mod_point(self, lookup, idx, x, y):
        pl = lookup[idx]
        pt = pl.get("pt")
        pt[0] += x
        pt[1] += y
        self.value[pl.get("vi")][-1][pl.get("i")] = pt
        return pt
    
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
    
    def preserve(self, tag, calls, dir=None):
        self.tag(tag)
        pdir = Path("preserved" or dir)
        pdir.mkdir(exist_ok=True, parents=True)
        tmp = (pdir / f"test_{tag}.pickle")
        self.data["_preserve"] = dict(calls=calls, pickle=str(tmp.absolute()))
        pickle.dump(self, open(str(tmp), "wb"))
        return self

    def bp(self):
        try:
            bp = dbu.db.BezierPath()
            self.replay(bp)
            return bp
        except:
            print("DrawBot not installed!")
            return None


class DATPens(DATPen):
    """
    A set/collection of DATPen’s
    
    Behaves like a list but can be queried somewhat like a DOM
    """
    def __init__(self, pens=[]):
        self.single_pen_class = DATPen
        self.pens = []
        self.typographic = True
        self.layered = False
        self._tag = "?"
        self._alpha = 1
        self._parent = None
        self.container = None
        self.frame = None
        self.data = {}
        self.visible = True

        if isinstance(pens, DATPen):
            self += pens
        else:
            for pen in pens:
                self += pen
    
    def __str__(self):
        v = "" if self.visible else "ø-"
        return f"<{v}DPS:{len(self.pens)}——tag:{self._tag}/data{self.data})>"
    
    def __len__(self):
        return len(self.pens)
    
    def to_code(self):
        out = "(DATPens()"

        t = None
        if self._tag and self._tag != "?":
            t = self._tag
        if t:
            out += f"\n    .tag(\"{t}\")"
        
        if self.data:
            out += f"\n    .add_data({repr(self.data)})"

        for pen in self.pens:
            for idx, line in enumerate(pen.to_code().split("\n")):
                if idx == 0:
                    out += f"\n    .append{line}"
                else:
                    out += f"\n    {line}"
            out += ""

        out += ")"
        return out
    
    def print_tree(self, depth=0):
        """Print a hierarchical representation of the pen set"""
        print(" |"*depth, self)
        for pen in self.pens:
            if hasattr(pen, "pens"):
                #print("  "*depth, pen)
                pen.print_tree(depth=depth+1)
                #print("  "*depth, "/"+str(pen))
            else:
                print(" |"*(depth+1), pen)
        #print("  "*depth + "/"+str(self))
        return self
    
    def copy(self, with_data=False):
        """Get a completely new copy of this whole set of pens,
        usually done so you can duplicate and further modify a
        DATPens without mutating the original"""
        dps = DATPens()
        for p in self.pens:
            dps.append(p.copy(with_data=with_data))
        return dps
    
    def __getitem__(self, index):
        return self.pens[index]
    
    def indexed_subset(self, indices):
        """Take only the pens at the given indices"""
        dps = DATPens()
        for idx, p in enumerate(self.pens):
            if idx in indices:
                dps.append(p.copy())
        return dps
    
    def __setitem__(self, index, pen):
        self.pens[index] = pen
    
    def __iadd__(self, item):
        return self.append(item)
    
    def __add__(self, item):
        return self.append(item)
    
    def __sub__(self, item):
        return self
    
    def insert(self, index, pen):
        if pen:
            self.pens.insert(index, pen)
        return self
    
    def append(self, pen, allow_blank=False):
        if pen or allow_blank:
            if isinstance(pen, DATPenLikeObject):
                self.pens.append(pen)
            else:
                try:
                    for p in pen:
                        if p:
                            self.pens.append(p)
                except TypeError:
                    #print("appending non-pen", type(pen))
                    self.pens.append(pen)
                    #print(">>> append rejected", pen)
        return self
    
    def extend(self, pens):
        if hasattr(pens, "pens"):
            self.append(pens)
        else:
            for p in pens:
                if p:
                    if hasattr(p, "value"):
                        self.append(p)
                    else:
                        self.extend(p)
        return self
        
    def reversePens(self):
        """Reverse the order of the pens; useful for overlapping glyphs from the left-to-right rather than right-to-left (as is common in OpenType applications)"""
        self.pens = list(reversed(self.pens))
        return self
    
    rp = reversePens
    
    def removeBlanks(self):
        """Remove blank pens from the set"""
        nonblank_pens = []
        for pen in self.pens:
            if not pen.removeBlanks():
                nonblank_pens.append(pen)
        self.pens = nonblank_pens
        return self
    
    def clearFrames(self):
        """Get rid of any non-bounds-derived pen frames;
        i.e. frames set by Harfbuzz"""
        for p in self.pens:
            p.clearFrame()
        return self
    
    def addFrame(self, frame, typographic=False, passthru=False):
        """Add a frame that isn't derived from the bounds"""
        if passthru:
            for p in self.pens:
                p.addFrame(frame, typographic=typographic)
        else:
            self.frame = frame
            self.typographic = typographic
        return self
    
    def getFrame(self, th=False, tv=False):
        """Get the frame of the DATPens;
        `th` means `(t)rue (h)orizontal`;
        `ty` means `(t)rue (v)ertical`;
        passing either ignores a non-bounds-derived frame
        in either dimension"""
        if self.frame and (th == False and tv == False):
            return self.frame
        else:
            try:
                union = self.pens[0].getFrame(th=th, tv=tv)
                for p in self.pens[1:]:
                    union = union.union(p.getFrame(th=th, tv=tv))
                return union
            except Exception as e:
                return Rect(0,0,0,0)
    
    def bounds(self):
        """Calculated bounds of a DATPens"""
        return self.getFrame(th=1, tv=1)
    
    def replay(self, pen):
        self.pen().replay(pen)
    
    def pen(self):
        """A flat representation of this set as a single pen"""
        dp = DATPen()
        fps = self.collapse()
        for p in fps.pens:
            dp.record(p)
        if len(fps.pens) > 0:
            for k, attrs in fps.pens[0].attrs.items():
                dp.attr(tag=k, **attrs)
        dp.addFrame(self.getFrame())
        return dp

    # Pen Primitives

    def moveTo(self, p0):
        self._in_progress_pen = DATPen()
        self._in_progress_pen.moveTo(p0)
        return self
    
    def lineTo(self, p1):
        self._in_progress_pen.lineTo(p1)
        return self
    
    def qCurveTo(self, *points):
        self._in_progress_pen.qCurveTo(*points)
        return self
    
    def curveTo(self, *points):
        self._in_progress_pen.curveTo(*points)
        return self
    
    def closePath(self):
        self._in_progress_pen.closePath()
        self.append(self._in_progress_pen)
        self._in_progress_pen = None
        return self
    
    def endPath(self):
        self._in_progress_pen.endPath()
        self.append(self._in_progress_pen)
        self._in_progress_pen = None
        return self
    
    def record(self, pen):
        """Alias for append"""
        return self.append(pen)
    
    def explode(self):
        """Noop on a set"""
        return self
    
    # Overrides
    
    def attr(self, key="default", field=None, **kwargs):
        if field: # getting, not setting, kind of weird to return the first value?
            if len(self.pens) > 0:
                return self.pens[0].attr(key=key, field=field)
            else:
                return None
        for p in self.pens:
            p.attr(key, **kwargs)
        return self
    
    def lattr(self, tag, fn: Callable[[DATPen], Optional[DATPen]]):
        for p in self.pens:
            p.lattr(tag, fn)
        return self
    
    def removeOverlap(self):
        for p in self.pens:
            p.removeOverlap()
        return self
    
    def transform(self, transform, transformFrame=True):
        for p in self.pens:
            p.transform(transform)
        if transformFrame and self.frame:
            self.frame = self.frame.transform(transform)
        return self

    #def nlt(self, fn, flatten=0):
    #    return self.pmap(lambda idx, p: p.nonlinear_transform(fn))
    
    def round(self, rounding):
        """Round all values for all pens in this set"""
        for p in self.pens:
            p.round(rounding)
        return self
    
    def round_to(self, rounding):
        """Round all values for all pens in this set to nearest multiple of rounding value (rather than places, as in `round`)"""
        for p in self.pens:
            p.round_to(rounding)
        return self
    
    def map(self, fn: Callable[[int, DATPen], Optional[DATPen]]):
        """Apply `fn` to all top-level pen(s) in this set;
        if `fn` returns a value, it will overwrite
        the pen it was given as an argument;
        fn lambda receives `idx, p` as arguments"""
        for idx, p in enumerate(self.pens):
            result = fn(idx, p)
            if result:
                self.pens[idx] = result
        return self
    
    def mmap(self, fn: Callable[[int, DATPen], None]):
        """Apply `fn` to all top-level pen(s) in this set but
        do not look at return value; first m in mmap
        stands for `mutate`;
        fn lambda receives `idx, p` as arguments"""
        for idx, p in enumerate(self.pens):
            fn(idx, p)
        return self
    
    def filter(self, fn: Callable[[int, DATPen], bool]):
        """Filter top-level pen(s)"""
        dps = DATPens()
        for idx, p in enumerate(self.pens):
            if fn(idx, p):
                dps.append(p)
        #self.pens = dps.pens
        #return self
        return dps
    
    def pmap(self, fn):
        """Apply `fn` to all individal pens, recursively"""
        for idx, p in enumerate(self.pens):
            if hasattr(p, "pens"):
                p.pmap(fn)
            else:
                fn(idx, p)
        return self
    
    def pfilter(self, fn):
        """Filter all pens, recursively"""
        to_keep = []
        for idx, p in enumerate(self.pens):
            if hasattr(p, "pens"):
                matches = p.pfilter(fn)
                if len(matches) > 0:
                    to_keep.extend(matches)
            if fn(idx, p):
                to_keep.append(p)
        return to_keep
    
    def index(self, idx, fn):
        fn(self[idx])
        return self
    
    def glyphs_named(self, glyph_name):
        """Pluck glyphs named `glyph_name`"""
        #return self.pfilter(lambda i, p: p.glyphName == glyph_name).pmap(lambda idx, p: mod_fn(p))
        for p in self:
            if callable(glyph_name) and glyph_name(p.glyphName):
                yield p
            elif p.glyphName == glyph_name:
                yield p
    
    def tagged(self, tag):
        """Yield all top-level pens tagged w/ `tag`"""
        for p in self:
            if p.getTag() == tag:
                yield p
    
    def ffg(self, glyph_name):
        """(f)ind the (f)irst (g)lyph named this name"""
        return list(self.glyphs_named(glyph_name))[0]
    
    def fft(self, tag):
        """(f)ind the (f)irst (t)agged with `tag`"""
        try:
            return list(self.tagged(tag))[0]
        except:
            return None
    
    def mfilter(self, fn):
        """Same as `filter` but (m)utates this DATPens
        to now have only the filtered pens"""
        self.pens = self.filter(fn)
        return self
    
    def collapseonce(self):
        pens = []
        for idx, p in enumerate(self.pens):
            pens.extend(p)
        self.pens = pens
        return self
    
    def collapse(self, levels=100, onself=False):
        """AKA `flatten` in some programming contexts, though
        `flatten` is a totally different function here that flattens
        outlines; this function flattens nested collections into
        one-dimensional collections"""
        pens = []
        for idx, p in enumerate(self.pens):
            if hasattr(p, "pens") and levels > 0:
                pens.extend(p.collapse(levels=levels-1).pens)
            else:
                pens.append(p)
        dps = DATPens(pens)
        if self.layered:
            dps.layered = True
        if onself:
            self.pens = dps.pens
            return self
        else:
            return dps
    
    flatten = collapse # deprecated but used in the wild
    
    def frameSet(self, th=False, tv=False):
        """All the frames of all the pens"""
        if self.frame:
            return super().frameSet(th=th, tv=tv)
        dps = DATPens()
        for p in self.pens:
            if p.frame:
                dps.append(p.frameSet(th=th, tv=tv))
        return dps
    
    def align(self, rect, x=Edge.CenterX, y=Edge.CenterY, th=True, tv=False, transformFrame=True):
        return super().align(rect, x, y, th, tv, transformFrame)
    
    def alignToRects(self, rects, x=Edge.CenterX, y=Edge.CenterY, th=1, tv=1):
        for idx, p in enumerate(self.pens):
            p.align(rects[idx], x, y, th=th, tv=tv)
    
    def xa(self, x="centerx"):
        for pen in self:
            pen.xAlignToFrame(x)
        return self
    
    def distribute(self, v=False):
        off = 0
        for p in self:
            frame = p.getFrame()
            if v:
                if frame.y < 0:
                    p.translate(0, -frame.y)
                p.translate(0, off)
                off += frame.h
            else:
                if frame.x < 0:
                    p.translate(-frame.x, 0)
                p.translate(off, 0)
                off += frame.w
        return self
    
    def track(self, t, v=False):
        for idx, p in enumerate(self.pens):
            frame = p.getFrame()
            if v:
                p.translate(0, t*idx)
            else:
                p.translate(t*idx, 0)
        return self
        
    def distribute_on_path(self, path, offset=0, cc=None, notfound=None):
        if cc:
            cutter = cc
        else:
            cutter = CurveCutter(path)
        limit = len(self.pens)
        for idx, p in enumerate(self.pens):
            f = p.getFrame()
            bs = f.y
            ow = offset + f.x + f.w / 2
            #if ow < 0:
            #    if notfound:
            #        notfound(p)
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
    
    # deprecated
    distributeOnPath = distribute_on_path
    
    def implode(self):
        # TODO preserve frame from some of this?
        dp = self[0]
        for p in self[1:]:
            dp.record(p)
        return dp
    
    def understroke(self, s=0, sw=5, outline=False, dofill=0):
        if sw == 0:
            return self
        if not outline:
            return self.interleave(lambda idx, p: p.f(s).s(s).sw(sw))
        else:
            def mod(idx, p):
                if dofill:
                    pf = p.copy()
                p.f(s).outline(sw*2)
                if dofill:
                    p.reverse().record(pf)
                return p
            return self.interleave(mod)
    
    def interleave(self, style_fn, direction=-1, recursive=True):
        """Provide a callback-lambda to interleave new DATPens between the existing ones; useful for stroke-ing glyphs, since the stroked glyphs can be placed behind the primary filled glyphs."""
        pens = []
        for idx, p in enumerate(self.pens):
            if recursive and hasattr(p, "pens"):
                _p = p.interleave(style_fn, direction=direction, recursive=True)
                pens.append(_p)
            else:
                try:
                    np = style_fn(idx, p.copy())
                except TypeError:
                    np = style_fn(p.copy())
                if isinstance(np, DATPen):
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
        print(">>>", gn1, gn2)
        for idx, dp in enumerate(self):
            if dp.glyphName == gn2:
                try:
                    next_dp = self[idx+1]
                    if next_dp.glyphName == gn1:
                        self.addOverlaps(idx, idx+1, which, outline)
                except IndexError:
                    pass
        return self

DATPenSet = DATPens