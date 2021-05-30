import math
from drafting.geometry.geometrical import Geometrical
from drafting.interpolation import norm
from drafting.geometry.primitives import polar_coord, line_intersection, calc_angle, calc_vector


class Point(Geometrical):
    """Representation of a point (x,y), indexable"""
    def __init__(self, *points):
        if len(points) == 2:
            self.x = points[0]
            self.y = points[1]
        else:
            point = points[0]
            try:
                x, y = point
                self.x = x
                self.y = y
            except:
                try:
                    self.x = point.x
                    self.y = point.y
                except:
                    self.x = 0
                    self.y = 0
    
    __hash__ = object.__hash__

    def Z():
        return Point([0, 0])

    def from_obj(obj):
        p = Point((0, 0))
        try:
            p.x = obj.x
            p.y = obj.y
        except:
            pass
        return p

    def offset(self, dx, dy):
        "Offset by dx, dy"
        return Point((self.x + dx, self.y + dy))
    
    def offset_x(self, dx):
        return self.offset(dx, 0)
    
    def offset_y(self, dy):
        return self.offset(0, dy)
    
    o = offset

    def rect(self, w, h):
        "Create a rect from this point as center, with w and h dimensions provided"
        from drafting.geometry.rect import Rect
        return Rect((self.x-w/2, self.y-h/2, w, h))

    def xy(self):
        "As a tuple"
        return self.x, self.y
    
    def round(self):
        """round the values in the point to the nearest integer"""
        return Point([int(round(n)) for n in self])
    
    def round_to(self, to=10):
        """round the values in the point to the nearest integer multiple"""
        return Point([int(round(n/to)*to) for n in self.xy()])
    
    def inside(self, rect):
        mnx, mny, mxx, mxy = rect.mnmnmxmx()
        if mnx <= self.x <= mxx and mny <= self.y <= mxy:
            return True
        else:
            return False

    def flip(self, frame):
        return Point((self.x, frame.h - self.y))

    def flipSelf(self, frame):
        x, y = self.flip(frame)
        self.x = x
        self.y = y
    
    def scale(self, x, y=None):
        if not y:
            y = x
        return Point((self.x * x, self.y * y))
    
    def join(self, other):
        from drafting.geometry.line import Line
        return Line(self, other)
    
    def interp(self, v, other):
        """Interpolate with another point"""
        sx, sy = self
        ox, oy = other
        if not isinstance(v, float) and v != 1:
            v = v/100
        return Point((norm(v, sx, ox), norm(v, sy, oy)))
    
    def i(self, *args):
        other = args
        if isinstance(other[0], Point):
            return self.interp(0.5, other[0])
        else:
            x, pt = other
            return self.interp(x, pt)
    
    def project(self, angle, dist):
        dx, dy = polar_coord((0, 0), math.radians(angle), dist)
        return self.offset(dx, dy)
    
    def project_to(self, angle, line):
        ray = [self, self.project(angle, 1000)]
        return Point(line_intersection(ray, line))
    
    def cdist(self, other):
        vec = calc_vector(self, other)
        ang = calc_angle(self, other)
        dist = math.sqrt(math.pow(vec[0], 2) + math.pow(vec[1], 2))
        return dist, math.degrees(ang)
    
    def noop(self, *args, **kwargs):
        return self
    
    def __eq__(self, o):
        try:
            return all([self.x == o.x, self.y == o.y])
        except:
            return False

    def __repr__(self):
        return "Point" + str(self.xy())

    def __getitem__(self, key):
        return self.xy()[key]
    
    def __len__(self):
        return 2

    def __setitem__(self, key, value):
        if key == 0:
            self.x = value
        elif key == 1:
            self.y = value
        else:
            raise IndexError(
                "Invalid index for point assignment, must be 0 or 1")
    
    def __floordiv__(self, other):
        return self.offset(0, other)
    
    def __truediv__(self, other):
        return self.offset(other, 0)
    
    def setx(self, x):
        return Point([x, self.y])
    
    def __mul__(self, other):
        return self.setx(other)
    
    def sety(self, y):
        return Point([self.x, y])
    
    def __matmul__(self, other):
        return self.sety(other)
    
    def __or__(self, other):
        from drafting.geometry.line import Line
        return Line(self, other)
    
    #def as3d(self):
    #    return Point3D(self)
    
    def reverse(self):
        return Point(self.y, self.x)


# class Point3D(Point):
#     def __init__(self, p):
#         super().__init__(p)
#         self.z = 0
    
#     def __len__(self):
#         return 3
    
#     def __getitem__(self, idx):
#         if idx == 2:
#             return self.z
#         return super().__getitem__(idx)