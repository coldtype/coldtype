import math, tempfile, pickle, inspect
from pathlib import Path

from typing import Optional, Callable, Tuple
#from collections.abc import Callable

from fontTools.misc.transform import Transform

from random import randint
from noise import pnoise1

from drafting.sh import sh
from drafting.pens.draftingpens import DraftingPen, DraftingPens
from drafting.interpolation import norm

from drafting.geometry import Rect, Edge, Point, Line, Geometrical
from coldtype.beziers import CurveCutter, splitCubicAtT
from drafting.color import normalize_color, hsl

from coldtype.pens.outlinepen import OutlinePen
from coldtype.pens.translationpen import TranslationPen, polarCoord


def listit(t):
    return list(map(listit, t)) if isinstance(t, (list, tuple)) else t


# class DATBPT():
#     def __init__(self, ps):
#         self.ps = ps
    
#     def angle(self):
#         b = self.ps[0]
#         c = self.ps[1]
#         d = self.ps[2]
#         return c.cdist(b), c.cdist(d)
    
#     def rotate(self, angle):
#         c = self.ps[1]
#         bdist, bang = c.cdist(self.ps[0])
#         ddist, dang = c.cdist(self.ps[2])
#         self.ps[0] = c.project(bang + angle, bdist)
#         self.ps[2] = c.project(dang + angle, ddist)
#         return self
    
#     def offset(self, x, y):
#         self.ps = [p.offset(x, y) for p in self.ps]
#         return self
    
#     def __floordiv__(self, other):
#         return self.offset(0, other)
    
#     def __truediv__(self, other):
#         return self.offset(other, 0)


class DATPen(DraftingPen):
    """
    Main vector representation in Coldtype
    
    DATPen is a subclass of fontTools ``RecordingPen``
    """
    def __init__(self, *args, **kwargs):
        """**kwargs support is deprecated, should not accept any arguments"""
        super().__init__()
        self.single_pen_class = DATPen
        self.multi_pen_class = DATPens

        self._current_attr_tag = "default"
        self.clearAttrs()
        self.attr("default", **kwargs)
        self.typographic = False
        self._tag = "?"
        self._alpha = 1
        self._parent = None
        self.container = None
        self.glyphName = None
        self.data = {}
        self._visible = True

        for idx, arg in enumerate(args):
            if isinstance(arg, str):
                self.tag(arg)
            elif isinstance(arg, DraftingPen):
                self.replace_with(arg)
            elif isinstance(arg, Rect):
                self.rect(arg)
            elif isinstance(arg, Line):
                self.line(arg).s(0, 0.5, 1).sw(5)
            elif isinstance(arg, Point):
                self.oval(Rect.FromCenter(arg, 50, 50))
    
    def __str__(self):
        v = "" if self._visible else "ø-"
        return f"<{v}DP(typo:int({self.typographic})({self.glyphName}))——tag:{self._tag}/data:{self.data}>"
    
    def __len__(self):
        return len(self.value)
    
    def __bool__(self):
        return True
        return bool(len(self) > 0 or self._frame)
    
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
    
    def fvl(self):
        allpts = []
        for mv, pts in self.value:
            if len(pts) > 0:
                allpts.extend(pts)
        return allpts
    
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
    
    # def mod_bpt(self, idx, fn):
    #     pidxs = [[idx, -2], [idx, -1], [idx+1, 0]]
    #     bpt = DATBPT([self.value[i][-1][j] for (i,j) in pidxs])
    #     fn(bpt)
    #     for idx, (i,j) in enumerate(pidxs):
    #         self.value[i][-1][j] = bpt.ps[idx]
    #     #self.mod_pt(idx+1, 0, fn)
    #     #self.mod_pt(idx, -1, fn)
    #     #self.mod_pt(idx, -2, fn)
    #     return self
    
    def add_pt(self, cuidx, t, fn=None):
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
        
        if c2:
            self.value[insert_idx] = ("curveTo", c1[1:])
            self.value.insert(insert_idx+1, ("curveTo", c2[1:]))

            if fn:
                self.pvl()
                self.mod_bpt(insert_idx, fn)
            #return insert_idx
        return self
    
    def take(self, slice):
        self.value = self.value[slice]
        return self
    
    def ups(self):
        dps = DATPens()
        dps.append(self.copy())
        return dps
    
    as_set = ups
    
    def calc_alpha(self):
        a = self._alpha
        p = self._parent
        while p:
            a = a * p._alpha
            p = p._parent
        return a
    
    def getFrame(self, th=False, tv=False):
        return self.ambit(th=th, tv=tv)
    
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
                if filter_fn and not filter_fn(p):
                    continue
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
    
    def fenced(self, *lines):
        if len(lines) == 1 and isinstance(lines[0], Rect):
            return self.intersection(DATPen().rect(lines[0]))
        return self.intersection(DATPen().fence(*lines))
    
    ƒ = fenced
    
    def connect(self):
        return self.map(lambda i, mv, pts: ("lineTo" if i > 0 and mv == "moveTo" else mv, pts))
    
    def collapse(self):
        """For compatibility with calls to a DATPens"""
        return DATPens([self])
    
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
    
    ol = outline
    
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
    
    def fence(self, *edges):
        self.moveTo(edges[0][0])
        self.lineTo(edges[0][1])
        for edge in edges[1:]:
            self.lineTo(edge[0])
            self.lineTo(edge[1])
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
    
    def skel(self):
        return DPS([
            self,
            self.skeleton().f(None).s(hsl(0.9)).sw(4)
        ])
    
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
    
    _context = None
    _pen_class = None
    _precompose_save = None
    
    def center_on_point(self, rect, pt, interp=1):
        return self.translate(norm(interp, 0, rect.w/2-pt[0]), norm(interp, 0, rect.h/2-pt[1]))

    def copy(self, with_data=False):
        """Make a totally fresh copy; useful given the DATPen’s general reliance on mutable state."""
        dp = self.single_pen_class()
        self.replay(dp)
        for tag, attrs in self.attrs.items():
            dp.attr(tag, **attrs)
        dp.glyphName = self.glyphName
        if with_data:
            dp.data = self.data
            if self.typographic:
                dp._frame = self._frame
                dp.typographic = True
        return dp

    def add_data(self, key, value=None):
        if value is None:
            self.data = key
        else:
            self.data[key] = value
        return self
    
    def editable(self, tag):
        self.tag(tag)
        self.editable = True
        return self
    
    def contain(self, rect):
        """For conveniently marking an arbitrary `Rect` container."""
        self.container = rect
        return self
    
    def blendmode(self, blendmode=None):
        if blendmode:
            return self.attr(blendmode=blendmode)
        else:
            return self.attr(field="blendmode")
        return self
    
    def clearFrame(self):
        """Remove the DATPen frame."""
        self._frame = None
        return self
    
    def addFrame(self, frame, typographic=False, passthru=False):
        """Add a new frame to the DATPen, replacing any old frame. Passthru ignored, there for compatibility"""
        self._frame = frame
        if typographic:
            self.typographic = True
        return self
    
    def frameSet(self, th=False, tv=False):
        """Return a new DATPen representation of the frame of this DATPen."""
        return self.single_pen_class(fill=("random", 0.25)).rect(self.getFrame(th=th, tv=tv))
    
    def trackToRect(self, rect, pullToEdges=False, r=0):
        """Distribute pens evenly within a frame"""
        if len(self) == 1:
            return self.align(rect)
        total_width = 0
        pens = self.pens
        if r:
            pens = list(reversed(pens))
        start_x = pens[0].getFrame(th=pullToEdges).x
        end_x = pens[-1].getFrame(th=pullToEdges).point("SE").x
        # TODO easy to knock out apostrophes here based on a callback, last "actual" frame
        total_width = end_x - start_x
        leftover_w = rect.w - total_width
        tracking_value = leftover_w / (len(self)-1)
        if pullToEdges:
            xoffset = rect.x - pens[0].bounds().x
        else:
            xoffset = rect.x - pens[0].getFrame().x
        for idx, p in enumerate(pens):
            if idx == 0:
                p.translate(xoffset, 0)
            else:
                p.translate(xoffset+tracking_value*idx, 0)
        return self
    
    def at_rotation(self, degrees, fn:Callable[["DATPen"], None], point=None):
        self.rotate(degrees)
        fn(self)
        self.rotate(-degrees)
        return self
    
    # def at_scale(self, scale, fn:Callable[["DATPen"], None]):
    #     self.scale(scale)
    #     self.scale()
    #     # TODO
    #     return self
    
    def filmjitter(self, doneness, base=0, speed=(10, 20), scale=(2, 3), octaves=16):
        """
        An easy way to make something move in a way reminiscent of misregistered film
        """
        nx = pnoise1(doneness*speed[0], base=base, octaves=octaves)
        ny = pnoise1(doneness*speed[1], base=base+10, octaves=octaves)
        return self.translate(nx * scale[0], ny * scale[1])
    
    def _get_renderer_state(self, pen_class, context):
        if not pen_class:
            pen_class = DATPen._pen_class
        if not pen_class:
            raise Exception("No _pen_class")

        if not context:
            context = DATPen._context
        elif context == -1:
            context = None
        
        return pen_class, context
    
    def precompose(self, rect, placement=None, opacity=1, scale=1, pen_class=None, context=None):
        pc, ctx = self._get_renderer_state(pen_class, context)
        img = pc.Precompose(self, rect, context=ctx, scale=scale, disk=DATPen._precompose_save)
        return self.single_pen_class().rect(placement or rect).img(img, (placement or rect), False, opacity).f(None)
    
    def rasterized(self, rect, scale=1, pen_class=None, context=None):
        """
        Same as precompose but returns the Image created rather
        than setting that image as the attr-image of this pen
        """
        pc, ctx = self._get_renderer_state(pen_class, context)
        return pc.Precompose(self, rect, scale=scale, context=ctx, disk=DATPen._precompose_save)
    
    def mod_pixels(self, rect, scale=0.1, mod=lambda rgba: None, pen_class=None, context=None):
        import skia
        import PIL.Image
        rasterized = self.rasterized(rect, scale=scale, pen_class=pen_class, context=context)
        pi = PIL.Image.fromarray(rasterized, "RGBa")
        for x in range(pi.width):
            for y in range(pi.height):
                r, g, b, a = pi.getpixel((x, y))
                res = mod((r, g, b, a))
                if res:
                    pi.putpixel((x, y), tuple(res))
        out = skia.Image.frombytes(pi.convert('RGBA').tobytes(), pi.size, skia.kRGBA_8888_ColorType)
        return self.single_pen_class().rect(rect).img(out, rect, False).f(None)

    def potrace(self, rect, poargs=[], invert=True, pen_class=None, context=None):
        import skia
        from PIL import Image
        from pathlib import Path
        from subprocess import run
        from fontTools.svgLib import SVGPath

        pc, ctx = self._get_renderer_state(pen_class, context)

        img = pc.Precompose(self, rect, context=ctx)
        pilimg = Image.fromarray(img.convert(alphaType=skia.kUnpremul_AlphaType))
        binpo = Path("bin/potrace")
        if not binpo.exists():
            binpo = Path(__file__).parent.parent.parent / "bin/potrace"

        with tempfile.NamedTemporaryFile(prefix="coldtype_tmp", suffix=".bmp") as tmp_bmp:
            pilimg.save(tmp_bmp.name)
            rargs = [str(binpo), "-s"]
            if invert:
                rargs.append("--invert")
            rargs.extend([str(x) for x in poargs])
            rargs.extend(["-o", "-", "--", tmp_bmp.name])
            if False:
                print(">>>", " ".join(rargs))
            result = run(rargs, capture_output=True)
            if False:
                print(result)
            t = Transform()
            t = t.scale(0.1, 0.1)
            svgp = SVGPath.fromstring(result.stdout, transform=t)
            if False:
                print(svgp)
            dp = self.single_pen_class()
            svgp.draw(dp)
            return dp.f(0)
    
    def phototype(self, rect, blur=5, cut=127, cutw=3, fill=1, pen_class=None, context=None, rgba=[0, 0, 0, 1], luma=True):
        r, g, b, a = rgba
        pc, ctx = self._get_renderer_state(pen_class, context)

        import skia
        import coldtype.filtering as fl

        first_pass = dict(ImageFilter=fl.blur(blur))
        
        if luma:
            first_pass["ColorFilter"] = skia.LumaColorFilter.Make()

        cut_filters = [
            fl.as_filter(
                fl.contrast_cut(cut, cutw),
                a=a, r=r, g=g, b=b)]
            
        if fill is not None:
            cut_filters.append(fl.fill(normalize_color(fill)))

        return (self
            .precompose(rect, pen_class=pc, context=ctx)
            .attr(skp=first_pass)
            .precompose(rect, pen_class=pc, context=ctx)
            .attr(skp=dict(
                ColorFilter=fl.compose(*cut_filters))))
    
    def color_phototype(self, rect, blur=5, cut=127, cutw=15, pen_class=None, context=None, rgba=[1, 1, 1, 1]):
        return self.phototype(rect, blur, 255-cut, cutw, fill=None, pen_class=pen_class, context=context, rgba=rgba, luma=False)
    
    def DiskCached(path:Path, build_fn: Callable[[], "DATPen"]):
        dpio = None
        fn_src = inspect.getsource(build_fn)
        if not path.exists():
            path.parent.mkdir(parents=True, exist_ok=True)
            dpio = build_fn()
        else:
            try:
                dpio = pickle.load(open(path, "rb"))
                old_fn_src = dpio.data.get("fn_src", "")
                if fn_src != old_fn_src:
                    dpio = build_fn()
            except pickle.PickleError:
                dpio = build_fn()
        
        dpio.data["fn_src"] = fn_src
        pickle.dump(dpio, open(path, "wb"))
        return dpio
    
    def pickle(self, dst):
        dst.parent.mkdir(parents=True, exist_ok=True)
        pickle.dump(self, open(str(dst), "wb"))
        return self
    
    def Unpickle(self, src):
        return pickle.load(open(str(src), "rb"))


class DATPens(DATPen, DraftingPens):
    """
    A set/collection of DATPen’s
    
    Behaves like a list but can be queried somewhat like a DOM
    """
    def __init__(self, pens=[]):
        DraftingPens.__init__(self) # TODO pass pens

        self.single_pen_class = DATPen
        self.pens = []
        self.typographic = True
        self.layered = False
        #self._tag = "?"
        self._alpha = 1
        self._parent = None
        self.container = None
        self._frame = None
        self.data = {}
        self._visible = True
        
        self.locals = dict(DP=DATPen)
        self.subs = {
            "□": "ctx.bounds()",
            "■": "_dps.bounds()"
        }


        if isinstance(pens, DraftingPen):
            self.append(pens)
        else:
            for pen in pens:
                self.append(pen)
    
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
        if callable(pen):
            pen = pen(self)
        if pen or allow_blank:
            if isinstance(pen, Geometrical):
                self.pens.append(DATPen(pen))
            elif isinstance(pen, DATPen):
                self.pens.append(pen)
            elif isinstance(pen, DraftingPen):
                self.pens.append(DATPen(pen))
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
    
    ap = append
    
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
            self._frame = frame
            self.typographic = typographic
        return self
    
    def getFrame(self, th=False, tv=False):
        """Get the frame of the DATPens;
        `th` means `(t)rue (h)orizontal`;
        `ty` means `(t)rue (v)ertical`;
        passing either ignores a non-bounds-derived frame
        in either dimension"""
        if self._frame and (th == False and tv == False):
            return self._frame
        else:
            try:
                union = self.pens[0].ambit(th=th, tv=tv)
                for p in self.pens[1:]:
                    union = union.union(p.ambit(th=th, tv=tv))
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
    
    def get(self, k):
        tagged = self.fft(k)
        if tagged:
            return tagged.copy()
    
    def define(self, *args, **kwargs):
        return self.context_record("$", "defs", None, *args, **kwargs)
    
    def declare(self, *whatever):
        # TODO do something with what's declared somehow?
        return self
    
    def realize(self):
        for k, v in self._register.values.items():
            self.append(DATPen(v).tag(k))
        return self
    
    def record(self, pen):
        """Alias for append"""
        if callable(pen):
            return self.append(pen(self))
        else:
            return self.append(pen)
    
    def explode(self):
        """Noop on a set"""
        return self
    
    # Overrides

    #def nlt(self, fn, flatten=0):
    #    return self.pmap(lambda idx, p: p.nonlinear_transform(fn))
    
    # def round(self, rounding):
    #     """Round all values for all pens in this set"""
    #     for p in self.pens:
    #         p.round(rounding)
    #     return self
    
    # def round_to(self, rounding):
    #     """Round all values for all pens in this set to nearest multiple of rounding value (rather than places, as in `round`)"""
    #     for p in self.pens:
    #         p.round_to(rounding)
    #     return self
    
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
    
    def fmmap(self, filter_fn:Callable[[int, DATPen], bool], map_fn:Callable[[int, DATPen], None]):
        for idx, p in enumerate(self.pens):
            if filter_fn(idx, p):
                map_fn(idx, p)
        return self

    def ffg(self, glyph_name):
        """(f)ind the (f)irst (g)lyph named this name"""
        return list(self.glyphs_named(glyph_name))[0]
    
    def fft(self, tag, fn=None):
        """(f)ind the (f)irst (t)agged with `tag`"""
        try:
            tagged = list(self.tagged(tag))[0]
            if fn:
                fn(tagged)
                return self
            else:
                return tagged
        except:
            if fn:
                return self
            return None
    
    def remove(self, *args):
        """remove a pen from these pens by identify, or by tag if a string is passed"""
        for k in args:
            if isinstance(k, str):
                tagged = self.fft(k)
                if tagged:
                    self.pens.remove(tagged)
            else:
                self.pens.remove(k)
        return self
    
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
        if self._frame:
            return super().frameSet(th=th, tv=tv)
        dps = DATPens()
        for p in self.pens:
            if p._frame:
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
        
    def distribute_on_path(self, path, offset=0, cc=None, notfound=None, center=False):
        if cc:
            cutter = cc
        else:
            cutter = CurveCutter(path)
        if center is not False:
            offset = (cutter.length-self.bounds().w)/2 + center
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
    
    def skel(self, pts=None, start=0):
        _pts = pts or DPS()
        for idx, pen in enumerate(self):
            if hasattr(pen, "pens"):
                pen.skel(pts=_pts)
            else:
                c = (start + idx)*0.37
                pen.f(hsl(c, s=1, a=0.05)).s(hsl(c, s=0.65, a=0.5)).sw(8)
                _pts.append(pen.copy().skeleton().f(None).s(hsl(c+0.05, s=1, a=0.35)).sw(4))
        if not pts:
            self.append(_pts)
        return self
    
    def all_guides(self, field="defs", sw=6, l=0):
        dps = DATPens()
        for idx, (k, x) in enumerate(getattr(self, field).values.items()):
            c = hsl(idx/2.3, 1, l=0.35, a=0.35)
            if isinstance(x, Geometrical) or isinstance(x, DraftingPen):
                g = (DATPen(x)
                    .translate(l, 0)
                    .f(None)
                    .s(c).sw(sw))
                if k in ["gb", "gc", "gs", "gxb"]:
                    c = hsl(0.6, 1, 0.5, 0.25)
                    g.s(c).sw(2)
                dps += g
                dps += DATText(k, ["Helvetica", 24, dict(fill=c.with_alpha(0.5).darker(0.2))], Rect.FromCenter(g.bounds().pc, 24))
        return dps
    
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
DPS = DATPens
DP = DATPen


class DATText(DATPen):
    def __init__(self, text, style, frame):
        self.text = text
        self.style = style
        self.visible = True
        super().__init__()
        self.addFrame(frame)
    
    def __str__(self):
        return f"<DT({self.text}/{self.style.font})/>"