import math
from fontTools.misc.transform import Transform
from coldtype.geometry.geometrical import Geometrical
from coldtype.geometry.point import Point
from coldtype.geometry.primitives import line_intersection, calc_angle, polar_coord
from coldtype.interpolation import norm


class Line(Geometrical):
    def __init__(self, start, end):
        self.start = Point(start)
        self.end = Point(end)
    
    def __eq__(self, l):
        if not hasattr(l, "start"):
            return False
        return self.start == l.start and self.end == l.end

    __hash__ = object.__hash__

    def point(self, p):
        if p == "N":
            return self.pn
        elif p == "E":
            return self.pe
        elif p == "S":
            return self.ps
        elif p == "W":
            return self.pw
        elif p == "C":
            return self.mid
    
    @property
    def mid(self):
        return self.start.i(0.5, self.end)
    
    @property
    def mxx(self):
        return max([p.x for p in self.pts()])
    
    @property
    def mnx(self):
        return min([p.x for p in self.pts()])
    
    @property
    def mxy(self):
        return max([p.y for p in self.pts()])
    
    @property
    def mny(self):
        return min([p.y for p in self.pts()])
    
    @property
    def pe(self):
        return max(self.pts(), key=lambda p: p.x)
    
    @property
    def pw(self):
        return min(self.pts(), key=lambda p: p.x)
    
    @property
    def pn(self):
        return max(self.pts(), key=lambda p: p.y)
    
    @property
    def ps(self):
        return min(self.pts(), key=lambda p: p.y)
    
    def __repr__(self):
        return f"Line({self.start}, {self.end})"
    
    def __len__(self):
        return 2
    
    def __getitem__(self, idx):
        if idx == 0:
            return self.start
        elif idx == 1:
            return self.end
        else:
            raise IndexError("Line only has two points")

    def reverse(self):
        p1, p2 = self
        return Line(p2, p1)
    
    def __invert__(self):
        return self.reverse()

    def t(self, t):
        return self.start.interp(t, self.end)
    
    def length(self):
        a2 = math.pow(self.start.x - self.end.x, 2)
        b2 = math.pow(self.start.y - self.end.y, 2)
        return math.sqrt(a2 + b2)
    
    @property
    def l(self):
        return self.length()
    
    def tpx(self, tpx, limit=True):
        x = tpx * math.cos(self.angle())
        y = tpx * math.sin(self.angle())
        tp = self.start.offset(x, y)
        if not limit:
            return tp
        else:
            if Line(self.start, tp).length() > self.length():
                return self.end
            else:
                return tp

    def angle(self):
        return calc_angle(self.start, self.end)
    
    @property
    def ang(self):
        return self.angle()%math.pi
    
    def pts(self):
        return [self.start, self.end]
    
    def splat(self):
        return [(self.start.x, self.start.y), (self.end.x, self.end.y)]
    
    def transform(self, t):
        pts = self.pts()
        x1, x2 = [t.transformPoint(pt) for pt in pts]
        return Line(x1, x2)

    def rotate(self, degrees, point=None):
        if Transform:
            t = Transform()
            if not point:
                point = self.mid
            t = t.translate(point.x, point.y)
            t = t.rotate(math.radians(degrees))
            t = t.translate(-point.x, -point.y)
            return self.transform(t)
        else:
            raise Exception("fontTools not installed")
    
    def bow(self, amt, t=0.5, angle=90):
        rotated = self.rotate(angle, point=self.t(t))
        return rotated.tpx(self.length()*0.5+amt)
    
    def project(self, pt, dist, angle=90):
        dx, dy = polar_coord((0, 0), self.ang+math.radians(angle), dist)
        return self.t(pt).offset(dx, dy)
    
    def inset(self, px):
        return Line(self.tpx(px), self.reverse().tpx(px))
    
    inset_y = inset
    inset_x = inset
    
    def extr(self, amt):
        p1, p2 = self
        return Line(p2.i(1+amt, p1), p1.i(1+amt, p2))
    
    def offset(self, x, y):
        p1, p2 = self
        return Line(p1.offset(x, y), p2.offset(x, y))
    
    def offset_x(self, dx):
        return self.offset(dx, 0)
    
    def offset_y(self, dy):
        return self.offset(0, dy)
    
    def tan_out(self):
        return self
    
    def tan_in(self):
        return self
    
    o = offset
    
    def __floordiv__(self, other):
        return self.offset(0, other)
    
    def __truediv__(self, other):
        return self.offset(other, 0)
    
    def __mod__(self, other):
        return self.offset(*other)
    
    def intersection(self, other):
        return Point(line_intersection(self, other))
    
    sect = intersection
    
    def __and__(self, other):
        return self.intersection(other)
    
    def join(self, other):
        from coldtype.geometry.rect import Rect
        return Rect.FromPoints(self.start, self.end, other.end, other.start)
    
    def interp(self, x, other):
        return Line(self.start.i(x, other.start), self.end.i(x, other.end))

    i = interp

    def setx(self, x):
        return Line(self.start.setx(x), self.end.setx(x))
    
    def __mul__(self, other):
        return self.setx(other)
    
    def sety(self, y):
        return Line(self.start.sety(y), self.end.sety(y))
    
    def __matmul__(self, other):
        return self.sety(other)