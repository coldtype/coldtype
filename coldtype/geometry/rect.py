import math, re

from coldtype.geometry.geometrical import Geometrical
from coldtype.geometry.point import Point
from coldtype.geometry.line import Line
from coldtype.geometry.edge import Edge, txt_to_edge
from coldtype.interpolation import norm
from coldtype.geometry.primitives import *

try:
    from fontTools.misc.transform import Transform
except ImportError:
    Transform = None


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


def align(b, rect, x=Edge.CenterX, y=Edge.CenterY):
    x = txt_to_edge(x)
    y = txt_to_edge(y)
    
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
    
    #diff = rect.w - b.w
    return (xoff, yoff)


class Rect(Geometrical):
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
        return "Rect(" + str(self.rect()).replace(" ", "") + ")"
    
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
    
    @property
    def mdx(self):
        return self.point("C").x
    
    @property
    def mdy(self):
        return self.point("C").y

    def square(self):
        """take a square from the center of this rect"""
        return Rect(centered_square(self.rect()))
    
    def align(self, rect, x=Edge.CenterX, y=Edge.CenterY):
        return self.offset(*align(self, rect, x, y))
    
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
        if Transform:
            t = Transform()
            if not point:
                point = self.point("C")
            t = t.translate(point.x, point.y)
            t = t.rotate(math.radians(degrees))
            t = t.translate(-point.x, -point.y)
            return self.transform(t)
        else:
            raise Exception("fontTools not installed")

    def scale(self, s, x_edge=Edge.MinX, y_edge=Edge.MinY):
        return Rect(scale(self.rect(), s, x_edge, y_edge))
        #x_edge = txt_to_edge(x_edge)
        #y_edge = txt_to_edge(y_edge)
        #sx = self.w * s
        #sy = self.h * s
        #return self.take(sx, x_edge, forcePixel=True).take(sy, y_edge, forcePixel=True)

    def union(self, otherRect):
        return Rect.FromMnMnMxMx(unionRect(self.mnmnmxmx(), otherRect.mnmnmxmx()))
    
    def intersection(self, otherRect):
        return Rect.FromMnMnMxMx(sectRect(self.mnmnmxmx(), otherRect.mnmnmxmx())[1])
    
    sect = intersection

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
    
    def inset_x(self, dx):
        return self.inset(dx, 0)
    
    def inset_y(self, dy):
        return self.inset(0, dy)

    def offset(self, dx, dy=None):
        if dy == None:
            dy = dx
        return Rect(offset(self.rect(), dx, dy))
    
    def offset_x(self, dx):
        return self.offset(dx, 0)
    
    def offset_y(self, dy):
        return self.offset(0, dy)
    
    o = offset

    def zero(self):
        return Rect((0, 0, self.w, self.h))

    def __add__(self, another_rect):
        return Rect(add(self, another_rect))

    def grid(self, columns=2, rows=2):
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
    
    def avg(self):
        pts = self.cardinals()
        return Point(
            sum([p.x for p in pts])/4,
            sum([p.y for p in pts])/4)

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
        pc = Edge.PairFromCompass(eh)
        if pc:
            return self.point(*pc)
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
    
    def maxima(self, n, edge):
        e = txt_to_edge(edge)
        if e == Edge.MinX:
            return self.setmnx(n)
        elif e == Edge.MaxX:
            return self.setmxx(n)
        elif e == Edge.CenterX:
            return self.setmdx(n)
        elif e == Edge.MinY:
            return self.setmny(n)
        elif e == Edge.MaxY:
            return self.setmxy(n)
        elif e == Edge.CenterY:
            return self.setmdy(n)
        else:
            raise Exception("HELLO")
    
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
        parts = re.split(r"\s|ƒ|,", line)
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
        if auto_count > 0:
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
    
    def symbol_to_edge(self, idx, symbol):
        d = ["x", "y"][idx]
        if symbol == "-":
            return "mn" + d
        elif symbol == "+":
            return "mx" + d
        elif symbol == "=":
            return "md" + d
    
    def sign_to_dim(self, sign):
        xy = "x"
        if isinstance(sign, complex):
            xy = "y"
            sign = sign.imag
        return xy, sign
    
    def sign_to_edge(self, sign):
        xy, sign = self.sign_to_dim(sign)
        if sign == 0:
            return "md" + xy
        elif sign < 0:
            return "mn" + xy
        else:
            return "mx" + xy
    
    def t(self, sign, n):
        return self.take(n, self.sign_to_edge(sign))
    
    def s(self, sign, n):
        return self.subtract(n, self.sign_to_edge(sign))
    
    def i(self, sign, n):
        xy, _ = self.sign_to_dim(sign)
        return self.inset(n if xy == "x" else 0, n if xy == "y" else 0)
    
    def columns(self, *args):
        r = self
        _xs = " ".join([str(s) for s in args])
        ws = self.parse_line(r.w, _xs)
        rs = []
        for w in ws:
            _r, r = r.divide(w, "mnx")
            rs.append(_r)
        return rs
    
    def rows(self, *args):
        r = self
        _xs = " ".join([str(s) for s in args])
        ws = self.parse_line(r.h, _xs)
        rs = []
        for w in ws:
            _r, r = r.divide(w, "mxy")
            rs.append(_r)
        return rs
    
    def to_pen(self):
        from coldtype.pens.draftingpen import DraftingPen
        return DraftingPen(self)