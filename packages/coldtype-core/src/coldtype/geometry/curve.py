from coldtype.geometry.line import Line
from coldtype.geometry.point import Point
from fontTools.misc.bezierTools import calcCubicArcLength, splitCubicAtT

class Curve(Line):
    def __init__(self, start, cp1, cp2, end):
        self.cp1 = cp1
        self.cp2 = cp2
        super().__init__(start, end)
    
    @property
    def abcd(self):
        return [self.start, self.cp1, self.cp2, self.end]
    
    def pts(self):
        return self.abcd
    
    def split_t(self, t):
        l1, l2 = splitCubicAtT(*self.abcd, t)
        return Curve(*l1), Curve(*l2)
    
    def t(self, t):
        l1, l2 = self.split_t(t)
        return Point(*l2.start)
    
    def length(self):
        return calcCubicArcLength(*self.abcd)
    
    def split_tpx(self, tpx):
        return self.split_t(tpx/self.length())

    def tpx(self, tpx, limit=True):
        return self.t(tpx/self.length())

    def __eq__(self, l):
        if not hasattr(l, "start") or not hasattr(l, "cp1"):
            return False
        return self.start == l.start and self.end == l.end and self.cp1 == l.cp1 and self.cp2 == l.cp2
    
    def reverse(self):
        return Curve(*list(reversed(self.abcd)))
    
    def tan_out(self):
        return Line(self.cp2, self.end)
    
    def tan_in(self):
        return Line(self.start, self.cp1)
    
    def inset(self, px):
        inset_start = self.split_tpx(px)[1]
        return inset_start.reverse().split_tpx(px)[1].reverse()
    
    def __repr__(self):
        pts = ','.join([str(p) for p in self.abcd])
        return f"Curve({pts})"
    
    def __len__(self):
        return 4
    
    def __getitem__(self, idx):
        if idx == 0:
            return self.start
        elif idx == 1:
            return self.cp1
        elif idx == 2:
            return self.cp2
        elif idx == 3:
            return self.end
        else:
            raise IndexError("Curve only has four points")