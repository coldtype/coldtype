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
        
        if self.val_present():
            try:
                cbp = BoundsPen(None)
                self._val.replay(cbp)
                mnx, mny, mxx, mxy = cbp.bounds
                b = Rect((mnx, mny, mxx - mnx, mxy - mny))
            except:
                pass
        
        if len(self._els) > 0:
            bs = []
            for el in self._els:
                eb = el.bounds()
                if eb and eb.nonzero():
                    bs.append(eb)
            
            if len(bs) > 0:
                b = bs[0]
                for eb in bs[1:]:
                    b = b.union(eb)
        
        return b
    
    def _normT(self, th, tv, tx, ty, t):
        import traceback

        if th is not None:
            traceback.print_stack()
            tx = th
            raise Exception("! API CHANGE: th is now: tx")
        if tv is not None:
            print("HELLO")
            ty = tv
            raise Exception("! API CHANGE: tv is now: ty")

        if t is not None:
            tx = bool(int(t))
            if tx:
                ty = int((t-1)*10) == 1
            else:
                ty = int(t)*10 == 1
        else:
            tx, ty = tx, ty
        return tx, ty
    
    def empty(self):
        return len(self._val.value) == 0
    
    def ambit(self, th=None, tv=None, tx=0, ty=0, t=None):
        """Get the calculated rect boundary;
        `th` means `(t)rue (h)orizontal`;
        `ty` means `(t)rue (v)ertical`;
        passing either ignores a non-bounds-derived frame
        in either dimension"""
        
        th, tv = self._normT(th, tv, tx, ty, t)
        f = self._data.get("frame", None)

        # true bounds
        if th and tv:
            return self.bounds()
        
        # true no-bounds
        elif not th and not tv and f:
            return f
        
        # partial bounds
        elif f and (self.val_present() or (self.data("glyphName") and len(self) == 0)):
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
                union = self._els[0].ambit(tx=th, ty=tv)
                for p in self._els[1:]:
                    a = p.ambit(tx=th, ty=tv)
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
    
    getFrame = ambit
    
    def align(self,
        rect,
        x="mdx",
        y="mdy",
        th=None,
        tv=None,
        tx=1,
        ty=0,
        transformFrame=True,
        h=None,
        returnOffset=False
        ):
        """Align this pen to another rect, defaults to the center;
        `th` means true-horizontal (i.e. will disregard any invisible 'frame'
        set on the pen (as in the case of glyphs returned from StSt/Glyphwise));
        `tv` means true-vertical, which is the same but for the vertical dimension"""

        if not isinstance(rect, Rect):
            rect = rect.rect
        
        th, tv = self._normT(th, tv, tx, ty, None)
        r = self.ambit(tx=th, ty=tv)

        if h is not None:
            r = r.seth(h)
        
        self.data(_last_align_rect=rect)
        
        offset = align(r, rect, x, y)
        self.translate(*offset,
            transformFrame=transformFrame)
        
        if returnOffset:
            return offset
        else:
            return self
    
    å = align

    def xalign(self, rect=None, x="centerx", th=None, tv=None, tx=1, ty=0):
        th, tv = self._normT(th, tv, tx, ty, None)

        if x == "C":
            x = "CX"
        
        if rect is None:
            rect = self.ambit(tx=th, ty=tv)
        
        if callable(rect):
            rect = rect(self)
        
        self.align(rect, x=x, y=None, tx=th, ty=tv)
        for el in self._els:
            el.align(rect, x=x, y=None, tx=th, ty=tv)
        return self
    
    xå = xalign

    def yalign(self, rect=None, y="centery", th=None, tv=None, tx=0, ty=1):
        th, tv = self._normT(th, tv, tx, ty, None)

        if rect is None:
            rect = self.ambit(tx=th, ty=tv)
        
        if callable(rect):
            rect = rect(self)
        
        self.align(rect, x=None, y=y, th=th, tv=tv)
        return self
    
    xå = xalign

    def _normPoint(self, point=None, th=None, tv=None, tx=0, ty=0, **kwargs):
        th, tv = self._normT(th, tv, tx, ty, kwargs.get("t"))

        if "pt" in kwargs:
            point = kwargs["pt"]
        
        a = self.ambit(tx=th, ty=tv)
        if point is None:
            return a.pc
        elif point == 0:
            return a.psw
        elif point is False:
            return Point(0, 0)
        elif isinstance(point, str):
            if point.startswith("th"):
                a = self.ambit(tx=1, ty=0)
                point = point[2:]
            elif point.startswith("tv"):
                a = self.ambit(tx=0, ty=1)
                point = point[2:]
            elif point.startswith("t"):
                a = self.ambit(tx=1, ty=1)
                point = point[1:]
            return a.point(point)
        elif (not (isinstance(point[1], int)
                or isinstance(point[1], float))
            and hasattr(self, "_normPoint")):
            return self[point[0]]._normPoint(point[1])
        else:
            return Point(point)
    
    def transform(self, transform, transformFrame=True):
        """Perform an arbitrary transformation on the pen, using the fontTools `Transform` class."""

        if self.val_present():
            op = RecordingPen()
            tp = TransformPen(op, transform)
            self._val.replay(tp)
            self._val.value = op.value
        
        f = self._data.get("frame")
        if transformFrame and f:
            self.data(frame=f.transform(transform))
        
        for p in self._els:
            p.transform(transform, transformFrame=transformFrame)
        
        substructure = self._data.get("substructure")
        if substructure:
            substructure.transform(transform, transformFrame=transformFrame)
        
        img = self.img()
        if img:
            img["rect"] = img["rect"].transform(transform)
        
        return self
    
    def invertYAxis(self, height):
        rp = RecordingPen()
        tp = TransformPen(rp, (1, 0, 0, -1, 0, height))
        self.replay(tp)
        self._val.value = rp.value
        return self
    
    def nonlinear_transform(self, fn):
        for el in self._els:
            el.nonlinear_transform(fn)
        
        if self.val_present():
            for idx, (move, pts) in enumerate(self._val.value):
                if len(pts) > 0:
                    _pts = []
                    for _pt in pts:
                        x, y = _pt
                        _pts.append(fn(x, y))
                    self._val.value[idx] = (move, _pts)
        
        return self
    
    nlt = nonlinear_transform
    
    def translate(self, x, y=None, transformFrame=True):
        """Translate this shape by `x` and `y` (pixel values)."""
        if y is None:
            y = x
        return self.transform(Transform(1, 0, 0, 1, x, y), transformFrame=transformFrame)
    
    offset = translate
    t = translate
    
    def zero(self, th=None, tv=None, tx=0, ty=0):
        th, tv = self._normT(th, tv, tx, ty, None)
        x, y, _, _ = self.ambit(tx=th, ty=tv)
        self.translate(-x, -y)
        return self
    
    def centerZero(self, th=None, tv=None, tx=0, ty=0):
        th, tv = self._normT(th, tv, tx, ty, None)

        x, y, w, h = self.ambit(tx=th, ty=tv)
        nx, ny = -x-w/2, -y-h/2
        return (self
            .t(-x-w/2, -y-h/2)
            .data(centerZeroOffset=(nx, ny)))
    
    def centerPoint(self, rect, pt, interp=1, th=None, tv=None, tx=1, ty=0, **kwargs):
        th, tv = self._normT(th, tv, tx, ty, None)

        if "i" in kwargs:
            interp = kwargs["i"]
        
        x, y = self._normPoint(pt, tx=th, ty=tv, **kwargs)

        return self.translate(norm(interp, 0, rect.w/2-x), norm(interp, 0, rect.h/2-y))
    
    def skew(self, x=0, y=0, point=None, th=None, tv=None, tx=1, ty=0, **kwargs):
        th, tv = self._normT(th, tv, tx, ty, None)

        t = Transform()
        px, py = self._normPoint(point, tx=th, ty=tv, **kwargs)
        t = t.translate(px, py)
        t = t.skew(x, y)
        t = t.translate(-px, -py)
        return self.transform(t)
    
    def rotate(self, degrees, point=None, th=None, tv=None, tx=1, ty=1, **kwargs):
        """Rotate this shape by a degree (in 360-scale, counterclockwise)."""
        th, tv = self._normT(th, tv, tx, ty, None)

        t = Transform()
        x, y = self._normPoint(point, tx=th, ty=tv, **kwargs)
        t = t.translate(x, y)
        t = t.rotate(math.radians(degrees))
        t = t.translate(-x, -y)
        return self.transform(t, transformFrame=False)
    
    rt = rotate
    
    def scale(self, scaleX, scaleY=None, point=None, th=None, tv=None, tx=1, ty=0, **kwargs):
        """Scale this shape by a percentage amount (1-scale)."""
        th, tv = self._normT(th, tv, tx, ty, None)

        t = Transform()
        x, y = self._normPoint(point, tx=th, ty=tv, **kwargs)
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
    
    # multi-elements

    def distribute(self, v=False, tracks=None, th=None, tv=None, tx=0, ty=0):
        th, tv = self._normT(th, tv, tx, ty, None)

        off = 0
        for idx, p in enumerate(self):
            if tracks is not None and idx > 0:
                t = tracks[idx-1]
                #print(t)
                off += t
            frame = p.ambit(tx=th, ty=tv)
            if v:
                if frame.y < 0:
                    p.translate(0, -frame.y)
                p.translate(0, off)
                off += frame.h
            else:
                if frame.x < 0:
                    p.translate(-frame.x, 0)
                if frame.x > 0 and th:
                    p.translate(-frame.x, 0)
                p.translate(off, 0)
                off += frame.w
        return self
    
    def spread(self, tracking=0, th=0, zero=False):
        "Horizontal distribution of elements"
        if zero:
            for p in self:
                p.zero()
        ambits = [p.ambit(tx=th, ty=0).expand(tracking, "E") for p in self._els]
        
        ax = 0
        for idx, p in enumerate(self._els):
            aw = ambits[idx].w
            p.translate(ax, 0)
            ax += aw

        return self
    
    def stack(self, leading=0, ty=0, zero=False):
        "Vertical distribution of elements"
        if zero:
            for p in self:
                p.zero()
        ambits = [p.ambit(tx=0, ty=ty).expand(leading, "N") for p in self._els]
        for idx, p in enumerate(self._els):
            for a in ambits[idx+1:]:
                p.translate(0, a.h)
        return self
    
    def track(self, t, v=False):
        """Track-out/distribute elements"""
        for idx, p in enumerate(self._els):
            if v:
                p.translate(0, -t*idx)
            else:
                p.translate(t*idx, 0)
        return self
    
    def lead(self, leading):
        "Vertical spacing"
        ln = len(self._els)

        try:
            if self._els[-1].ambit().y > self._els[0].ambit().y:
                leading = -leading
        except IndexError:
            pass
        
        for idx, p in enumerate(self._els):
            p.translate(0, leading*(ln-1-idx))
        return self
    
    def gridlayer(self, nx, ny=None, track=0, lead=0):
        """Spread nx copies and then stack ny copies, w/ optional tracking & leading"""
        return (self
            .layer(nx)
            .spread(track)
            .layer(ny if ny is not None else nx)
            .stack(lead))
    
    def track_with_width(self, t):
        """Track-out/distribute elements"""
        x = 0
        for idx, p in enumerate(self._els):
            frame = p.ambit()
            p.translate(x + t, 0)
            x += frame.w
        return self
    
    def track_to_rect(self, rect, pullToEdges=False, r=0):
        """Distribute pens evenly within a frame"""
        if len(self) == 1:
            return self.align(rect)
        total_width = 0
        pens = self._els
        if r:
            pens = list(reversed(pens))
        start_x = pens[0].ambit(tx=pullToEdges).x
        end_x = pens[-1].ambit(tx=pullToEdges).point("SE").x
        # TODO easy to knock out apostrophes here based on a callback, last "actual" frame
        total_width = end_x - start_x
        leftover_w = rect.w - total_width
        tracking_value = leftover_w / (len(self)-1)
        if pullToEdges:
            xoffset = rect.x - pens[0].bounds().x
        else:
            xoffset = rect.x - pens[0].ambit().x
        for idx, p in enumerate(pens):
            if idx == 0:
                p.translate(xoffset, 0)
            else:
                p.translate(xoffset+tracking_value*idx, 0)
        return self
    
    trackToRect = track_to_rect

    def connect(self, *others):
        return (type(self)([self, *others])
            .distribute()
            .pen())

    @property
    def x(self): return self.ambit().x
    @property
    def y(self): return self.ambit().y
    @property
    def w(self): return self.ambit().w
    @property
    def h(self): return self.ambit().h

    @property
    def tx(self): return self.ambit(tx=1).x
    @property
    def ty(self): return self.ambit(ty=1).y
    @property
    def tw(self): return self.ambit(tx=1).w
    @property
    def th(self): return self.ambit(ty=1).h