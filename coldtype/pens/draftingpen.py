import enum
import math, re

from time import sleep
from typing import Callable, Optional, Tuple, Type
from collections import OrderedDict
from copy import deepcopy

from fontTools.misc.transform import Transform
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.recordingPen import RecordingPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.basePen import decomposeQuadraticSegment
from fontTools.pens.reverseContourPen import ReverseContourPen

from fontPens.flattenPen import FlattenPen
from coldtype.geometry import Atom, Point, Line, Edge, Rect, Curve, align
from coldtype.color import normalize_color
from coldtype.sh import SH_UNARY_SUFFIX_PROPS, sh, SHContext

from coldtype.pens.misc import BooleanOp, calculate_pathop, ExplodingPen, SmoothPointsPen

from coldtype.pens.outlinepen import OutlinePen
from coldtype.pens.translationpen import TranslationPen, polarCoord

from coldtype.beziers import CurveCutter, splitCubicAtT
from coldtype.interpolation import norm
from coldtype.grid import Grid


class DraftingPen(RecordingPen, SHContext):
    """Fluent subclass of RecordingPen"""

    def __init__(self, *args):
        SHContext.__init__(self)
        RecordingPen.__init__(self)

        from coldtype.pens.draftingpens import DraftingPens

        self.single_pen_class = DraftingPen
        self.multi_pen_class = DraftingPens

        self._tag = None
        self._frame = None
        self._visible = True
        self._parent = None
        self._last = None
        self._alpha = 1

        self._typographic = False
        self.glyphName = None

        self._current_attr_tag = "default"
        self.clearAttrs()
        self.data = {}

        self.defs = None
        self.macros = {}

        for _, arg in enumerate(args):
            if isinstance(arg, str):
                self.tag(arg)
            elif isinstance(arg, DraftingPen):
                self.replace_with(arg)
            elif isinstance(arg, Rect):
                self.rect(arg)
            elif isinstance(arg, Line):
                self.line(arg)
            elif isinstance(arg, Point):
                self.oval(Rect.FromCenter(arg, 50, 50))
    
    def __repr__(self):
        s = f"{type(self).__name__}<"
        if self._tag:
            s += self._tag + ":"
        if len(self.value) == 0:
            s += "(((empty)))"
        else:
            s += f"{len(self.value)}mvs:"
            if self.value[-1][0] == "closePath":
                s += "closed"
            elif self.value[-1][0] == "endPath":
                s += "end"
            else:
                s += "open"
        s += "/>"
        return s
    
    def tag(self, value=None):
        if value:
            if isinstance(value, str):
                self._tag = value
            return self
        else:
            return self._tag
        
    def frame(self, value=None):
        if value:
            if isinstance(value, Rect):
                self._frame = value
            return self
        else:
            return self._frame
    
    def visible(self, value=None):
        if value is not None:
            self._visible = value
            return self
        else:
            return self._visible
        
    def bounds(self):
        """Calculate the bounds of this shape; mostly for internal use."""
        try:
            cbp = BoundsPen(None)
            self.replay(cbp)
            mnx, mny, mxx, mxy = cbp.bounds
            return Rect((mnx, mny, mxx - mnx, mxy - mny))
        except:
            return Rect(0, 0, 0, 0)
    
    def ambit(self, th=False, tv=False):
        """Get the calculated rect boundary of the DraftingPen;
        `th` means `(t)rue (h)orizontal`;
        `ty` means `(t)rue (v)ertical`;
        passing either ignores a non-bounds-derived frame
        in either dimension"""
        if self._frame:
            if (th or tv) and len(self.value) > 0:
                f = self._frame
                b = self.bounds()
                if th and tv:
                    return b
                elif th:
                    return Rect(b.x, f.y, b.w, f.h)
                else:
                    return Rect(f.x, b.y, f.w, b.h)
            else:
                return self._frame
        else:
            return self.bounds()
    
    def addFrame(self, frame, typographic=False, passthru=False):
        """Add a new frame to the DATPen, replacing any old frame. Passthru ignored, there for compatibility"""
        self._frame = frame
        if typographic:
            self.typographic = True
        return self
    
    def unended(self):
        if len(self.value) == 0:
            return True
        elif self.value[-1][0] not in ["endPath", "closePath"]:
            return True
        return False
    
    def fully_close_path(self):
        if self.value[-1][0] == "closePath":        
            start = self.value[0][-1][-1]
            end = self.value[-2][-1][-1]

            if start != end:
                self.value = self.value[:-1]
                self.lineTo(start)
                self.closePath()
        return self
    
    def reverse(self):
        """Reverse the winding direction of the pen."""
        if self.unended():
            self.closePath()
        dp = type(self)()
        rp = ReverseContourPen(dp)
        self.replay(rp)
        self.value = dp.value
        return self
    
    def __invert__(self):
        return self.reverse()
    
    def sh(self, s, subs={}):
        try:
            start = self.value[0][1][-1]
        except:
            start = None
        #print("SH", s, self.defs)
        res = sh(s, self, subs={"¬":self._last, "§":start, **subs})
        if res[0] == "∫":
            res = [self.single_pen_class().gs(res[1:])]
        return res
    
    def gss(self, s):
        dps = self.multi_pen_class()
        sh(s, ctx=self, dps=dps)
        for p in dps._pens:
            self.record(p)
        return self
    
    def gs(self, s, fn=None, tag=None, writer=None, ctx=None, dps=None, macros={}):
        ctx = ctx or self
        macros = {**self.macros, **macros}

        def expand_multisuffix(m):
            out = []
            arrows = list(m.group(2))
            for a in arrows:
                out.append(m.group(1)+a)
            return " ".join(out)

        def sp(_s):
            return [x.strip() for x in re.split(r"\s|\n", _s)]

        if isinstance(s, str):
            s = s
            s = re.sub(r"([\$\&]{1}[a-z]+)([↖↑↗→↘↓↙←•⍺⍵µ]{2,})", expand_multisuffix, s)
            #e = sh(s, ctx, dps)
            moves = sp(s)
        else:
            e = s
            moves = e
        
        def one_move(_e, move="lineTo"):
            if _e is None:
                return
            elif isinstance(_e, Point):
                getattr(self, move)(_e)
            elif isinstance(_e, Rect):
                self.rect(_e)
            elif isinstance(_e, Curve):
                _, b, c, d = _e
                self.curveTo(b, c, d)
            elif isinstance(_e, str):
                getattr(self, _e)()
            elif _e[0][0] == "∑":
                    macro = "".join(_e[0][1:])
                    if macro in macros:
                        macro_fn = macros[macro]
                        macro_fn(self, *_e[1:])
                    else:
                        raise Exception("unrecognized macro '" + macro + "'")
            elif len(_e) >= 3:
                if len(_e) >= 5:
                    self.interpCurveTo(*_e)
                else:
                    self.boxCurveTo(*_e)

        locals = {}
        mvs = [moves[0]]
        if isinstance(mvs[0], str):
            res = sh(mvs[0], ctx, dps)
        else:
            res = [mvs[0]]
        one_move(res[0], move="moveTo")

        try:
            start = self.value[0][1][-1]
        except:
            start = None

        for _m in moves[1:]:
            last = self._last
            ctx._last = last
            if isinstance(_m, str):
                res = sh(_m, ctx, dps, subs={"¬":last,"§":start})
            else:
                res = [_m]
            if res:
                one_move(res[0], move="lineTo")
        
        if self.unended():
            self.closePath()

        if tag:
            self.tag(tag)
        if fn:
            fn(self)
        return self

    def moveTo(self, p0):
        super().moveTo(p0)
        self._last = p0
        return self

    def lineTo(self, p1):
        if len(self.value) == 0:
            super().moveTo(p1)
        else:
            super().lineTo(p1)
        self._last = p1
        return self

    def qCurveTo(self, *points):
        super().qCurveTo(*points)
        self._last = points[-1]
        return self

    def curveTo(self, *points):
        super().curveTo(*points)
        self._last = points[-1]
        return self

    def closePath(self):
        super().closePath()
        return self

    def endPath(self):
        super().endPath()
        return self

    def addComponent(self, glyphName, transformation):
        if hasattr(self, "_glyphSet") and self._glyphSet:
            if glyphName in self._glyphSet:
                dp = DraftingPen().glyph(self._glyphSet[glyphName], self._glyphSet).transform(transformation)
                self.record(dp)
            #super().addComponent(glyphName, transformation)
        else:
            print("no glyphset, cannot add component")
        return self

    def replay(self, pen):
        super().replay(pen)
        return self
    
    def record(self, pen):
        """Play a pen into this pen, meaning that pen will be added to this one’s value."""
        if hasattr(pen, "_pens"):
            for p in pen:
                self.record(p)
        elif pen:
            pen.replay(self)
        return self
    
    def glyph(self, glyph, glyphSet=None):
        """Play a glyph (like from `defcon`) into this pen."""
        if glyphSet:
            self._glyphSet = glyphSet
        glyph.draw(self)
        return self
    
    def to_glyph(self, name=None, width=None, allow_blank=False):
        """
        Create a glyph (like from `defcon`) using this pen’s value.
        *Warning*: if path is unended, closedPath will be called
        """
        from defcon import Glyph
        if not allow_blank:
            if self.unended():
                self.closePath()
        bounds = self.bounds()
        glyph = Glyph()
        glyph.name = name
        glyph.width = width or bounds.w
        try:
            sp = glyph.getPen()
            self.replay(sp)
        except AssertionError:
            if not allow_blank:
                print(">>>blank glyph:", glyph.name)
        return glyph
    
    def rect(self, rect):
        """Rectangle primitive — `moveTo/lineTo/lineTo/lineTo/closePath`"""
        self.moveTo(rect.point("SW").xy())
        self.lineTo(rect.point("SE").xy())
        self.lineTo(rect.point("NE").xy())
        self.lineTo(rect.point("NW").xy())
        self.closePath()
        return self
    
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
    
    def oval(self, rect):
        """Oval primitive"""
        self.roundedRect(rect, 0.5, 0.5)
        return self

    def line(self, points, moveTo=True, endPath=True):
        """Syntactic sugar for `moveTo`+`lineTo`(...)+`endPath`; can have any number of points"""
        if isinstance(points, Line):
            points = list(points)
        if len(points) == 0:
            return self
        if len(self.value) == 0 or moveTo:
            self.moveTo(points[0])
        else:
            self.lineTo(points[0])
        for p in points[1:]:
            self.lineTo(p)
        if endPath:
            self.endPath()
        return self
    
    def hull(self, points):
        """Same as `DraftingPen.line` but calls closePath instead of endPath`"""
        self.moveTo(points[0])
        for pt in points[1:]:
            self.lineTo(pt)
        self.closePath()
        return self

    def interpCurveTo(self, p1, f1, p2, f2, to, inset=0):
        a = Point(self.value[-1][-1][-1])
        d = Point(to)
        pl = Line(p1, p2).inset(inset)
        b = Line(a, pl.start).t(f1/100)
        c = Line(d, pl.end).t(f2/100)
        return self.curveTo(b, c, d)
    
    def boxCurveTo(self, point, factor, pt, po=(0, 0), mods={}, flatten=False):
        if flatten:
            self.lineTo(pt)
            return self
        
        a = Point(self.value[-1][-1][-1])
        d = Point(pt)
        box = Rect.FromMnMnMxMx([min(a.x, d.x), min(a.y, d.y), max(a.x, d.x), max(a.y, d.y)])
        try:
            f1, f2 = factor
        except TypeError:
            if isinstance(factor, Atom):
                f1, f2 = (factor[0], factor[0])
            else:
                f1, f2 = (factor, factor)

        if isinstance(point, str):
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
    
    def vl(self, value):
        self.value = value
        return self
    
    def replace_with(self, other):
        return self.vl(other.value)
    
    def pvl(self):
        for idx, (_, pts) in enumerate(self.value):
            if len(pts) > 0:
                self.value[idx] = list(self.value[idx])
                self.value[idx][-1] = [Point(p) for p in self.value[idx][-1]]
        return self
    
    def add_data(self, key, value=None):
        if value is None:
            self.data = key
        else:
            self.data[key] = value
        return self
    
    def copy(self, with_data=False):
        dp = self.single_pen_class()
        self.replay(dp)
        for tag, attrs in self.attrs.items():
            dp.attr(tag, **attrs)
        
        dp.glyphName = self.glyphName
        dp.defs = self.defs

        if with_data:
            dp.data = self.data
            if self._frame:
                dp._frame = self._frame
            if hasattr(self, "macros"):
                dp.macros = self.macros
            if self.typographic:
                dp.typographic = True
        return dp
    
    def cast(self, _class, *args):
        """Quickly cast to a (different) subclass."""
        #if hasattr(self, "_pens"):
        #    return _class(self._pens)
        res = _class(self, *args)
        res.attrs = deepcopy(self.attrs)
        return res
    
    def pen(self):
        """Return a single-pen representation of this pen(set)."""
        return self
    
    def to_pen(self):
        return self.pen()
    
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

    def transform(self, transform, transformFrame=True):
        """Perform an arbitrary transformation on the pen, using the fontTools `Transform` class."""
        op = RecordingPen()
        tp = TransformPen(op, transform)
        self.replay(tp)
        self.value = op.value
        if transformFrame and self._frame:
            self._frame = self._frame.transform(transform)
        img = self.img()
        if img:
            img["rect"] = img["rect"].transform(transform)
        return self
    
    def align(self, rect, x="mdx", y="mdy", th=True, tv=False, transformFrame=True, h=None, return_offset=False):
        r = self.ambit(th, tv)
        if h is not None:
            r = r.seth(h)
        offset = align(r, rect, x, y)
        self.translate(*offset, transformFrame=transformFrame)
        if return_offset:
            return offset
        return self
    
    def x_align_to_frame(self, x=Edge.CenterX, th=0):
        if self._frame:
            return self.align(self.ambit(th=th, tv=0), x=x, transformFrame=1, th=1)
        else:
            raise Exception("No Frame")

    # deprecated camelcase
    xAlignToFrame = x_align_to_frame
    
    def translate(self, x, y=None, transformFrame=True):
        """Translate this shape by `x` and `y` (pixel values)."""
        if y is None:
            y = x
        return self.transform(Transform(1, 0, 0, 1, x, y), transformFrame=transformFrame)
    
    offset = translate

    def offset_x(self, x):
        return self.translate(x, 0)
    
    def offset_y(self, y):
        return self.translate(0, y)
    
    def zero_translate(self, th=1, tv=0):
        x, y, _, _ = self.ambit(th=th, tv=tv)
        self.translate(-x, -y)
        return self
    
    def center_on_point(self, rect, pt, interp=1):
        return self.translate(norm(interp, 0, rect.w/2-pt[0]), norm(interp, 0, rect.h/2-pt[1]))
    
    def skew(self, x=0, y=0, point=None):
        t = Transform()
        if not point:
            point = self.bounds().point("C") # maybe should be getFrame()?
        t = t.translate(point.x, point.y)
        t = t.skew(x, y)
        t = t.translate(-point.x, -point.y)
        return self.transform(t)
    
    def rotate(self, degrees, point=None):
        """Rotate this shape by a degree (in 360-scale, counterclockwise)."""
        t = Transform()
        if not point:
            point = self.bounds().point("C") # maybe should be getFrame()?
        elif isinstance(point, str):
            point = self.bounds().point(point)
        t = t.translate(point.x, point.y)
        t = t.rotate(math.radians(degrees))
        t = t.translate(-point.x, -point.y)
        return self.transform(t, transformFrame=False)
    
    def scale(self, scaleX, scaleY=None, point=None):
        """Scale this shape by a percentage amount (1-scale)."""
        t = Transform()
        if point != False:
            point = self.bounds().point("C") if point == None else point # maybe should be getFrame()?
            t = t.translate(point.x, point.y)
        t = t.scale(scaleX, scaleY or scaleX)
        if point != False:
            t = t.translate(-point.x, -point.y)
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
    
    # PEN-BASED MODIFICATIONS
    
    def flatten(self, length=10):
        """
        Runs a fontTools `FlattenPen` on this pen
        """
        if length == 0:
            return self
        dp = type(self)()
        fp = FlattenPen(dp, approximateSegmentLength=length, segmentLines=True)
        self.replay(fp)
        self.value = dp.value
        return self
    
    def smooth(self, length=100):
        rp = RecordingPen()
        fp = SmoothPointsPen(rp)
        self.replay(fp)
        self.value = rp.value
        return self
    
    def explode(self):
        """Read each contour into its own DATPen; returns a DATPens"""
        dp = RecordingPen()
        ep = ExplodingPen(dp)
        self.replay(ep)
        dps = self.multi_pen_class()
        for p in ep._pens:
            dp = type(self)()
            dp.value = p
            dp.attrs = deepcopy(self.attrs)
            dps.append(dp)
        return dps
    
    def repeat(self, times=1):
        copy = self.copy()
        copy_0_move, copy_0_data = copy.value[0]
        copy.value[0] = ("lineTo", copy_0_data)
        self.value = self.value[:-1] + copy.value
        if times > 1:
            self.repeat(times-1)
        return self
    
    # Iteration-manipulation
    
    def take(self, slice):
        self.value = self.value[slice]
        return self
    
    def take_curve(self, idx):
        a = self.value[idx-1][-1][-1]
        b, c, d = self.value[idx][-1]
        return Curve(a, b, c, d)

    def ups(self):
        "Convert this single pen into a collection of pens, with one-pen in the collection (this pen)"
        dps = self.multi_pen_class()
        dps.append(self.copy())
        return dps
    
    def pens(self):
        """Return a set representation of this"""
        if hasattr(self, "_pens"):
            return self
        else:
            return self.ups()
    
    def collapse(self, levels=100, onself=False):
        return self.multi_pen_class([self])
    
    def mod_pt(self, vidx, pidx, fn):
        pt = Point(self.value[vidx][-1][pidx])
        if callable(fn):
            res = fn(pt)
        else:
            res = pt.offset(*fn)
        try:
            self.value[vidx][-1][pidx] = res
        except TypeError:
            self.pvl()
            self.value[vidx][-1][pidx] = res
        return self
    
    def mod_pts(self, rect, fn):
        self.map_points(fn, lambda p: p.inside(rect))
        return self
    
    # Contour manipulation

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
        self.value = self.multi_pen_class(keep).implode().value
        return self
    
    def slicec(self, contour_slice):
        self.value = self.multi_pen_class(self.explode()[contour_slice]).implode().value
        return self
    
    # Iterating

    def map(self, fn:Callable[[int, str, list], Tuple[str, list]]):
        for idx, (mv, pts) in enumerate(self.value):
            self.value[idx] = fn(idx, mv, pts)
        return self
    
    def filter(self, fn:Callable[[int, str, list], bool]):
        vs = []
        for idx, (mv, pts) in enumerate(self.value):
            if fn(idx, mv, pts):
                vs.append((mv, pts))
        self.value = vs
        return self
    
    def map_points(self, fn, filter_fn=None):
        idx = 0
        for cidx, c in enumerate(self.value):
            move, pts = c
            pts = list(pts)
            for pidx, p in enumerate(pts):
                x, y = p
                if filter_fn and not filter_fn(*p):
                    continue
                result = fn(idx, x, y)
                if result:
                    pts[pidx] = result
                idx += 1
            self.value[cidx] = (move, pts)
        return self
    
    def walk(self,
        callback:Callable[["DraftingPen", int, dict], None],
        depth=0,
        visible_only=False,
        parent=None,
        alpha=1
        ):
        if visible_only and not self._visible:
            return
        
        if parent:
            self._parent = parent
        
        alpha = self._alpha * alpha
        
        is_dps = hasattr(self, "_pens")
        if is_dps:
            callback(self, -1, dict(depth=depth, alpha=alpha))
            for pen in self._pens:
                pen.walk(callback, depth=depth+1, visible_only=visible_only, parent=self, alpha=alpha)
            callback(self, 1, dict(depth=depth, alpha=alpha))
        else:
            callback(self, 0, dict(depth=depth, alpha=alpha))
    
    def remove_blanks(self):
        print("REMOVE BLANKS PEN", self)
        """If this is blank, `return True` (for recursive calls from DATPens)."""
        return len(self.value) == 0
    
    def interpolate(self, value, other):
        if len(self.value) != len(other.value):
            raise Exception("Cannot interpolate / diff lens")
        vl = []
        for idx, (mv, pts) in enumerate(self.value):
            ipts = []
            for jdx, p in enumerate(pts):
                pta = Point(p)
                try:
                    ptb = Point(other.value[idx][-1][jdx])
                except IndexError:
                    print(">>>>>>>>>>>>> Can’t interpolate", idx, mv, "///", other.value[idx])
                    raise IndexError
                ipt = pta.interp(value, ptb)
                ipts.append(ipt)
            vl.append((mv, ipts))
        return type(self)().vl(vl)
    
    def Interpolate(instances, value):
        spread = len(instances)-1
        start = math.floor(value*spread)
        end = math.ceil(value*spread)
        v = value*spread-start
        return instances[start].interpolate(v, instances[end])
    
    # GEOMETRICAL

    def nsew(self):
        pts = [el[1][-1] for el in self.value if len(el[1]) > 0]
        
        lines = []
        for i, p in enumerate(pts):
            if i + 1 == len(pts):
                lines.append(Line(p, pts[0]))
            else:
                lines.append(Line(p, pts[i+1]))
        
        mnx, mny, mxx, mxy = self.bounds().mnmnmxmx()
        min_ang = min([l.ang for l in lines])
        max_ang = max([l.ang for l in lines])
        #for idx, l in enumerate(lines):
        #    print(idx, ">", l.ang, min_ang, max_ang)
        xs = [l for l in lines if l.ang < 0.25 or l.ang > 2.5]
        ys = [l for l in lines if 1 < l.ang < 2]

        if len(ys) == 2 and len(xs) < 2:
            xs = [l for l in lines if l not in ys]
        elif len(ys) < 2 and len(xs) == 2:
            ys = [l for l in lines if l not in xs]
        
        #for l in ys:
        #    print(l.ang)

        #print(len(xs), len(ys))
        #print("--------------------")

        n = [l for l in xs if l.start.y == mxy or l.end.y == mxy][0]
        s = [l for l in xs if l.start.y == mny or l.end.y == mny][0]
        e = [l for l in ys if l.start.x == mxx or l.end.x == mxx][0]
        w = [l for l in ys if l.start.x == mnx or l.end.x == mnx][0]
        return n, s, e, w
    
    def avg(self):
        self.pvl()
        pts = []
        for _, _pts in self.value:
            if len(_pts) > 0:
                pts.extend(_pts)
        n = len(pts)
        #print("AVG", self, self.value)
        return Point(
            sum([p.x for p in pts])/n,
            sum([p.y for p in pts])/n)

    def point(self, pt):
        n, s, e, w = self.nsew()
        if pt == "NE":
            return n.pe
        elif pt == "NW":
            return n.pw
        elif pt == "SE":
            return s.pe
        elif pt == "SW":
            return s.pw
        elif pt == "N":
            return n.mid
        elif pt == "S":
            return s.mid
        elif pt == "E":
            return e.mid
        elif pt == "W":
            return w.mid

    @property
    def pne(self): return self.point("NE")
    @property
    def pnw(self): return self.point("NW")
    @property
    def psw(self): return self.point("SW")
    @property
    def pse(self): return self.point("SE")
    @property
    def pn(self): return self.point("N")
    @property
    def ps(self): return self.point("S")
    @property
    def pe(self): return self.point("E")
    @property
    def pw(self): return self.point("W")
    @property
    def en(self): return self.nsew()[0]
    @property
    def es(self): return self.nsew()[1]
    @property
    def ee(self): return self.nsew()[2]
    @property
    def ew(self): return self.nsew()[3]
    
    @property
    def ecx(self):
        n, s, e, w = self.nsew()
        return e.interp(0.5, w.reverse())
    
    @property
    def ecy(self):
        n, s, e, w = self.nsew()
        return n.interp(0.5, s.reverse())
    
    def edge(self, e):
        e = e.lower()
        if e == "n":
            return self.en
        elif e == "s":
            return self.es
        elif e == "e":
            return self.ee
        elif e == "w":
            return self.ew
    
    def shprop(self, s):
        if s in SH_UNARY_SUFFIX_PROPS:
            return SH_UNARY_SUFFIX_PROPS[s]
        return s
    
    def pinch(self, edge, inset):
        if isinstance(edge, str):
            e = getattr(self, self.shprop(edge))
        elif isinstance(edge, int):
            if edge == 0:
                e = self.en
            elif edge == 1:
                e = self.ee
            elif edge == 2:
                e = self.es
            elif edge == 3:
                e = self.ew
        ei = e.inset(inset)
        self.pvl()
        for idx, (mv, pts) in enumerate(self.value):
            for jdx, pt in enumerate(pts):
                if pt == e.start:
                    self.value[idx][1][jdx] = ei.start
                elif pt == e.end:
                    self.value[idx][1][jdx] = ei.end
        return self

    # COMPUTATIONAL OBJECT
    
    def define(self, *args, **kwargs):
        return self.context_record("$", "defs", None, *args, **kwargs)
    
    def declare(self, *whatever):
        # TODO do something with what's declared somehow?
        return self
    
    def macro(self, **kwargs):
        for k, v in kwargs.items():
            self.macros[k] = v
        return self

    def guide(self, grid:Grid):
        for k, v in grid.keyed.items():
            setattr(self, k, v)
        return self
    
    def print(self, *args):
        for a in args:
            if callable(a):
                print(a(self))
            else:
                print(a)
        return self

    def noop(self, *args, **kwargs):
        """Does nothing"""
        return self
    
    def sleep(self, time):
        """Sleep call within the chain (if you want to measure something)"""
        sleep(time)
        return self

    def chain(self,
        fn:Callable[["DraftingPen"], None],
        *args
        ):
        """
        For simple take-one callback functions in a chain
        """
        if fn:
            try:
                fn, metadata = fn
            except TypeError:
                metadata = {}
            
            res = fn(self, *args)
            if "returns" in metadata:
                return res
            elif isinstance(res, DraftingPen):
                return res
        return self
    
    ch = chain
    
    def cond(self, condition, if_true:Callable[["DraftingPen"], None], if_false:Callable[["DraftingPen"], None]=None):
        if callable(condition):
            condition = condition(self)
        # TODO make if_false optional
        if condition:
            if callable(if_true):
                if_true(self)
            else:
                self.gs(if_true)
        else:
            if if_false is not None:
                if callable(if_false):
                    if_false(self)
                else:
                    self.gs(if_false)
        return self

    # BOOLEAN OPERATIONS

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
    
    # ATTRIBUTES

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
                        c = normalize_color(v)
                        if hasattr(c, "a"):
                            default_w = 1 if c.a > 0 else 0
                        else:
                            default_w = 1
                        attrs[k] = dict(color=c, weight=existing.get("weight", default_w))
                    else:
                        c = normalize_color(v.get("color", 0))
                        if hasattr(c, "a"):
                            default_w = 1 if c.a > 0 else 0
                        else:
                            default_w = 1
                        attrs[k] = dict(weight=v.get("weight", existing.get("weight",default_w)), color=c)
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
    
    def lattr(self, tag, fn: Callable[["DraftingPen"], Optional["DraftingPen"]]):
        was_tag = self._current_attr_tag
        self._current_attr_tag = tag
        fn(self)
        self._current_attr_tag = was_tag
        return self
    
    # def calc_alpha(self):
    #     a = self._alpha
    #     p = self._parent
    #     while p:
    #         a = a * p._alpha
    #         p = p._parent
    #     return a
    
    def v(self, v):
        self.visible(bool(v))
        return self
    
    def a(self, v):
        self._alpha = v
        return self

    def f(self, *value):
        """Get/set a (f)ill"""
        if value:
            return self.attr(fill=value)
        else:
            return self.attr(field="fill")
    
    fill = f
    
    def s(self, *value):
        """Get/set a (s)troke"""
        if value:
            return self.attr(stroke=value)
        else:
            return self.attr(field="stroke")
    
    stroke = s
    
    def sw(self, value):
        """Get/set a (s)troke (w)idth"""
        if value is not None:
            return self.attr(strokeWidth=value)
        else:
            return self.attr(field="strokeWidth")
    
    strokeWidth = sw

    def img(self, src=None, rect=Rect(0, 0, 500, 500), pattern=True, opacity=1.0):
        """Get/set an image fill"""
        if src:
            return self.attr(image=dict(src=src, rect=rect, pattern=pattern, opacity=opacity))
        else:
            return self.attr(field="image")
    
    def img_opacity(self, opacity, key="default"):
        img = self.attr(key, "image")
        if not img:
            raise Exception("No image found")
        self.attrs[key]["image"]["opacity"] = opacity
        return self
    
    image = img

    def shadow(self, radius=10, color=(0, 0.3), clip=None):
        return self.attr(shadow=dict(color=normalize_color(color), radius=radius, clip=clip))
    
    def all_pens(self):
        pens = []
        if hasattr(self, "_pens"):
            pens = self.collapse()._pens
        if isinstance(self, self.single_pen_class):
            pens = [self]
        
        for pen in pens:
            if pen:
                if hasattr(pen, "_pens"):
                    for _p in pen.collapse()._pens:
                        if _p:
                            yield _p
                else:
                    yield pen
    
    # Fun pen manipulations

    def outline(self, offset=1, drawInner=True, drawOuter=True, cap="square", miterLimit=None):
        """AKA expandStroke"""
        op = OutlinePen(None, offset=offset, optimizeCurve=True, cap=cap, miterLimit=miterLimit)
        self.replay(op)
        op.drawSettings(drawInner=drawInner, drawOuter=drawOuter)
        g = op.getGlyph()
        p = self.single_pen_class()
        g.draw(p)
        self.value = p.value
        return self
    
    ol = outline
    
    def project(self, angle, width):
        offset = polarCoord((0, 0), math.radians(angle), width)
        self.translate(offset[0], offset[1])
        return self

    def castshadow(self, angle=-45, width=100, ro=1, fill=1):
        out = self.single_pen_class()
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
    
    # Some curvy/bendy things

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
    
    def split_t(self, t=0.5):
        a = self.value[0][-1][0]
        b, c, d = self.value[-1][-1]
        return splitCubicAtT(a, b, c, d, t)
    
    def add_pt_t(self, cuidx, t):
        cidx = 0
        insert_idx = -1
        c1, c2 = None, None

        for idx, (mv, pts) in enumerate(self.value):
            if mv == "curveTo":
                if cidx == cuidx:
                    insert_idx = idx
                    a = self.value[idx-1][-1][-1]
                    b, c, d = pts
                    c1, c2 = splitCubicAtT(a, b, c, d, t)
                cidx += 1
            elif mv == "lineTo":
                if cidx == cuidx:
                    insert_idx = idx
                    a = self.value[idx-1][-1][-1]
                    b = pts[0]
                    l = Line(a, b)
                    c1 = [l.t(0.5)]
                    c2 = [b]
                cidx += 1
        
        if c2:
            if len(c2) > 1:
                self.value[insert_idx] = ("curveTo", c1[1:])
                self.value.insert(insert_idx+1, ("curveTo", c2[1:]))
            else:
                self.value[insert_idx] = ("lineTo", c1)
                self.value.insert(insert_idx+1, ("lineTo", c2))
        return self
    
    def length(self, t=1):
        """Get the length of the curve for time `t`"""
        cc = CurveCutter(self)
        start = 0
        tv = t * cc.calcCurveLength()
        return tv
    
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

    def q2c(self):
        new_vl = []
        for mv, pts in self.value:
            if mv == "qCurveTo":
                decomposed = decomposeQuadraticSegment(pts)
                for dpts in decomposed:
                    qp1, qp2 = [Point(pt) for pt in dpts]
                    qp0 = Point(new_vl[-1][-1][-1])
                    cp1 = qp0 + (qp1 - qp0)*(2.0/3.0)
                    cp2 = qp2 + (qp1 - qp2)*(2.0/3.0)
                    new_vl.append(["curveTo", (cp1, cp2, qp2)])
            else:
                new_vl.append([mv, pts])
        self.value = new_vl
        return self