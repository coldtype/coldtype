import math

from fontTools.pens.boundsPen import BoundsPen
from fontTools.misc.transform import Transform
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.recordingPen import RecordingPen

from coldtype.geometry import Point, Rect, align
from coldtype.interpolation import norm
from coldtype.color import bw, rgb, hsl

from functools import partialmethod

THTV_WARNING = False

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
        global THTV_WARNING

        if th is not None:
            #traceback.print_stack()
            tx = th
            if not THTV_WARNING:
                print("! API CHANGE: th/tv are now tx/ty !")
                THTV_WARNING = True
        if tv is not None:
            #traceback.print_stack()
            ty = tv
            if not THTV_WARNING:
                print("! API CHANGE: th/tv are now tx/ty !")
                THTV_WARNING = True

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
    
    def ambit(self, th=None, tv=None, tx=0, ty=0, t=None) -> Rect:
        """
        Get the calculated rect boundary.
        
        - `tx` means `(t)rue (x)` (i.e. the true width/horizontal dimension (was previously th));
        - `ty` means `(t)rue (y)` (i.e. the true height/vertical dimension (was previously tv));
        
        Passing either ignores a non-bounds-derived frame
        in either dimension
        """
        
        tx, ty = self._normT(th, tv, tx, ty, t)
        f = self._data.get("frame", None)

        # true bounds
        if tx and ty:
            return self.bounds()
        
        # true no-bounds
        elif not tx and not ty and f:
            return f
        
        # partial bounds
        elif f and (self.val_present() or (self.data("glyphName") and len(self) == 0)):
            if self.empty():
                if tx:
                    f = f.setw(0)
                elif ty:
                    f = f.seth(0)
                return f
            else:
                b = self.bounds()
                if tx:
                    return Rect(b.x, f.y, b.w, f.h)
                else:
                    return Rect(f.x, b.y, f.w, b.h)
        
        # pass-to-els
        elif len(self._els) > 0:
            try:
                union = self._els[0].ambit(tx=tx, ty=ty)
                for p in self._els[1:]:
                    a = p.ambit(tx=tx, ty=ty)
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
        th=None, # deprecated
        tv=None, # deprecated
        tx=1,
        ty=0,
        transformFrame=True,
        h=None,
        returnOffset=False
        ):
        """
        Align this pen to another rect, defaults to the center.

        - `tx` means true-x (i.e. will disregard any invisible 'frame'
        set on the pen (as in the case of glyphs returned from StSt/Glyphwise));
        - `ty` means true-y, which is the same but for the vertical dimension
        """

        if not isinstance(rect, Rect):
            if hasattr(rect, "ambit"):
                rect = rect.ambit(tx=tx, ty=ty)
            elif hasattr(rect, "rect"):
                rect = rect.rect
            else:
                raise Exception("can't align to this object")
        
        tx, ty = self._normT(th, tv, tx, ty, None)
        r = self.ambit(tx=tx, ty=ty)

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
    
    def _align_compass(self, compass, rect, tx=1, ty=0):
        return self.align(rect, compass, tx=tx, ty=ty)
    
    #å = align

    alne = partialmethod(_align_compass, "NE")
    ale = partialmethod(_align_compass, "E")
    alse = partialmethod(_align_compass, "SE")
    als = partialmethod(_align_compass, "S")
    alsw = partialmethod(_align_compass, "SW")
    alw = partialmethod(_align_compass, "W")
    alnw = partialmethod(_align_compass, "NW")
    aln = partialmethod(_align_compass, "N")

    def xalign(self, rect=None, x="centerx", th=None, tv=None, tx=1, ty=0):
        tx, ty = self._normT(th, tv, tx, ty, None)

        if x == "C":
            x = "CX"
        
        if rect is None:
            rect = self.ambit(tx=tx, ty=ty)
        
        if callable(rect):
            rect = rect(self)
        
        self.align(rect, x=x, y=None, tx=tx, ty=ty)
        for el in self._els:
            el.align(rect, x=x, y=None, tx=tx, ty=ty)
        return self
    
    #xå = xalign

    def yalign(self, rect=None, y="centery", th=None, tv=None, tx=0, ty=1):
        tx, ty = self._normT(th, tv, tx, ty, None)

        if rect is None:
            rect = self.ambit(tx=tx, ty=ty)
        
        if callable(rect):
            rect = rect(self)
        
        self.align(rect, x=None, y=y, tx=tx, ty=ty)
        return self
    
    #yå = yalign

    def _normPoint(self, point=None, th=None, tv=None, tx=0, ty=0, **kwargs):
        tx, ty = self._normT(th, tv, tx, ty, kwargs.get("t"))

        if "pt" in kwargs:
            point = kwargs["pt"]
        
        a = self.ambit(tx=tx, ty=ty)
        if point is None:
            return a.pc
        elif point == 0:
            return a.psw
        elif point is False:
            return Point(0, 0)
        elif isinstance(point, str):
            if point.startswith("tx"):
                a = self.ambit(tx=1, ty=0)
                point = point[2:]
            elif point.startswith("ty"):
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
    
    def matrix(self, a, b, c, d, e, f, transformFrame=False):
        return self.transform(Transform(a, b, c, d, e, f), transformFrame=transformFrame)
    
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

    def shift(self, dx, dy, tx=1, ty=1):
        amb = self.ambit(tx=tx, ty=ty)
        self.translate(amb.w*dx, amb.h*dy)
        return self
    
    sh = shift
    
    def zero(self, th=None, tv=None, tx=0, ty=0):
        tx, ty = self._normT(th, tv, tx, ty, None)
        x, y, _, _ = self.ambit(tx=tx, ty=ty)
        self.translate(-x, -y)
        return self
    
    def centerZero(self, th=None, tv=None, tx=0, ty=0):
        tx, ty = self._normT(th, tv, tx, ty, None)

        x, y, w, h = self.ambit(tx=tx, ty=ty)
        nx, ny = -x-w/2, -y-h/2
        return (self
            .t(-x-w/2, -y-h/2)
            .data(centerZeroOffset=(nx, ny)))
    
    def centerPoint(self, rect, pt, interp=1, th=None, tv=None, tx=1, ty=0, **kwargs):
        tx, ty = self._normT(th, tv, tx, ty, None)

        if "i" in kwargs:
            interp = kwargs["i"]
        
        x, y = self._normPoint(pt, tx=tx, ty=ty, **kwargs)

        return self.translate(norm(interp, 0, rect.w/2-x), norm(interp, 0, rect.h/2-y))
    
    def skew(self, x=0, y=0, point=None, th=None, tv=None, tx=1, ty=0, **kwargs):
        tx, ty = self._normT(th, tv, tx, ty, None)

        t = Transform()
        px, py = self._normPoint(point, tx=tx, ty=ty, **kwargs)
        t = t.translate(px, py)
        t = t.skew(x, y)
        t = t.translate(-px, -py)
        return self.transform(t)
    
    def rotate(self, degrees, point=None, th=None, tv=None, tx=1, ty=1, **kwargs):
        """Rotate this shape by a degree (in 360-scale, counterclockwise)."""
        tx, ty = self._normT(th, tv, tx, ty, None)

        t = Transform()
        x, y = self._normPoint(point, tx=tx, ty=ty, **kwargs)
        t = t.translate(x, y)
        t = t.rotate(math.radians(degrees))
        t = t.translate(-x, -y)
        return self.transform(t, transformFrame=False)
    
    rt = rotate

    def r90(self, multiplier, point=None, tx=1, ty=1, **kwargs):
        return self.rotate(90*multiplier, point=point, tx=tx, ty=ty, **kwargs)
    
    def scale(self, scaleX, scaleY=None, point=None, th=None, tv=None, tx=1, ty=0, **kwargs):
        """Scale this shape by a percentage amount (1-scale)."""
        tx, ty = self._normT(th, tv, tx, ty, None)

        t = Transform()
        x, y = self._normPoint(point, tx=tx, ty=ty, **kwargs)
        if point is not False:
            t = t.translate(x, y)
        t = t.scale(scaleX, scaleY or scaleX)
        if point is not False:
            t = t.translate(-x, -y)
        return self.transform(t)
    
    def flipx(self):
        return self.scale(-1,1)
    
    def flipy(self):
        return self.scale(1,-1)
    
    def scaleToRect(self, rect, preserveAspect=True, shrink_only=False, tx=1, ty=0, return_number=False):
        """Scale this shape into a `Rect`."""
        bounds = self.bounds()
        if not bounds.nonzero():
            return self

        h = rect.w / bounds.w
        v = rect.h / bounds.h
        if preserveAspect:
            scale = h if h < v else v
            if shrink_only and scale >= 1:
                if return_number:
                    return 1
                return self
            
            if return_number:
                return scale
            else:
                return self.scale(scale, tx=tx, ty=ty)
        else:
            if shrink_only and (h >= 1 or v >= 1):
                if return_number:
                    return 1, 1
                return self
            
            if return_number:
                return h, v
            return self.scale(h, v, tx=tx, ty=ty)
    
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
        tx, ty = self._normT(th, tv, tx, ty, None)

        off = 0
        for idx, p in enumerate(self):
            if tracks is not None and idx > 0:
                t = tracks[idx-1]
                #print(t)
                off += t
            frame = p.ambit(tx=tx, ty=ty)
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
    
    def spread(self, tracking=0, tx=0, zero=False):
        "Horizontal distribution of elements"
        if zero:
            for p in self:
                p.zero(tx=tx)
        ambits = [p.ambit(tx=tx, ty=0).expand(tracking, "E") for p in self._els]
        
        ax = 0
        for idx, p in enumerate(self._els):
            aw = ambits[idx].w
            p.translate(ax, 0)
            ax += aw

        return self
    
    def stack(self, leading=0, ty=0, zero=False):
        "Vertical distribution of elements"
        if isinstance(leading, str) and "%" in leading:
            leading = self[0].ambit(ty=0).h * float(leading[:-1])/100
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
    
    def grid(self, every, spread=0, stack=0, zero=False):
        top = type(self)()
        row = None
        
        for idx, p in enumerate(self._els):
            if zero:
                p.zero()
            
            if idx%every == 0:
                row = type(self)()
                top.append(row)
            row.append(p)
        
        self._els = top._els

        for row in self:
            row.spread(spread)
        
        self.stack(stack)
        return self
    
    def gridlayer(self, nx, ny=None, track=0, lead=0):
        """Spread nx copies and then stack ny copies, w/ optional tracking & leading"""
        return (self
            .layer(nx)
            .spread(track)
            .layer(ny if ny is not None else nx)
            .stack(lead))
    
    def pasteup(self, styler=lambda p: p.f(bw(1)), padding=(5, 5), tx=1, ty=0, x="CX", y="CY"):
        r = self.ambit(tx=tx, ty=ty).inset(*[-x for x in padding]).zero()
        board = type(self)(r).ch(styler)
        self.align(r, tx=tx, ty=ty, x=x, y=y)
        return self.up().insert(0, board)
    
    def pattern_repeat(self, r):
        a = self.ambit(tx=1, ty=1)
        copies = type(self)()
        def repeater(_p):
            if a.mxx > r.mxx:
                copies.append(_p.copy().translate(-r.w, 0).fssw(hsl(0, a=0.5), -1, 0).rotate(0))
            if a.mxy > r.mxy:
                copies.append(_p.copy().translate(0, -r.h).fssw(hsl(0.25, a=0.5), -1, 0).rotate(0))
            if a.mny < r.mny:
                copies.append(_p.copy().translate(0, r.h).fssw(hsl(0.5, a=0.5), -1, 0).rotate(0))
            if a.mnx < r.mnx:
                copies.append(_p.copy().translate(r.w, 0).fssw(hsl(0.75, a=0.5), -1, 0).rotate(0))
        repeater(self)
        for c in list(copies):
            repeater(c)
        return self.up().append(copies)
    
    def track_with_width(self, t):
        """Track-out/distribute elements"""
        x = 0
        for idx, p in enumerate(self._els):
            frame = p.ambit()
            p.translate(x + t, 0)
            x += frame.w
        return self
    
    def track_to_width(self, width, pullToEdges=False, r=0):
        return self.track_to_rect(Rect(width, 0), pullToEdges=pullToEdges, r=r)
    
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