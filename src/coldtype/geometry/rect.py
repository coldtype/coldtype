import math, re, inspect

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

def pair_to_edges(x, y=None):
    if x == "NE":
        return Edge.MaxX, Edge.MaxY
    elif x == "NW":
        return Edge.MinX, Edge.MaxY
    elif x == "SW":
        return Edge.MinX, Edge.MinY
    elif x == "SE":
        return Edge.MaxX, Edge.MinY
    elif x == "N":
        return Edge.CenterX, Edge.MaxY
    elif x == "S":
        return Edge.CenterX, Edge.MinY
    elif x == "E":
        return Edge.MaxX, txt_to_edge(y)
    elif x == "W":
        return Edge.MinX, txt_to_edge(y)
    elif x == "C":
        return Edge.CenterX, Edge.CenterY
    
    if y is not None:
        return txt_to_edge(x), txt_to_edge(y)
    else:
        e = txt_to_edge(x)
        return e, e

def align(b, rect, x=Edge.CenterX, y=Edge.CenterY, round_result=False):
    x, y = pair_to_edges(x, y)
    
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
    if round_result:
        return round(xoff), round(yoff)
    else:
        return (xoff, yoff)


class GeoIterable():
    def __init__(self, *items):
        self.items = items

    def __getitem__(self, key):
        return self.items[key]
    
    def map(self, fn):
        out = []
        for idx, item in enumerate(self.items):
            arg_count = len(inspect.signature(fn).parameters)
            if arg_count == 1:
                result = fn(item)
            else:
                result = fn(idx, item)
            out.append(result)
        return GeoIterable(*out)


class Rect(Geometrical):
    """
    Representation of a rectangle as (x, y, w, h), indexable
    
    Constructor handles multiple formats, including:
    
    * `x, y, w, h`
    * `[x, y, w, h]`
    * `w, h` (x and y default to 0, 0)

    `Rect` objects can be splat'd where lists are expected as individual arguments (as in drawBot), i.e. `rect(*my_rect)`, or can be passed directly to functions expected a list representation of a rectangle.
    """

    def FromCenter(center, w, h=None) -> "Rect":
        """Create a rect given a center point and a width and height (optional, height will default to width if not specified")"""
        x, y = center
        if not h:
            h = w
        return Rect((x - w/2, y - h/2, w, h))
    
    def Inches(w, h, dpi=72.0) -> "Rect":
        return Rect(w*dpi, h*dpi)

    def __init__(self, *rect):
        if hasattr(rect[0], "rect") and not isinstance(rect[0], Rect):
            rect = [rect[0].rect]

        if isinstance(rect[0], str):
            x, y = 0, 0
            w, h = COMMON_PAPER_SIZES[rect[0].lower()]
        elif isinstance(rect[0], int) or isinstance(rect[0], float):
            if len(rect) == 1:
                x, y = 0, 0
                w, h = rect[0], rect[0]
            else:
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
    
    def origin(self) -> tuple:
        """`(x, y)` as tuple"""
        return self.x, self.y

    def from_obj(obj, w=None, h=None) -> "Rect":
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

    def FromExtents(extents) -> "Rect":
        nw, ne, se, sw = extents
        return Rect(sw[0], sw[1], abs(ne[0] - sw[0]), abs(ne[1] - sw[1]))
    
    def noop(self, *args, **kwargs) -> "Rect":
        return self

    def FromMnMnMxMx(extents) -> "Rect":
        """Create a rectangle from `xmin, ymin, xmax, ymax`"""
        xmin, ymin, xmax, ymax = extents
        return Rect(xmin, ymin, xmax - xmin, ymax - ymin)

    def FromPoints(*points) -> "Rect":
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

    def mnmnmxmx(self) -> tuple:
        """Return extents of rectangle as list"""
        return (self.x, self.y, self.x + self.w, self.y + self.h)

    def __getitem__(self, key):
        return self.rect()[key]

    def __repr__(self):
        return "Rect({:.2f},{:.2f},{:.2f},{:.2f})".format(*self.rect())
    
    def __eq__(self, r):
        try:
            return all([self.x == r.x, self.y == r.y, self.w == r.w, self.h == r.h])
        except:
            return False
    
    __hash__ = object.__hash__

    def rect(self) -> list:
        """x,y,w,h in list"""
        return [self.x, self.y, self.w, self.h]
    
    def ambit(self, tx=None, ty=None) -> "Rect":
        return self
    
    @property
    def r(self) -> "Rect":
        """A Scaffold has an .r, this was we can always 'cast' a Scaffold/Rect to a Rect"""
        return self
    
    xywh = rect
    
    def round(self) -> "Rect":
        """round the values in the rectangle to the nearest integer"""
        return Rect([int(round(n)) for n in self])

    def xy(self) -> list:
        """equivalent to origin"""
        return [self.x, self.y]

    def wh(self) -> list:
        """the width and height as a tuple"""
        return [self.w, self.h]
    
    @property
    def mnx(self) -> int:
        return self.x
    
    @property
    def mny(self) -> int:
        return self.y

    @property
    def mxx(self) -> int:
        return self.x + self.w
    
    @property
    def mxy(self) -> int:
        return self.y + self.h
    
    @property
    def mdx(self) -> int:
        return self.point("C").x
    
    @property
    def mdy(self) -> int:
        return self.point("C").y

    def square(self, outside=False) -> "Rect":
        """take a square from the center of this rect"""
        if not outside:
            return Rect(centered_square_inside(self.rect()))
        else:
            return Rect(centered_square_outside(self.rect()))
    
    def fit_aspect(self, x, y, align="C", grid=False):
        aspect_ratio = x / y

        if self.w / self.h > aspect_ratio:
            scale = self.h / y
            inner_width = x * scale
            inner_height = self.h
        else:
            scale = self.w / x
            inner_width = self.w
            inner_height = y * scale

        r = Rect(self.x, self.y, inner_width, inner_height).align(self, align)
        if grid:
            return r.grid(x, y)
        else:
            return r
    
    def align(self, rect, x=Edge.CenterX, y=Edge.CenterY, round_result=False) -> "Rect":
        return self.offset(*align(self, rect, x, y, round_result=round_result))
    
    def ipos(self, pt, defaults=(0.5, 0.5), clamp=True) -> tuple:
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

    def divide(self, amount, edge, forcePixel=False) -> list:
        """
        **Dividing**

        Derived from the behavior of the classic Cocoa function CGRectDivide, which takes a rectangle and breaks it into two pieces, based on a pixel amount and an edge.

        A quick example: assume you have a rectangle, `r`, defined as such:

        `r = Rect(0, 0, 300, 100)`
        
        If you want to break that into a left-hand rectangle that’s 100 pixels wide and a right-hand rectangle that’s 200 pixels wide, you could either say:
        
        `left, right = r.divide(100, "mnx")`
        
        `or you could say`
        
        `right, left = r.divide(200, "mxx")`

        where `mxx` is the rightmost edge, and `mnx` is the leftmost edge.

        **Centering**

        A special use-case is if you want to break a rectangle into `three` rectangles, based on the center "edge", you can do something like this:

        `left, center, right = r.divide(200, "mdx")`

        This will result in three rectangles, always left-to-right, where
        left is 50px wide, then center is 200px wide, then right is also 50px wide — anything not in the center will be evenly distributed between left and right, or top-and-bottom in the case of a Y edge.
        """
        edge = txt_to_edge(edge)
        if edge == Edge.CenterX or edge == Edge.CenterY:
            a, b, c = divide(self.rect(), amount, edge, forcePixel=forcePixel)
            return GeoIterable(Rect(a), Rect(b), Rect(c))
        else:
            a, b = divide(self.rect(), amount, edge, forcePixel=forcePixel)
            return GeoIterable(Rect(a), Rect(b))

    def subdivide(self, amount, edge, forcePixel=False) -> list:
        """
        Like `divide`, but here you specify the number of equal pieces you want (like columns or rows), and then what edge to start at, i.e.
        
        .. code:: python
            
            r = Rect(0, 0, 500, 100)
            r.subdivide(5, "mxx")
            => [Rect([400.0, 0, 100.0, 100]), Rect([300.0, 0, 100.0, 100]), Rect([200.0, 0, 100.0, 100]), Rect([100.0, 0, 100.0, 100]), Rect([0, 0, 100.0, 100])]
        
        will get you five 100-px wide rectangles, right-to-left

        (N.B. Does not support center edges, as that makes no sense)
        """
        edge = txt_to_edge(edge)
        return [Rect(x) for x in subdivide(self.rect(), amount, edge, forcePixel=forcePixel)]
    
    def subdivide_with_leading(self, count, leading, edge, forcePixel=True) -> list:
        """
        Same as `subdivide`, but inserts leading between each subdivision
        """
        return self.subdivide_with_leadings(count, [leading]*(count-1), edge, forcePixel)

    def subdivide_with_leadings(self, count, leadings, edge, forcePixel=True) -> list:
        """
        Same as `subdivide_with_leadings`, but inserts leading between each subdivision, indexing the size of the leading from a list of leadings
        """
        edge = txt_to_edge(edge)
        leadings = leadings + [0]
        full = self.w if edge == Edge.MinX or edge == Edge.MaxX else self.h
        unit = (full - sum(leadings)) / count
        amounts = [val for pair in zip([unit] * count, leadings) for val in pair][:-1]
        return [Rect(x) for x in subdivide(self.rect(), amounts, edge, forcePixel=forcePixel)][::2]
    
    sub = subdivide
    subl = subdivide_with_leading
    subls = subdivide_with_leadings

    def transform(self, t) -> "Rect":
        pts = ["NW", "NE", "SE", "SW"]
        x1, x2, x3, x4 = [t.transformPoint(self.point(pt)) for pt in pts]
        return Rect.FromExtents([x1, x2, x3, x4])

    def rotate(self, degrees, point=None) -> "Rect":
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

    def scale(self, s, x_edge=Edge.MinX, y_edge=Edge.MinY) -> "Rect":
        return Rect(scale(self.rect(), s, x_edge, y_edge))
        #x_edge = txt_to_edge(x_edge)
        #y_edge = txt_to_edge(y_edge)
        #sx = self.w * s
        #sy = self.h * s
        #return self.take(sx, x_edge, forcePixel=True).take(sy, y_edge, forcePixel=True)

    def union(self, otherRect) -> "Rect":
        return Rect.FromMnMnMxMx(unionRect(self.mnmnmxmx(), otherRect.mnmnmxmx()))
    
    def intersection(self, otherRect) -> "Rect":
        return Rect.FromMnMnMxMx(sectRect(self.mnmnmxmx(), otherRect.mnmnmxmx())[1])
    
    sect = intersection

    def take(self, amount, edge, forcePixel=False) -> "Rect":
        """
        Like `divide`, but here it just returns the "first" rect from a divide call, not all the resulting pieces, i.e. you can "take" 200px from the center of a rectangle by doing this `Rect(0, 0, 300, 100).take(200, "mdx")` which will result in `Rect([50, 0, 200, 100])`
        """
        edge = txt_to_edge(edge)
        if not isinstance(edge, Edge):
            res = self
            for e in edge:
                res = res.take(amount, e, forcePixel=forcePixel)
            return res
        else:
            return Rect(take(self.rect(), amount, edge, forcePixel=forcePixel))

    def takeOpposite(self, amount, edge, forcePixel=False) -> "Rect":
        edge = txt_to_edge(edge)
        return self.divide(amount, edge, forcePixel=forcePixel)[1]

    def subtract(self, amount, edge, forcePixel=False) -> "Rect":
        """
        The opposite of `take`, this will remove and not return a piece of the given amount from the given edge.
        
        Let's say you have a 100px-wide square and you want to drop 10px from the right-hand side, you would do:

        `Rect(100, 100).subtract(10, Edge.MaxX)`, which leaves you with `Rect([0, 0, 90, 100])`
        """
        edge = txt_to_edge(edge)
        return Rect(subtract(self.rect(), amount, edge, forcePixel=forcePixel))
    
    drop = subtract

    def expand(self, amount, edge) -> "Rect":
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

    def inset(self, dx, dy=None) -> "Rect":
        """
        Creates padding in the amount of dx and dy. Also does expansion with negative values, or both at once
        """
        if dy == None:
            dy = dx
        return Rect(inset(self.rect(), dx, dy))
    
    def inset_x(self, dx) -> "Rect":
        return self.inset(dx, 0)
    
    def inset_y(self, dy) -> "Rect":
        return self.inset(0, dy)

    def offset(self, dx, dy=None) -> "Rect":
        if dy == None:
            dy = dx
        return Rect(offset(self.rect(), dx, dy))
    
    def offset_x(self, dx) -> "Rect":
        return self.offset(dx, 0)
    
    def offset_y(self, dy) -> "Rect":
        return self.offset(0, dy)
    
    o = offset

    def zero(self) -> "Rect":
        """disregard origin and set it to (0,0)"""
        return Rect((0, 0, self.w, self.h))
    
    def nonzero(self) -> bool:
        """is this rect not just all zeros?"""
        return not (self.x == 0 and self.y == 0 and self.w == 0 and self.h == 0)

    def __add__(self, another_rect):
        return self.union(another_rect)
        #return Rect(add(self, another_rect))

    def grid(self, columns=2, rows=None) -> list:
        """Construct a grid; if rows is None, rows = columns"""
        if rows is None:
            rows = columns

        xs = [row.subdivide(columns, Edge.MinX) for row in self.subdivide(rows, Edge.MaxY)]
        return [item for sublist in xs for item in sublist]

    def pieces(self, amount, edge) -> list:
        edge = txt_to_edge(edge)
        return [Rect(x) for x in pieces(self.rect(), amount, edge)]

    def edge(self, edge) -> Line:
        edge = txt_to_edge(edge)
        return Line(*edgepoints(self.rect(), edge))

    def center(self) -> Point:
        return Point(centerpoint(self.rect()))

    def flip(self, h) -> "Rect":
        return Rect([self.x, h - self.h - self.y, self.w, self.h])

    def cardinals(self) -> tuple:
        return self.point("N"), self.point("E"), self.point("S"), self.point("W")

    def intercardinals(self) -> tuple:
        return self.point("NE"), self.point("SE"), self.point("SW"), self.point("NW")
    
    def FromIntercardinals(pts) -> "Rect":
        ne, se, sw, nw = pts
        return Rect(sw[0], sw[1], abs(ne[0] - sw[0]), abs(ne[1] - sw[1]))
    
    def aspect(self) -> float:
        return self.h / self.w
    
    def fit(self, other) -> "Rect":
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
    
    def avg(self) -> Point:
        pts = self.cardinals()
        return Point(
            sum([p.x for p in pts])/4,
            sum([p.y for p in pts])/4)
    
    def asciih(self, layout, areas):
        from coldtype.grid import Grid
        g = Grid(self, layout, "a", areas)
        out = []
        for k, v in g.keyed.items():
            try:
                ki = int(k)
                out.append([ki, v])
            except ValueError:
                pass
        return [v[1] for v in sorted(out, key=lambda x: x[0])]

    def asciiv(self, layout, areas):
        from coldtype.grid import Grid
        g = Grid(self, "a", layout, areas.replace(" ", " / "))
        out = []
        for k, v in g.keyed.items():
            try:
                ki = int(k)
                out.append([ki, v])
            except ValueError:
                pass
        return [v[1] for v in sorted(out, key=lambda x: x[0])]

    def point(self, eh, ev=Edge.MinX) -> Point:
        """
        Get a `Point` at a given compass direction, chosen from
        
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

    def nsew(self):
        return [self.en, self.es, self.ee, self.ew]

    @property
    def pne(self) -> Point: return self.point("NE")

    @property
    def pe(self) -> Point: return self.point("E")

    @property
    def ee(self) -> Line: return self.edge("mxx")

    @property
    def pse(self) -> Point: return self.point("SE")

    @property
    def ps(self) -> Point: return self.point("S")

    @property
    def es(self) -> Line: return self.edge("mny")

    @property
    def psw(self) -> Point: return self.point("SW")

    @property
    def pw(self) -> Point: return self.point("W")

    @property
    def ew(self) -> Line: return self.edge("mnx")

    @property
    def pnw(self) -> Point: return self.point("NW")

    @property
    def pn(self) -> Point: return self.point("N")

    @property
    def en(self) -> Line: return self.edge("mxy")

    @property
    def pc(self) -> Point: return self.point("C")

    @property
    def ecx(self) -> Line: return self.edge("mdx")

    @property
    def ecy(self) -> Line: return self.edge("mdy")

    def contains(self, other) -> bool:
        return (self.pne.x >= other.pne.x and self.pne.y >= other.pne.y
            and self.psw.x <= other.psw.x and self.psw.y <= other.psw.y)
    
    def __contains__(self, item) -> bool:
        return self.contains(item)

    def intersects(self, other) -> bool:
        return not (self.point("NE").x < other.point("SW").x or self.point("SW").x > other.point("NE").x or self.point("NE").y < other.point("SW").y or self.point("SW").y > other.point("NE").y)
    
    def maxima(self, n, edge) -> "Rect":
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
    
    def setmnx(self, x) -> "Rect":
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
    
    def interp(self, v, other) -> "Rect":
        """Interpolate with another rect"""
        apts = self.intercardinals()
        bpts = other.intercardinals()
        ipts = [p1.interp(v, p2) for p1, p2 in zip(apts, bpts)]
        return Rect.FromIntercardinals(ipts)

    def is_integer(self):
        return all(float(x).is_integer() for x in self.rect());
