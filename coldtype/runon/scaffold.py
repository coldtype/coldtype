from coldtype.runon import Runon
from coldtype.geometry import Rect
from coldtype.grid import Grid
from coldtype.color import hsl, bw
from coldtype.random import random_series
from collections import defaultdict

import re

_view_rs1 = None

class Scaffold(Runon):
    @staticmethod
    def AspectGrid(r:Rect, x:int, y:int, align:str="C"):
        s = Scaffold(r.fit_aspect(x, y, align))
        return s.numeric_grid(x, y)

    def __init__(self, *val, warn_float=True):
        self.warn_float = warn_float
        
        super().__init__(*val)
    
    def find_(self, finder_fn=None, fn=None, index=0, none_ok=0, find_one=False, **kwargs):
        if isinstance(finder_fn, str):
            def to_xy(xy):
                return [int(n) for n in xy.split("|")]
            
            def wrap(xy):
                x, y = to_xy(xy)
                w = len(self.cols())
                h = len(self.rows())
                if x < 0:
                    x = w + x
                if y < 0:
                    y = h + y
                return f"{x}|{y}"
            
            if "*" in finder_fn:
                start, extend = finder_fn.split("*")
                start = wrap(start)
                start = to_xy(start)
                extend = to_xy(extend)
                x, y = start
                ex, ey = extend
                end = [x+(ex-1), y+(ey-1)]
                
                if ex == 0: end[0] = start[0]
                elif ex < 0: end[0] = x+(ex+1)
                
                if ey == 0: end[1] = start[1]
                elif ey < 0: end[1] = y+(ey+1)
                
                finder_fn = f"{start[0]}|{start[1]}+{end[0]}|{end[1]}"
            
            elif "-" in finder_fn:
                finder_fn = wrap(finder_fn)
        
        return super().find_(finder_fn=finder_fn, fn=fn, index=index, none_ok=none_ok, find_one=find_one, **kwargs)

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
    
    def annotate_rings(self):
        grid_data = self.data("grid")
        columns = grid_data.get("columns")
        rows = grid_data.get("rows")

        def rectangular_rings(xs, ys):
            center_x, center_y = xs // 2, ys // 2
            max_radius = max(center_x, center_y)
            rings = []

            for r in range(max_radius + 1):
                ring = [
                    self[f"{x}|{y}"].data(ring=r, ring_e=r/max_radius)
                    for x in range(center_x - r, center_x + r + 1)
                    for y in range(center_y - r, center_y + r + 1)
                    if (
                        (x == center_x - r or x == center_x + r or y == center_y - r or y == center_y + r)
                        and 0 <= x < xs and 0 <= y < ys)]
                if ring:
                    rings.append(ring)
            return rings

        return rectangular_rings(columns, rows)
    
    def numeric_grid(self, columns=2, rows=None, gap=None, column_gap=0, row_gap=0, start_1=False, start_bottom=True, annotate_rings=False
        ):
        if rows is None:
            rows = columns
        if gap is not None:
            column_gap = gap
            row_gap = gap
        
        self.data(grid=dict(columns=columns, rows=rows))

        names = []

        if column_gap == 0 and row_gap == 0:
            for ridx, row in enumerate(range(0, rows)):
                row_names = []
                for cidx, col in enumerate(range(0, columns)):
                    row_names.append(f"{cidx}|{ridx}")
                names.append(" ".join(row_names))
            
            if start_bottom:
                names = list(reversed(names))
            
            self.cssgrid(("a " * columns).strip(), ("a " * rows).strip(), " / ".join(names))
        else:
            _cols = []
            _rows = []
            for ridx, row in enumerate(range(0, rows)):
                _rows.append("a")
                _cols = []
                row_names = []
                for cidx, col in enumerate(range(0, columns)):
                    _cols.append("a")
                    row_names.append(f"{cidx}|{ridx}")
                    if cidx != columns-1:
                        _cols.append(str(column_gap))
                        row_names.append(f"cg.{cidx}|{ridx}")
                
                names.append(" ".join(row_names))
                if ridx != rows-1:
                    _rows.append(str(row_gap))
                    row_names = []
                    for cidx, col in enumerate(range(0, columns)):
                        row_names.append(f"rg.{cidx}|{ridx}")
                        if cidx != columns-1:
                            row_names.append(f"rcg.{cidx}|{ridx}")
                    names.append(" ".join(row_names))

            if start_bottom:
                names = list(reversed(names))
            
            self.cssgrid(" ".join(_cols).strip(), " ".join(_rows), " / ".join(names), forcePixel=True)

        if not hasattr(self, "_borders"):
            self._borders = []
        
        first_row = names[0].split(" ")
        last_row = names[-1].split(" ")

        for cidx, _ in enumerate(first_row[:-1]):
            self._borders.append([self[first_row[cidx]].pne, self[last_row[cidx]].pse])
        
        for ridx, row in enumerate(names[:-1]):
            rs = row.split(" ")
            self._borders.append([self[rs[0]].psw, self[rs[-1]].pse])
        
        for cell in self:
            tag = cell.tag()
            if "." not in tag:
                c, r = [int(x) for x in cell.tag().split("|")]
                ch = not((not r%2 and not c%2) or (r%2 and c%2))
                if start_1:
                    r += 1
                    c += 1
                
                cell.data(row=r, col=c, checker=ch)
            
        if annotate_rings:
            self.annotate_rings()
        
        return self
    
    def labeled_grid(self, columns=2, rows=2, column_gap=0, row_gap=0, start_1=False, start_bottom=False):
        from string import ascii_lowercase
        possible_names = [a for a in ascii_lowercase]
        possible_names.extend([f"{a}{a}" for a in ascii_lowercase])
        possible_names.extend([f"{a}{a}{a}" for a in ascii_lowercase])

        if start_1:
            inc = 1
        else:
            inc = 0

        names = []

        if column_gap == 0 and row_gap == 0:
            for ridx, row in enumerate(range(0, rows)):
                row_names = []
                for cidx, col in enumerate(range(0, columns)):
                    row_names.append(f"{possible_names[ridx]}{cidx+inc}")
                names.append(" ".join(row_names))
            
            if start_bottom:
                names = list(reversed(names))
            
            self.cssgrid(("a " * columns).strip(), ("a " * rows).strip(), " / ".join(names))
        else:
            _cols = []
            _rows = []
            for ridx, row in enumerate(range(0, rows)):
                _rows.append("a")
                _cols = []
                row_names = []
                for cidx, col in enumerate(range(0, columns)):
                    _cols.append("a")
                    row_names.append(f"{ascii_lowercase[ridx]}{cidx+inc}")
                    if cidx != columns-1:
                        _cols.append(str(column_gap))
                        row_names.append(f"cg.{ascii_lowercase[ridx]}{cidx+inc}")
                
                names.append(" ".join(row_names))
                if ridx != rows-1:
                    _rows.append(str(row_gap))
                    row_names = []
                    for cidx, col in enumerate(range(0, columns)):
                        row_names.append(f"rg.{ascii_lowercase[ridx]}{cidx+inc}")
                        if cidx != columns-1:
                            row_names.append(f"rcg.{ascii_lowercase[ridx]}{cidx+inc}")
                    names.append(" ".join(row_names))

            if start_bottom:
                names = list(reversed(names))
            
            self.cssgrid(" ".join(_cols).strip(), " ".join(_rows), " / ".join(names))

        if not hasattr(self, "_borders"):
            self._borders = []
        
        first_row = names[0].split(" ")
        last_row = names[-1].split(" ")

        for cidx, _ in enumerate(first_row[:-1]):
            self._borders.append([self[first_row[cidx]].pne, self[last_row[cidx]].pse])
        
        for ridx, row in enumerate(names[:-1]):
            rs = row.split(" ")
            self._borders.append([self[rs[0]].psw, self[rs[-1]].pse])
        
        for cell in self:
            tag = cell.tag()
            if "." not in tag:
                _r = re.search(r"[a-z]{1,3}", cell.tag())[0]
                _c = re.search(r"[0-9]{1,3}", cell.tag())[0]
                #_r, _c = list(cell.tag())
                r = possible_names.index(_r)
                c = int(_c)
                ch = not((not r%2 and not c%2) or (r%2 and c%2))
                if start_1:
                    r += 1
                    c += 1
                
                cell.data(row=r, col=c, checker=ch)
        
        return self
    
    def cells(self):
        return self.copy().filter(lambda x: "." not in x.tag())
    
    def gaps(self):
        return self.copy().filter(lambda x: "." in x.tag())
    
    def rows(self):
        rows = defaultdict(list)
        for cell in self:
            row = cell.data("row")
            if row is not None:
                rows[row].append(cell.copy())
        return list(rows.values())

    def cols(self):
        cols = defaultdict(list)
        for cell in self:
            col = cell.data("col")
            if col is not None:
                cols[col].append(cell.copy())
        return list(cols.values())
    
    def grid(self, columns=2, rows=None, tags=[]):
        if rows is None:
            rows = columns

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
    
    def cssgrid(self, cols, rows, ascii, mods={}, forcePixel=False, **kwargs):
        if self.val_present():
            if not hasattr(self, "_borders"):
                self._borders = []

            r = self.r

            if callable(cols):
                cols = cols(self)
            if callable(rows):
                rows = rows(self)

            g = Grid(self.r, cols, rows, ascii, warn_float=self.warn_float, forcePixel=forcePixel)
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
    
    def view(self, fontSize=22, fill=False, stroke=True, vectors=False):
        global _view_rs1
        if _view_rs1 is None:
            _view_rs1 = random_series()

        from coldtype.runon.path import P
        from coldtype.text import Style, StSt, Font

        out = P()
        ridx = 0

        def walker(el, pos, data):
            nonlocal ridx
            if pos == 0:
                out.append(P(
                    P(el.r).f(hsl(_view_rs1[ridx], 1)).alpha(0.1) if fill else None,
                    P(el.r.inset(0)).fssw(-1, bw(0, 0.2), 1) if stroke else None,
                    P().text(el.tag() or ("u:" + data["utag"])
                        , Style("Monaco", fontSize, load_font=0, fill=bw(0, 0.5))
                        , el.r.inset(7, 10)) if not vectors else
                            StSt(el.tag(), Font.JBMono(), fontSize)
                                .scaleToRect(el.r, shrink_only=True)
                                .align(el.r.inset(2), "SW")))
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