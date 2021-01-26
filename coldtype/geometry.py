from fontTools.misc.arrayTools import unionRect
from fontTools.misc.transform import Transform
from coldtype.interpolation import norm
from functools import partialmethod
from enum import Enum
import math, re

YOYO = "ma"

MINYISMAXY = False


COMMON_PAPER_SIZES = {
    'letter': (612, 792),
    'tabloid': (792, 1224),
    'ledger': (1224, 792),
    'legal': (612, 1008),
    'a0': (2384, 3371),
    'a1': (1685, 2384),
    'a2': (1190, 1684),
    'a3': (842, 1190),
    'a4': (595, 842),
    'a4Small': (595, 842),
    'a5': (420, 595),
    'b4': (729, 1032),
    'b5': (516, 729),
    'folio': (612, 936),
    'quarto': (610, 780),
    '10x14': (720, 1008),
}

for key, (w, h) in list(COMMON_PAPER_SIZES.items()):
    COMMON_PAPER_SIZES["%s-landscape" % key] = (h, w)


class Edge(Enum):
    MaxY = 1
    MaxX = 2
    MinY = 3
    MinX = 4
    CenterY = 5
    CenterX = 6


def txt_to_edge(txt):
    if isinstance(txt, str):
        txt = txt.lower()
        if txt in ["maxy", "mxy", "n"]:
            return Edge.MaxY
        elif txt in ["maxx", "mxx", "e"]:
            return Edge.MaxX
        elif txt in ["miny", "mny", "s"]:
            return Edge.MinY
        elif txt in ["minx", "mnx", "w"]:
            return Edge.MinX
        elif txt in ["centery", "cy", "midy", "mdy"]:
            return Edge.CenterY
        elif txt in ["centerx", "cx", "midx", "mdx"]:
            return Edge.CenterX
        else:
            return None
    else:
        return txt

#https://stackoverflow.com/questions/20677795/how-do-i-compute-the-intersection-point-of-two-lines

def line_intersection(line1, line2):
    xdiff = (line1[0][0] - line1[1][0], line2[0][0] - line2[1][0])
    ydiff = (line1[0][1] - line1[1][1], line2[0][1] - line2[1][1])

    def det(a, b):
        return a[0] * b[1] - a[1] * b[0]

    div = det(xdiff, ydiff)
    if div == 0:
        raise Exception('lines do not intersect')

    d = (det(*line1), det(*line2))
    x = det(d, xdiff) / div
    y = det(d, ydiff) / div
    return x, y

def calc_vector(point1, point2):
    x1, y1 = point1
    x2, y2 = point2
    dx = x2 - x1
    dy = y2 - y1
    return dx, dy


def calc_angle(point1, point2):
    dx, dy = calc_vector(point1, point2)
    return math.atan2(dy, dx)


def polar_coord(xy, angle, distance):
    x, y = xy
    nx = x + (distance * math.cos(angle))
    ny = y + (distance * math.sin(angle))
    return nx, ny


def centered_square(rect):
    x, y, w, h = rect
    if w > h:
        return [x + (w - h) / 2, y, h, h]
    else:
        return [x, y + (h - w) / 2, w, w]


def perc_to_pix(rect, amount, edge):
    """
    perc(entage) to pix(els) — where the percentage is a decimal between 0 and 1 — cannot be 0 or 1
    """
    x, y, w, h = rect
    if amount <= 1.0:
        d = h if edge == Edge.MinY or edge == Edge.MaxY or edge == Edge.CenterY else w
        if amount < 0:
            return d + amount
        else:
            return d * amount  # math.floor
    else:
        return amount


def divide(rect, amount, edge, forcePixel=False):
    x, y, w, h = rect
    if not forcePixel:
        amount = perc_to_pix(rect, amount, edge)

    if edge == Edge.MaxY:
        if MINYISMAXY:
            return [x, y, w, amount], [x, y + amount, w, h - amount]
        else:
            return [x, y + h - amount, w, amount], [x, y, w, h - amount]
    elif edge == Edge.MinY:
        if MINYISMAXY:
            return [x, y + h - amount, w, amount], [x, y, w, h - amount]
        else:
            return [x, y, w, amount], [x, y + amount, w, h - amount]
    elif edge == Edge.MinX:
        return [x, y, amount, h], [x + amount, y, w - amount, h]
    elif edge == Edge.MaxX:
        return [x + w - amount, y, amount, h], [x, y, w - amount, h]
    elif edge == Edge.CenterX:
        lw = (w - amount) / 2
        return [x, y, lw, h], [x + lw, y, amount, h], [x + lw + amount, y, lw, h]
    elif edge == Edge.CenterY:
        lh = (h - amount) / 2
        return [x, y, w, lh], [x, y + lh, w, amount], [x, y + lh + amount, w, lh]


def subdivide(rect, count, edge, forcePixel=False):
    r = rect
    subs = []
    if hasattr(count, "__iter__"):
        amounts = count
        i = len(amounts) + 1
        a = 0
        while i > 1:
            s, r = divide(r, amounts[a], edge, forcePixel=forcePixel)
            subs.append(s)
            i -= 1
            a += 1
        subs.append(r)
        return subs
    else:
        i = count
        while i > 1:
            s, r = divide(r, 1/i, edge, forcePixel=forcePixel)
            subs.append(s)
            i -= 1
        subs.append(r)
        return subs


def pieces(rect, amount, edge):
    x, y, w, h = rect
    d = w
    if edge == Edge.MaxX or edge == Edge.MaxY:
        d = h
    fit = math.floor(d / amount)
    return subdivide(rect, fit, edge)


def take(rect, amount, edge, forcePixel=False):
    if edge == Edge.CenterX or edge == Edge.CenterY:
        _, r, _ = divide(rect, amount, edge, forcePixel=forcePixel)
        return r
    else:
        r, _ = divide(rect, amount, edge, forcePixel=forcePixel)
        return r


def subtract(rect, amount, edge):
    _, r = divide(rect, amount, edge)
    return r


def drop(rect, amount, edge):
    return subtract(rect, amount, edge)


def inset(rect, dx, dy):
    x, y, w, h = rect
    return [x + dx, y + dy, w - (dx * 2), h - (dy * 2)]


def offset(rect, dx, dy):
    x, y, w, h = rect
    if MINYISMAXY:
        return [x + dx, y - dy, w, h]
    else:
        return [x + dx, y + dy, w, h]


def expand(rect, amount, edge):
    x, y, w, h = rect
    if edge == Edge.MinX:
        w += amount
        x -= amount
    elif edge == Edge.MaxX:
        w += amount
    elif edge == Edge.MinY:
        y -= amount
        h += amount
    elif edge == Edge.MaxY:
        h += amount
    return [x, y, w, h]


def centerpoint(rect):
    x, y, w, h = rect
    return [x + w/2, y + h/2]


def add(rect_a, rect_b):
    # TODO better/correct implementation!
    ax, ay, aw, ah = rect_a
    bx, by, bw, bh = rect_b
    return [
        min(ax, bx),
        min(ay, by),
        aw + bw,
        ah
    ]


def scale(rect, s, x_edge=Edge.CenterX, y_edge=Edge.CenterY):
    """
    Only a partial implementation atm
    """
    x, y, w, h = rect
    return [x * s, y * s, w * s, h * s]


def edgepoints(rect, edge):
    x, y, w, h = rect
    if edge == Edge.MaxY:
        if MINYISMAXY:
            return (x, y), (x + w, y)
        else:
            return (x, y + h), (x + w, y + h)
    elif edge == Edge.MinY:
        if MINYISMAXY:
            return (x, y + h), (x + w, y + h)
        else:
            return (x, y), (x + w, y)
    elif edge == Edge.MinX:
        return (x, y), (x, y + h)
    elif edge == Edge.MaxX:
        return (x + w, y), (x + w, y + h)
    elif edge == Edge.CenterX:
        return (x + w/2, y), (x + w/2, y + h)
    elif edge == Edge.CenterY:
        return (x, y + h/2), (x + w, y + h/2)


class Point():
    """Representation of a point (x,y), indexable"""
    def __init__(self, point):
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
    
    o = offset

    def rect(self, w, h):
        "Create a rect from this point as center, with w and h dimensions provided"
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
    
    def interp(self, v, other):
        """Interpolate with another point"""
        sx, sy = self
        ox, oy = other
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
        return "<Point" + str(self.xy()) + ">"

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
    
    def as3d(self):
        return Point3D(self)


class Point3D(Point):
    def __init__(self, p):
        super().__init__(p)
        self.z = 0
    
    def __len__(self):
        return 3
    
    def __getitem__(self, idx):
        if idx == 2:
            return self.z
        return super().__getitem__(idx)


class Line():
    def __init__(self, start, end):
        self.start = Point(start)
        self.end = Point(end)
    
    def __repr__(self):
        return f"<Line:{self.start}/{self.end}>"
    
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
    
    def tpx(self, tpx):
        print("angle>", self.angle())
        pass

    def angle(self):
        return calc_angle(self.start, self.end)
    
    def extr(self, amt):
        p1, p2 = self
        return Line(p2.i(1+amt, p1), p1.i(1+amt, p2))
    
    def offset(self, x, y):
        p1, p2 = self
        return Line(p1.offset(x, y), p2.offset(x, y))
    
    def __floordiv__(self, other):
        return self.offset(0, other)
    
    def __truediv__(self, other):
        return self.offset(other, 0)
    
    def __mod__(self, other):
        return self.offset(*other)
    
    def intersection(self, other):
        return Point(line_intersection(self, other))
    
    def __and__(self, other):
        return self.intersection(other)


class Rect():
    """
    Representation of a rectangle as (x, y, w, h), indexable
    
    Constructor handles multiple formats, including:
    
    * ``x, y, w, h``
    * ``[x, y, w, h]``
    * ``w, h`` (x and y default to 0, 0)

    ``Rect`` objects can be splat'd where lists are expected as individual arguments (as in drawBot), i.e. ``rect(*my_rect)``, or can be passed directly to functions expected a list representation of a rectangle.
    """

    def FromCenter(center, w, h=None):
        """Create a rect given a center point and a width and height (optional, height will default to width if not specified")"""
        x, y = center
        if not h:
            h = w
        return Rect((x - w/2, y - h/2, w, h))
    
    def Inches(w, h, dpi=72.0):
        return Rect(w*dpi, h*dpi)

    def __init__(self, *rect):
        if isinstance(rect[0], str):
            x, y = 0, 0
            w, h = COMMON_PAPER_SIZES[rect[0].lower()]
        elif isinstance(rect[0], int) or isinstance(rect[0], float):
            try:
                x, y, w, h = rect
            except:
                w, h = rect
                x, y = 0, 0
        else:
            try:
                x, y, w, h = rect[0]
            except:
                w, h = rect[0]
                x, y = 0, 0
        self.x = x
        self.y = y
        self.w = w
        self.h = h
    
    def origin(self):
        """``(x, y)`` as tuple"""
        return self.x, self.y

    def from_obj(obj, w=None, h=None):
        r = Rect((0, 0, 0, 0))
        try:
            r.x = obj.x
            r.y = obj.y
        except:
            pass
        try:
            r.w = obj.w
            r.h = obj.h
        except:
            pass
        if w:
            r.w = w
            r.x -= w/2
        if h:
            r.h = h
            r.y -= h/2
        return r

    def FromExtents(extents):
        nw, ne, se, sw = extents
        return Rect(sw[0], sw[1], abs(ne[0] - sw[0]), abs(ne[1] - sw[1]))
    
    def noop(self, *args, **kwargs):
        return self

    def FromMnMnMxMx(extents):
        """Create a rectangle from ``xmin, ymin, xmax, ymax``"""
        xmin, ymin, xmax, ymax = extents
        return Rect(xmin, ymin, xmax - xmin, ymax - ymin)

    def FromPoints(*points):
        xmin, ymin, xmax, ymax = None, None, None, None
        for p in points:
            if xmin is None or p[0] < xmin:
                xmin = p[0]
            if ymin is None or p[1] < ymin:
                ymin = p[1]
            if xmax is None or p[0] > xmax:
                xmax = p[0]
            if ymax is None or p[1] > ymax:
                ymax = p[1]
        return Rect.FromMnMnMxMx([xmin, ymin, xmax, ymax])

    def mnmnmxmx(self):
        """Return extents of rectangle as list"""
        return (self.x, self.y, self.x + self.w, self.y + self.h)

    def __getitem__(self, key):
        return self.rect()[key]

    def __repr__(self):
        return "Rect(" + str(self.rect()) + ")"
    
    def __eq__(self, r):
        try:
            return all([self.x == r.x, self.y == r.y, self.w == r.w, self.h == r.h])
        except:
            return False
    
    __hash__ = object.__hash__

    def rect(self):
        """x,y,w,h in list"""
        return [self.x, self.y, self.w, self.h]
    
    def round(self):
        """round the values in the rectangle to the nearest integer"""
        return Rect([int(round(n)) for n in self])

    def xy(self):
        """equivalent to origin"""
        return [self.x, self.y]

    def wh(self):
        """the width and height as a tuple"""
        return [self.w, self.h]
    
    @property
    def mnx(self):
        return self.x
    
    @property
    def mny(self):
        return self.y

    @property
    def mxx(self):
        return self.x + self.w
    
    @property
    def mxy(self):
        return self.y + self.h

    def square(self):
        """take a square from the center of this rect"""
        return Rect(centered_square(self.rect()))
    
    def align(self, rect, x=Edge.CenterX, y=Edge.CenterY):
        x = txt_to_edge(x)
        y = txt_to_edge(y)
        b = self
        
        xoff = 0
        if x != None:
            if x == Edge.CenterX:
                xoff = -b.x + rect.x + rect.w/2 - b.w/2
            elif x == Edge.MinX:
                xoff = -(b.x-rect.x)
            elif x == Edge.MaxX:
                xoff = -b.x + rect.x + rect.w - b.w
        
        yoff = 0
        if y != None:
            if y == Edge.CenterY:
                yoff = -b.y + rect.y + rect.h/2 - b.h/2
            elif y == Edge.MaxY:
                yoff = (rect.y + rect.h) - (b.h + b.y)
            elif y == Edge.MinY:
                yoff = -(b.y-rect.y)
        
        diff = rect.w - b.w
        return self.offset(xoff, yoff)
    
    def ipos(self, pt, defaults=(0.5, 0.5), clamp=True):
        """
        Get scaled 0-1 bounded (optional) value
        from a point in a rectangle
        """
        if not pt:
            return defaults
        sx = ((pt.x - self.x) / self.w)
        sy = ((pt.y - self.y) / self.h)
        if clamp:
            sx = min(1, max(0, sx))
            sy = min(1, max(0, sy))
        return sx, sy

    def divide(self, amount, edge, forcePixel=False):
        """
        **Dividing**

        Derived from the behavior of the classic Cocoa function CGRectDivide, which takes a rectangle and breaks it into two pieces, based on a pixel amount and an edge.

        A quick example: assume you have a rectangle, ``r``, defined as such:

        ``r = Rect(0, 0, 300, 100)``
        
        If you want to break that into a left-hand rectangle that’s 100 pixels wide and a right-hand rectangle that’s 200 pixels wide, you could either say:
        
        ``left, right = r.divide(100, "mnx")``
        
        `or you could say`
        
        ``right, left = r.divide(200, "mxx")``

        where ``mxx`` is the rightmost edge, and ``mnx`` is the leftmost edge.

        **Centering**

        A special use-case is if you want to break a rectangle into `three` rectangles, based on the center "edge", you can do something like this:

        ``left, center, right = r.divide(200, "mdx")``

        This will result in three rectangles, always left-to-right, where
        left is 50px wide, then center is 200px wide, then right is also 50px wide — anything not in the center will be evenly distributed between left and right, or top-and-bottom in the case of a Y edge.
        """
        edge = txt_to_edge(edge)
        if edge == Edge.CenterX or edge == Edge.CenterY:
            a, b, c = divide(self.rect(), amount, edge, forcePixel=forcePixel)
            return Rect(a), Rect(b), Rect(c)
        else:
            a, b = divide(self.rect(), amount, edge, forcePixel=forcePixel)
            return Rect(a), Rect(b)

    def subdivide(self, amount, edge):
        """
        Like ``divide``, but here you specify the number of equal pieces you want (like columns or rows), and then what edge to start at, i.e.
        
        .. code:: python
            
            r = Rect(0, 0, 500, 100)
            r.subdivide(5, "mxx")
            => [Rect([400.0, 0, 100.0, 100]), Rect([300.0, 0, 100.0, 100]), Rect([200.0, 0, 100.0, 100]), Rect([100.0, 0, 100.0, 100]), Rect([0, 0, 100.0, 100])]
        
        will get you five 100-px wide rectangles, right-to-left

        (N.B. Does not support center edges, as that makes no sense)
        """
        edge = txt_to_edge(edge)
        return [Rect(x) for x in subdivide(self.rect(), amount, edge)]
    
    def subdivide_with_leading(self, count, leading, edge, forcePixel=True):
        """
        Same as `subdivide`, but inserts leading between each subdivision
        """
        return self.subdivide_with_leadings(count, [leading]*(count-1), edge, forcePixel)

    def subdivide_with_leadings(self, count, leadings, edge, forcePixel=True):
        """
        Same as `subdivide_with_leadings`, but inserts leading between each subdivision, indexing the size of the leading from a list of leadings
        """
        edge = txt_to_edge(edge)
        leadings = leadings + [0]
        full = self.w if edge == Edge.MinX or edge == Edge.MaxX else self.h
        unit = (full - sum(leadings)) / count
        amounts = [val for pair in zip([unit] * count, leadings) for val in pair][:-1]
        return [Rect(x) for x in subdivide(self.rect(), amounts, edge, forcePixel=forcePixel)][::2]

    def transform(self, t):
        pts = ["NW", "NE", "SE", "SW"]
        x1, x2, x3, x4 = [t.transformPoint(self.point(pt)) for pt in pts]
        return Rect.FromExtents([x1, x2, x3, x4])

    def rotate(self, degrees, point=None):
        t = Transform()
        if not point:
            point = self.point("C")
        t = t.translate(point.x, point.y)
        t = t.rotate(math.radians(degrees))
        t = t.translate(-point.x, -point.y)
        return self.transform(t)

    def scale(self, s, x_edge=Edge.MinX, y_edge=Edge.MinY):
        return Rect(scale(self.rect(), s, x_edge, y_edge))
        #x_edge = txt_to_edge(x_edge)
        #y_edge = txt_to_edge(y_edge)
        #sx = self.w * s
        #sy = self.h * s
        #return self.take(sx, x_edge, forcePixel=True).take(sy, y_edge, forcePixel=True)

    def union(self, otherRect):
        return Rect.FromMnMnMxMx(unionRect(self.mnmnmxmx(), otherRect.mnmnmxmx()))

    def take(self, amount, edge, forcePixel=False):
        """
        Like `divide`, but here it just returns the "first" rect from a divide call, not all the resulting pieces, i.e. you can "take" 200px from the center of a rectangle by doing this ``Rect(0, 0, 300, 100).take(200, "mdx")`` which will result in ``Rect([50, 0, 200, 100])``
        """
        edge = txt_to_edge(edge)
        return Rect(take(self.rect(), amount, edge, forcePixel=forcePixel))

    def takeOpposite(self, amount, edge, forcePixel=False):
        edge = txt_to_edge(edge)
        return self.divide(amount, edge, forcePixel=forcePixel)[1]

    def subtract(self, amount, edge):
        """
        The opposite of ``take``, this will remove and not return a piece of the given amount from the given edge.
        
        Let's say you have a 100px-wide square and you want to drop 10px from the right-hand side, you would do:

        ``Rect(100, 100).subtract(10, Edge.MaxX)``, which leaves you with ``Rect([0, 0, 90, 100])``
        """
        edge = txt_to_edge(edge)
        return Rect(subtract(self.rect(), amount, edge))

    def expand(self, amount, edge):
        edges = None
        if edge == "NW":
            edges = ["mxy", "mnx"]
        elif edge == "NE":
            edges = ["mxy", "mxx"]
        elif edge == "SE":
            edges = ["mny", "mxx"]
        elif edge == "SW":
            edges = ["mny", "mnx"]
        
        if edges:
            return self.expand(amount, edges[0]).expand(amount, edges[1])
        edge = txt_to_edge(edge)
        return Rect(expand(self.rect(), amount, edge))
    
    add = expand

    def inset(self, dx, dy=None):
        """
        Creates padding in the amount of dx and dy. Also does expansion with negative values, or both at once
        """
        if dy == None:
            dy = dx
        return Rect(inset(self.rect(), dx, dy))

    def offset(self, dx, dy=None):
        if dy == None:
            dy = dx
        return Rect(offset(self.rect(), dx, dy))

    def zero(self):
        return Rect((0, 0, self.w, self.h))

    def __add__(self, another_rect):
        return Rect(add(self, another_rect))

    def grid(self, rows=2, columns=2):
        """Construct a grid"""
        xs = [row.subdivide(columns, Edge.MinX) for row in self.subdivide(rows, Edge.MaxY)]
        return [item for sublist in xs for item in sublist]

    def pieces(self, amount, edge):
        edge = txt_to_edge(edge)
        return [Rect(x) for x in pieces(self.rect(), amount, edge)]

    def edge(self, edge):
        edge = txt_to_edge(edge)
        return Line(*edgepoints(self.rect(), edge))

    def center(self):
        return Point(centerpoint(self.rect()))

    def flip(self, h):
        return Rect([self.x, h - self.h - self.y, self.w, self.h])

    def cardinals(self):
        return self.point("N"), self.point("E"), self.point("S"), self.point("W")

    def intercardinals(self):
        return self.point("NE"), self.point("SE"), self.point("SW"), self.point("NW")
    
    def aspect(self):
        return self.h / self.w
    
    def fit(self, other):
        sx, sy, sw, sh = self
        ox, oy, ow, oh = other
        if ow > oh:
            fw = sw
            fh = sw * other.aspect()
        else:
            fh = sh
            sw = sh * 1/other.aspect()
        #print(sh, fw, fh, other.aspect())
        return self.take(fh, "mdy")

    def point(self, eh, ev=Edge.MinX):
        """
        Get a ``Point`` at a given compass direction, chosen from
        
        * C
        * W
        * NW
        * N
        * NE
        * E
        * SE
        * S
        * SW
        """
        ev = txt_to_edge(ev)
        if eh == "C":
            return self.point(Edge.CenterX, Edge.CenterY)
        elif eh == "W":
            return self.point(Edge.MinX, Edge.CenterY)
        elif eh == "NW":
            return self.point(Edge.MinX, Edge.MaxY)
        elif eh == "N":
            return self.point(Edge.CenterX, Edge.MaxY)
        elif eh == "NE":
            return self.point(Edge.MaxX, Edge.MaxY)
        elif eh == "E":
            return self.point(Edge.MaxX, Edge.CenterY)
        elif eh == "SE":
            return self.point(Edge.MaxX, Edge.MinY)
        elif eh == "S":
            return self.point(Edge.CenterX, Edge.MinY)
        elif eh == "SW":
            return self.point(Edge.MinX, Edge.MinY)
        else:
            px = self.x
            py = self.y

            if eh == Edge.MaxX:
                px = self.x + self.w
            elif eh == Edge.CenterX:
                px = self.x + self.w/2

            if ev == Edge.MaxY:
                py = self.y + self.h
            if ev == Edge.CenterY:
                py = self.y + self.h/2

            return Point((px, py))
    
    p = point

    @property
    def pne(self): return self.point("NE")

    @property
    def pe(self): return self.point("E")

    @property
    def ee(self): return self.edge("mxx")

    @property
    def pse(self): return self.point("SE")

    @property
    def ps(self): return self.point("S")

    @property
    def es(self): return self.edge("mny")

    @property
    def psw(self): return self.point("SW")

    @property
    def pw(self): return self.point("W")

    @property
    def ew(self): return self.edge("mnx")

    @property
    def pnw(self): return self.point("NW")

    @property
    def pn(self): return self.point("N")

    @property
    def en(self): return self.edge("mxy")

    @property
    def pc(self): return self.point("C")

    @property
    def ecx(self): return self.edge("mdx")

    @property
    def ecy(self): return self.edge("mdy")

    def intersects(self, other):
        return not (self.point("NE").x < other.point("SW").x or self.point("SW").x > other.point("NE").x or self.point("NE").y < other.point("SW").y or self.point("SW").y > other.point("NE").y)
    
    def setmnx(self, x):
        mnx, mny, mxx, mxy = self.mnmnmxmx()
        return Rect.FromMnMnMxMx([x, mny, mxx, mxy])
    
    def __mul__(self, other):
        return self.setmnx(other)
    
    def setlmnx(self, x):
        if x > self.mnx:
            return self.setmnx(x)
        return self
    
    def setmny(self, y):
        mnx, mny, mxx, mxy = self.mnmnmxmx()
        return Rect.FromMnMnMxMx([mnx, y, mxx, mxy])
    
    def __matmul__(self, other):
        return self.setmny(other)
    
    def setlmny(self, y):
        if y > self.mny:
            return self.setmny(y)
        return self
    
    def setmxx(self, x):
        mnx, mny, mxx, mxy = self.mnmnmxmx()
        return Rect.FromMnMnMxMx([mnx, mny, x, mxy])
    
    def setlmxx(self, x):
        if x < self.mxx:
            return self.setmxx(x)
        return self
    
    def setmxy(self, y):
        mnx, mny, mxx, mxy = self.mnmnmxmx()
        return Rect.FromMnMnMxMx([mnx, mny, mxx, y])
    
    def setlmxy(self, y):
        if y < self.mxy:
            return self.setmxy(y)
        return self
    
    def setmdx(self, x):
        c = self.point("C")
        return Rect.FromCenter(Point([x, c.y]), self.w, self.h)
    
    def setmn(self, mn):
        return self.setmnx(mn.x).setmny(mn.y)

    def setmx(self, mx):
        return self.setmxx(mx.x).setmxy(mx.y)
    
    def setw(self, w):
        return Rect(self.x, self.y, w, self.h)
    
    def seth(self, h):
        return Rect(self.x, self.y, self.w, h)
    
    def parse_line(self, d, line):
        parts = re.split(r"\s", line)
        reified = []
        for p in parts:
            if p == "auto" or p == "a":
                reified.append("auto")
            elif "%" in p:
                reified.append(float(p.replace("%", ""))/100 * d)
            else:
                fp = float(p)
                if fp > 1:
                    reified.append(fp)
                else:
                    reified.append(fp*d)
        remaining = d - sum([0 if r == "auto" else r for r in reified])
        #if not float(remaining).is_integer():
        #    raise Exception("floating parse")
        auto_count = reified.count("auto")
        auto_d = remaining / auto_count
        auto_ds = [auto_d] * auto_count
        if not auto_d.is_integer():
            auto_d_floor = math.floor(auto_d)
            leftover = remaining - auto_d_floor * auto_count
            for aidx, ad in enumerate(auto_ds):
                if leftover > 0:
                    auto_ds[aidx] = auto_d_floor + 1
                    leftover -= 1
                else:
                    auto_ds[aidx] = auto_d_floor
            #print(auto_ds)
            #print("NO", auto_d - int(auto_d))
        res = []
        for r in reified:
            if r == "auto":
                res.append(auto_ds.pop())
            else:
                res.append(r)
        return res
        #return [auto_d if r == "auto" else r for r in reified]
    
    def __floordiv__(self, other):
        return self.offset(0, other)
    
    def __truediv__(self, other):
        return self.offset(other, 0)
    
    def __mod__(self, s):
        sfx = ["x", "y"]

        def do_op(r, xs):
            op = xs[0]
            if op in ["t", "i", "o", "s", "m", "c", "r", "a", "l", "@", "e"]:
                op = op
                xs = xs[1:].strip()
            else:
                op = "t"
                xs = xs.strip()
            
            _xs = xs
            xs = re.split(r"\s", xs)
            edges = []
            amounts = []
            
            for idx, x in enumerate(xs):
                if op in ["t", "s", "m", "l", "e"]:
                    if x[0] == "-":
                        edges.append("mn" + sfx[idx])
                    elif x[0] == "+":
                        edges.append("mx" + sfx[idx])
                    elif x[0] == "=":
                        edges.append("md" + sfx[idx])
                    elif x[0] == "1":
                        edges.append("mn" + sfx[idx])
                        amounts.append(1)
                        continue
                    elif x[0] == "0":
                        edges.append("mn" + sfx[idx])
                        amounts.append(0)
                        continue
                    elif x[0] == "ø":
                        edges.append(None)
                        amounts.append("ø")
                        continue
                    amounts.append(float(x[1:]))
                else:
                    if x == "auto" or x == "a":
                        continue
                    elif "%" in x:
                        continue
                    else:
                        amounts.append(float(x))

            if op == "t": # take
                return (r
                    .take(amounts[0], edges[0])
                    .take(amounts[1], edges[1]))
            elif op == "s": # subtract
                return (r
                    .subtract(amounts[0], edges[0])
                    .subtract(amounts[1], edges[1]))
            elif op == "e": # subtract
                return (r
                    .expand(amounts[0], edges[0])
                    .expand(amounts[1], edges[1]))
            elif op == "i": # inset
                return (r.inset(amounts[0], amounts[1]))
            elif op == "o": # offset
                return (r.offset(amounts[0], amounts[1]))
            elif op == "l": # limits
                # TODO simplify with setlmx* series
                if amounts[0] != "ø":
                    x = amounts[0]
                    if edges[0] == "mnx":
                        if x > r.mnx:
                            r = r.setmnx(x)
                    elif edges[0] == "mxx":
                        if x < r.mxx:
                            r = r.setmxx(x)
                elif amounts[1] != "ø":
                    y = amounts[1]
                    if edges[1] == "mny":
                        if y > r.mny:
                            r = r.setmny(y)
                    elif edges[1] == "mxy":
                        if y < r.mxy:
                            r = r.setmxy(y)
                return r
            elif op == "m": # maxima
                if amounts[0] != "ø":
                    if edges[0] == "mnx":
                        r = r.setmnx(amounts[0])
                    elif edges[0] == "mxx":
                        r = r.setmxx(amounts[0])
                    elif edges[0] == "mdx":
                        r = r.setmdx(amounts[0])
                if amounts[1] != "ø":
                    if edges[1] == "mny":
                        r = r.setmny(amounts[1])
                    elif edges[1] == "mxy":
                        r = r.setmxy(amounts[1])
                    elif edges[1] == "mdy":
                        r = r.setmdy(amounts[1])
                return r
            elif op == "c": # columns
                ws = self.parse_line(r.w, _xs)
                rs = []
                for w in ws:
                    _r, r = r.divide(w, "mnx")
                    rs.append(_r)
                return rs
            elif op == "r": # rows
                ws = self.parse_line(r.h, _xs)
                rs = []
                for w in ws:
                    _r, r = r.divide(w, "mny")
                    rs.append(_r)
                return rs
            elif op == "@": # get-at-index
                return r[int(amounts[0])]
            else:
                raise Exception("op", op, "not supported")

        ys = s.split("^")
        r = self
        for y in ys:
            if y.startswith("Rect("):
                r = eval(y.strip())
            else:
                try:
                    r = do_op(r, y.strip())
                except IndexError:
                    print("FAILED")
        return r