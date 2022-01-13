from random import random

from coldtype.runon import Runon
from coldtype.geometry import Rect
from coldtype.grid import Grid
from coldtype.color import hsl, bw


class Layout(Runon):
    def sum(self):
        if self.val_present():
            return self._val
        
        r = None
        for el in self._els:
            if r:
                r = r.union(el.rect)
            else:
                r = el.rect
        return r

    @property
    def rect(self) -> Rect:
        return self.sum()
    
    r = rect

    def _extend_with_tags(self, rects, tags):
        for idx, r in enumerate(rects):
            el = Layout(r)
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
        else:
            for el in self._els:
                el.grid(columns, rows, tags)
        return self
    
    def cssgrid(self, cols, rows, ascii):
        if self.val_present():
            g = Grid(self.r, cols, rows, ascii)
            for k, v in g.keyed.items():
                self.append(Layout(v).tag(k))
            self._val = None
        return self
    
    def sort(self, attr="x", reverse=False):
        if self.depth() == 2:
            self._els = sorted(self._els, key=lambda el: getattr(el.r, attr), reverse=reverse)
        return self
    
    def view(self, fontSize=32):
        from coldtype.runon.path import P
        from coldtype.text import Style

        out = P()

        def walker(el, pos, data):
            if pos == 0:
                out.append(P(
                    P(el.r).f(hsl(random(), 1)).alpha(0.1),
                    P(el.r.inset(2)).fssw(-1, bw(0, 0.2), 4),
                    P().text(el.tag() or ("u:" + data["utag"])
                        , Style("Times", fontSize, load_font=0, fill=bw(0, 0.5))
                        , el.r.inset(7, 10))))
        
        self.postwalk(walker)
        return out

L = Layout