from coldtype.runon import Runon
from coldtype.geometry import Rect
from coldtype.grid import Grid
from coldtype.color import hsl, bw
from coldtype.random import random_series

#self\.assertEqual\(([^,]+),([^)]+)\)
#assert $1 ==$2

_view_rs1 = random_series()


class Mondrian(Runon):
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
            el = Mondrian(r)
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
            self._val = None
        else:
            for el in self._els:
                el.grid(columns, rows, tags)
        return self
    
    def cssgrid(self, cols, rows, ascii, **kwargs):
        if self.val_present():
            if not hasattr(self, "_borders"):
                self._borders = []

            g = Grid(self.r, cols, rows, ascii)
            for k, v in g.keyed.items():
                self.append(Mondrian(v).tag(k))
            
            self._val = None
            self._borders.extend(g.borders)
        
        for k, v in kwargs.items(): self[k].cssgrid(*v)
        return self
    
    def borders(self, regular=None, bold=None):
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