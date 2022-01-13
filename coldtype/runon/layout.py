from random import random

from coldtype.runon import Runon
from coldtype.geometry import Rect
from coldtype.grid import Grid
from coldtype.color import hsl, bw


class Layout(Runon):
    @property
    def rect(self) -> Rect:
        return self._val
    
    r = rect

    def divide(self, amt, edge, forcePixel=False):
        if self.val_present():
            a, b = self.r.divide(amt, edge, forcePixel)
            self.extend([a, b])
        return self
    
    def grid(self, cols, rows, ascii):
        if self.val_present():
            g = Grid(self.r, cols, rows, ascii)
            for k, v in g.keyed.items():
                self.append(Layout(v).tag(k))
        return self
    
    def view(self, fontSize=32):
        from coldtype.path import P
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