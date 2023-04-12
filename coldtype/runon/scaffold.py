from coldtype.runon import Runon
from coldtype.geometry import Rect
from coldtype.grid import Grid
from coldtype.color import hsl, bw
from coldtype.random import random_series

import re
from typing import Pattern

#self\.assertEqual\(([^,]+),([^)]+)\)
#assert $1 ==$2

_view_rs1 = random_series()


class Scaffold(Runon):
    def __init__(self, *val, warn_float=True):
        self.warn_float = warn_float
        
        super().__init__(*val)

    def sum(self):
        if self.val_present():
            return self._val
        
        r = None
        for el in self._els:
            if r:
                rr = el.rect
                if rr.nonzero():
                    r = r.union(rr)
            else:
                rr = el.rect
                if rr.nonzero():
                    r = rr
        if r is not None:
            return r
        else:
            return Rect(0,0,0,0)

    @property
    def rect(self) -> Rect:
        return self.sum()
    
    r = rect

    def _extend_with_tags(self, rects, tags):
        for idx, r in enumerate(rects):
            el = Scaffold(r, warn_float=self.warn_float)
            try:
                el.tag(tags[idx])
            except IndexError:
                pass
            self.append(el)

    def divide(self, amt, edge, tags=[], forcePixel=False):
        if self.val_present():
            self._extend_with_tags(
                self.r.divide(amt, edge, forcePixel), tags)
            self._val = None
        else:
            for el in self._els:
                el.divide(amt, edge, tags=tags, forcePixel=forcePixel)
        return self
    
    def subdivide(self, amt, edge, tags=[]):
        if self.val_present():
            self._extend_with_tags(
                self.r.subdivide(amt, edge), tags)
            self._val = None
        else:
            for el in self._els:
                el.subdivide(amt, edge, tags)
        return self
    
    def grid(self, columns=2, rows=2, tags=[]):
        if self.val_present():
            self._extend_with_tags(
                self.r.grid(columns, rows), tags)
            
            if not hasattr(self, "_borders"):
                self._borders = []
            
            for _x in range(0, columns-1):
                self._borders.append([
                    self[_x].ee.pn,
                    self[_x].ee.intersection(self.r.es)])
            
            for _y in range(0, rows-1):
                self._borders.append([
                    self[_y*columns].psw,
                    self[_y*columns].es.intersection(self.r.ee)])
            
            self._val = None
        else:
            for el in self._els:
                el.grid(columns, rows, tags)
        return self
    
    def cssgridmod(self, mods, **kwargs):
        for k, v in mods.items():
            for m in self.match(k):
                m.cssgrid(*v)

        for k, v in kwargs.items():
            self[k].cssgrid(*v)
        
        return self
    
    def cssgrid(self, cols, rows, ascii, mods={}, **kwargs):
        if self.val_present():
            if not hasattr(self, "_borders"):
                self._borders = []

            r = self.r
            g = Grid(self.r, cols, rows, ascii, warn_float=self.warn_float)
            for k, v in g.keyed.items():
                if v.w > r.w or v.h > r.h or v.x < 0 or v.y < 0 or v.w < 0 or v.h < 0:
                    v = Rect(0, 0, 0, 0)
                self.append(Scaffold(v, warn_float=self.warn_float).tag(k))
            
            self._val = None
            self._borders.extend(g.borders)
        
        self.cssgridmod(mods, **kwargs)
        
        return self
    
    def borders(self):
        if hasattr(self, "_borders"):
            from coldtype.runon.path import P
            return (P().enumerate(self._borders, lambda x: P().line(x.el).fssw(-1, 0, 1)))
    
    def cssborders(self, regular=None, bold=None):
        if hasattr(self, "_borders"):
            from coldtype.runon.path import P
            out = P()
            for b in sorted(self._borders, key=lambda b: b[2]):
                if regular == -1 and not b[2]:
                    continue
                elif bold == -1 and b[2]:
                    continue
                
                out.append(P()
                    .line(b[0].edge(b[1]))
                    .fssw(-1, 0, 4 if b[2] else 2)
                    .ch(bold if b[2] else regular))
            return out
    
    def sort(self, attr="x", reverse=False):
        if self.depth() == 1:
            self._els = sorted(self._els, key=lambda el: getattr(el.r, attr), reverse=reverse)
        return self
    
    def view(self, fontSize=32):
        from coldtype.runon.path import P
        from coldtype.text import Style

        out = P()
        ridx = 0

        def walker(el, pos, data):
            nonlocal ridx
            if pos == 0:
                out.append(P(
                    P(el.r).f(hsl(_view_rs1[ridx], 1)).alpha(0.1),
                    P(el.r.inset(2)).fssw(-1, bw(0, 0.2), 4),
                    P().text(el.tag() or ("u:" + data["utag"])
                        , Style("Times", fontSize, load_font=0, fill=bw(0, 0.5))
                        , el.r.inset(7, 10))))
                ridx += 1
        
        self.postwalk(walker)
        return out
    
    # @property
    # def ne(self): return self.r.pne
    # @property
    # def nw(self): return self.r.pnw
    # @property
    # def sw(self): return self.r.psw
    # @property
    # def se(self): return self.r.pse
    # @property
    # def n(self): return self.r.pn
    # @property
    # def s(self): return self.r.ps
    # @property
    # def e(self): return self.r.pe
    # @property
    # def w(self): return self.r.pw

    @property
    def pne(self): return self.r.pne
    @property
    def pnw(self): return self.r.pnw
    @property
    def psw(self): return self.r.psw
    @property
    def pse(self): return self.r.pse
    @property
    def pn(self): return self.r.pn
    @property
    def ps(self): return self.r.ps
    @property
    def pe(self): return self.r.pe
    @property
    def pw(self): return self.r.pw
    @property
    def pc(self): return self.r.pc
    
    @property
    def en(self): return self.r.en
    @property
    def es(self): return self.r.es
    @property
    def ee(self): return self.r.ee
    @property
    def ew(self): return self.r.ew

    def joinp(self, regex):
        from coldtype.runon.path import P
        return P().enumerate(self.match(regex), lambda x: P(x.el.r))
    
    def scale(self, scale):
        def walker(el, pos, _):
            if pos == 0:
                el._val = el._val.scale(scale, scale)
        
        self.walk(walker)
        return self