import math
from re import L
from typing import Callable, Optional

from fontTools.misc.transform import Transform

from coldtype.sh import sh
from coldtype.geometry import Geometrical, Rect
from coldtype.pens.draftingpen import DraftingPen
from coldtype.beziers import CurveCutter


class DraftingPens(DraftingPen):
    def __init__(self, pens=None):
        self._pens = []
        super().__init__()

        self.single_pen_class = DraftingPen
        self._in_progress_pen = None

        self.typographic = True
        self.layered = False
        self.data = {}

        self._alpha = 1
        self._parent = None
        self.container = None
        self._visible = True

        self.subs = {
            "□": "ctx.bounds()",
            "■": "_dps.bounds()"
        }

        if pens:
            for p in pens:
                self.append(p)
    
    def tree(self, out=None, depth=0) -> str:
        """Hierarchical string representation"""
        if out is None:
            out = []
        out.append(" |"*depth + " " + str(self))
        for pen in self._pens:
            if hasattr(pen, "_pens"):
                pen.tree(out=out, depth=depth+1)
            else:
                out.append(" |"*(depth+1) + " " + str(pen))
        return "\n".join(out)
    
    def __repr__(self):
        return f"<{type(self).__name__}:{len(self._pens)}>"
    
    def __len__(self):
        return len(self._pens)
    
    def __getitem__(self, index):
        return self._pens[index]
        
    def __setitem__(self, index, pen):
        self._pens[index] = pen
    
    def __iadd__(self, item):
        return self.append(item)
    
    def __add__(self, item):
        return self.append(item)
    
    def append(self, pen, allow_blank=False):
        if isinstance(pen, Geometrical):
            return self._pens.append(self.single_pen_class(pen))
        elif isinstance(pen, DraftingPen):
            self._pens.append(pen)
        else:
            try:
                for p in pen:
                    if p:
                        self._pens.append(p)
            except TypeError:
                self._pens.append(pen)
        return self
    
    def insert(self, index, pen):
        if pen:
            self._pens.insert(index, pen)
        return self
    
    def extend(self, pens):
        if hasattr(pens, "_pens"):
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
        self._pens = list(reversed(self._pens))
        return self
    
    # Sizing
    
    def ambit(self, th=False, tv=False):
        """Get the calculated rect boundary of the DraftingPens;
        `th` means `(t)rue (h)orizontal`;
        `ty` means `(t)rue (v)ertical`;
        passing either ignores a non-bounds-derived frame
        in either dimension"""
        if self._frame and (th == False and tv == False):
            return self._frame
        elif self._frame and (th or tv) and not (th and tv):
            f = self._frame
            b = self.bounds()
            if th and tv:
                return b
            elif th:
                return Rect(b.x, f.y, b.w, f.h)
            else:
                return Rect(f.x, b.y, f.w, b.h)
        else:
            try:
                union = self._pens[0].ambit(th=th, tv=tv)
                for p in self._pens[1:]:
                    if hasattr(p, "_pens") or len(p.value) > 0:
                        union = union.union(p.ambit(th=th, tv=tv))
                return union
            except Exception as e:
                return Rect(0,0,0,0)
    
    def bounds(self):
        """Calculated bounds of a DraftingPens"""
        return self.ambit(th=1, tv=1)
    
    def gs(self, s, fn=None, tag=None, writer=None):
        return self.append(
            self.single_pen_class().gs(s,
                tag=tag, fn=fn, writer=writer,
                macros=self.macros,
                ctx=self, dps=type(self)()))
    
    def gss(self, s):
        dps = type(self)()
        xs = sh(s, ctx=self, dps=dps)
        return self.extend(dps._pens)
    
    def gsgroup(self, fn):
        grouper = self.copy(with_data=False)
        grouper.define(**self.defs.values)
        grouper.macros = self.macros
        grouper._pens = []
        res = fn(grouper)
        self.ap(res)
        return self
    
    # RecordingPen contract

    def moveTo(self, p0):
        self._in_progress_pen = self.single_pen_class()
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
    
    def replay(self, pen):
        self.pen().replay(pen)
    
    def record(self, pen):
        """Alias for append"""
        if callable(pen):
            return self.append(pen(self))
        else:
            return self.append(pen)
    
    def explode(self):
        """Noop on a set"""
        return self
    
    # Drawing
    
    def pen(self):
        """A flat representation of this set as a single pen"""
        dp = self.single_pen_class()
        fps = self.collapse()
        for p in fps._pens:
            dp.record(p)
        if len(fps._pens) > 0:
            for k, attrs in fps._pens[0].attrs.items():
                dp.attr(tag=k, **attrs)
        dp.frame(self.ambit())
        return dp
    
    def collapse(self, levels=100, onself=False):
        """AKA `flatten` in some programming contexts, though
        `flatten` is a totally different function here that flattens
        outlines; this function flattens nested collections into
        one-dimensional collections"""
        pens = []
        for idx, p in enumerate(self._pens):
            if hasattr(p, "_pens") and levels > 0:
                pens.extend(p.collapse(levels=levels-1)._pens)
            else:
                pens.append(p)
        dps = self.multi_pen_class(self)(pens)
        if self.layered:
            dps.layered = True
        if onself:
            self._pens = dps._pens
            return self
        else:
            return dps
        
    def copy(self, with_data=False):
        """Get a completely new copy of this whole set of pens,
        usually done so you can duplicate and further modify a
        DATPens without mutating the original"""
        dps = type(self)()
        for p in self._pens:
            dps.append(p.copy(with_data=with_data))
        return dps
    
    def remove_blanks(self):
        """Remove blank pens"""
        nonblank_pens = []
        for pen in self._pens:
            if hasattr(pen, "_pens"):
                pen.remove_blanks()
                nonblank_pens.append(pen)
            elif len(pen.value) > 0:
                nonblank_pens.append(pen)
            #rb = pen.remove_blanks()
            #print("RB RES", rb, bool(rb))
            #if not rb:
            #    nonblank_pens.append(pen)
        self._pens = nonblank_pens
        return self
    
    def remove_overlap(self):
        for p in self._pens:
            p.removeOverlap()
        return self
    
    removeOverlap = remove_overlap
    
    def transform(self, transform, transformFrame=True):
        for p in self._pens:
            p.transform(transform, transformFrame=transformFrame)
        if transformFrame and self._frame:
            self._frame = self._frame.transform(transform)
        return self
    
    def attr(self, key="default", field=None, **kwargs):
        if field: # getting, not setting, kind of weird to return the first value?
            if len(self._pens) > 0:
                return self._pens[0].attr(key=key, field=field)
            else:
                return None
        for p in self._pens:
            p.attr(key, **kwargs)
        return self
    
    def lattr(self, tag, fn: Callable[[DraftingPen], Optional[DraftingPen]]):
        for p in self._pens:
            p.lattr(tag, fn)
        return self
    
    def round_to(self, rounding):
        """Round all values for all pens in this set to nearest multiple of rounding value (rather than places, as in `round`)"""
        for p in self._pens:
            p.round_to(rounding)
        return self
    
    def xa(self, x="centerx"):
        for pen in self:
            pen.xAlignToFrame(x)
        return self
    
    def distribute(self, v=False, tracks=None):
        off = 0
        for idx, p in enumerate(self):
            if tracks is not None and idx > 0:
                t = tracks[idx-1]
                #print(t)
                off += t
            frame = p.ambit()
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
        """Track-out/distribute elements"""
        for idx, p in enumerate(self._pens):
            frame = p.ambit()
            if v:
                p.translate(0, t*idx)
            else:
                p.translate(t*idx, 0)
        return self
    
    def track_with_width(self, t):
        """Track-out/distribute elements"""
        x = 0
        for idx, p in enumerate(self._pens):
            frame = p.ambit()
            p.translate(x + t, 0)
            x += frame.w
        return self
    
    def track_to_rect(self, rect, pullToEdges=False, r=0):
        """Distribute pens evenly within a frame"""
        if len(self) == 1:
            return self.align(rect)
        total_width = 0
        pens = self._pens
        if r:
            pens = list(reversed(pens))
        start_x = pens[0].ambit(th=pullToEdges).x
        end_x = pens[-1].ambit(th=pullToEdges).point("SE").x
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
    
    def interleave(self, style_fn, direction=-1, recursive=True):
        """Provide a callback-lambda to interleave new DATPens between the existing ones; useful for stroke-ing glyphs, since the stroked glyphs can be placed behind the primary filled glyphs."""
        pens = []
        for idx, p in enumerate(self._pens):
            if recursive and hasattr(p, "_pens"):
                _p = p.interleave(style_fn, direction=direction, recursive=True)
                pens.append(_p)
            else:
                try:
                    np = style_fn(idx, p.copy())
                except TypeError:
                    np = style_fn(p.copy())
                if isinstance(np, self.single_pen_class):
                    np = [np]
                if direction < 0:
                    pens.extend(np)
                pens.append(p)
                if direction > 0:
                    pens.extend(np)

        self._pens = pens
        return self
    
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
    
    def distribute_on_path(self, path, offset=0, cc=None, notfound=None, center=False):
        if cc:
            cutter = cc
        else:
            cutter = CurveCutter(path)
        if center is not False:
            offset = (cutter.length-self.bounds().w)/2 + center
        limit = len(self._pens)
        for idx, p in enumerate(self._pens):
            f = p.ambit()
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

        if limit < len(self._pens):
            self._pens = self._pens[0:limit]
        return self
    
    # deprecated
    distributeOnPath = distribute_on_path

    def map(self, fn: Callable[[int, DraftingPen], Optional[DraftingPen]]):
        """Apply `fn` to all top-level pen(s) in this set;
        if `fn` returns a value, it will overwrite
        the pen it was given as an argument;
        fn lambda receives `idx, p` as arguments"""
        for idx, p in enumerate(self._pens):
            result = fn(idx, p)
            if result:
                self._pens[idx] = result
        return self
    
    def mmap(self, fn: Callable[[int, DraftingPen], None]):
        """Apply `fn` to all top-level pen(s) in this set but
        do not look at return value; first m in mmap
        stands for `mutate`;
        fn lambda receives `idx, p` as arguments"""
        for idx, p in enumerate(self._pens):
            fn(idx, p)
        return self
    
    def filter(self, fn: Callable[[int, DraftingPen], bool]):
        """Filter top-level pen(s)"""
        dps = self.multi_pen_class()
        for idx, p in enumerate(self._pens):
            if fn(idx, p):
                dps.append(p)
        #self._pens = dps._pens
        #return self
        return dps
    
    def pmap(self, fn):
        """Apply `fn` to all individal pens, recursively"""
        for idx, p in enumerate(self._pens):
            if hasattr(p, "_pens"):
                p.pmap(fn)
            else:
                fn(idx, p)
        return self
    
    def pfilter(self, fn):
        """Filter all pens, recursively"""
        to_keep = []
        for idx, p in enumerate(self._pens):
            if hasattr(p, "_pens"):
                matches = p.pfilter(fn)
                if len(matches) > 0:
                    to_keep.extend(matches)
            if fn(idx, p):
                to_keep.append(p)
        try:
            return type(self)(to_keep)
        except TypeError:
            return self.multi_pen_class(to_keep)
    
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
            if p.tag() == tag:
                yield p
    
    def find(self, tag):
        matches = []
        def finder(p, a, b):
            if p.tag() == tag:
                matches.append(p)
        self.walk(finder)
        return matches
    
    def get(self, k):
        tagged = self.fft(k)
        if tagged:
            return tagged.copy()
    
    def fmmap(self, filter_fn:Callable[[int, DraftingPen], bool], map_fn:Callable[[int, DraftingPen], None]):
        for idx, p in enumerate(self._pens):
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
                    self._pens.remove(tagged)
            else:
                self._pens.remove(k)
        return self
    
    def mfilter(self, fn):
        """Same as `filter` but (m)utates this DATPens
        to now have only the filtered pens"""
        self._pens = self.filter(fn)
        return self
    
    def collapseonce(self):
        pens = []
        for idx, p in enumerate(self._pens):
            pens.extend(p)
        self._pens = pens
        return self
    
    def collapse(self, levels=100, onself=False):
        """AKA `flatten` in some programming contexts, though
        `flatten` is a totally different function here that flattens outlines; this function flattens nested collections into one-dimensional collections"""
        pens = []
        for idx, p in enumerate(self._pens):
            if hasattr(p, "_pens") and levels > 0:
                pens.extend(p.collapse(levels=levels-1)._pens)
            else:
                pens.append(p)
        dps = self.multi_pen_class(pens)
        if self.layered:
            dps.layered = True
        if onself:
            self._pens = dps._pens
            return self
        else:
            return dps
    
    flatten = collapse # deprecated but used in the wild
    
    def frameSet(self, th=False, tv=False):
        """All the frames of all the pens"""
        if self._frame:
            return super().frameSet(th=th, tv=tv)
        dps = self.multi_pen_class()
        for p in self._pens:
            if p._frame:
                dps.append(p.frameSet(th=th, tv=tv))
        return dps
    
    #def cast(self, _class, *args):
        #return _class(self._pens)
    #    res = _class(self, *args)
    #    res.attrs = deepcopy(self.attrs)
    #    return res