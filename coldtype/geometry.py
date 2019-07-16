from enum import Enum
import math
try:
    import drawBot as db
except ImportError:
    db = None

YOYO = "ma"

MINYISMAXY = False

from fontTools.misc.transform import Transform
from fontTools.misc.arrayTools import unionRect

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
        if txt == "maxy":
            return Edge.MaxY
        elif txt == "maxx":
            return Edge.MaxX
        elif txt == "miny":
            return Edge.MinY
        elif txt == "minx":
            return Edge.MinX
        elif txt == "centery":
            return Edge.CenterY
        elif txt == "centerx":
            return Edge.CenterX
        else:
            return None
    else:
        return txt


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
    if amount < 1.0:
        d = h if edge == Edge.MinY or edge == Edge.MaxY or edge == Edge.CenterY else w
        if amount < 0:
            return d + amount
        else:
            return d * amount  # math.floor
    else:
        return amount


def divide(rect, amount, edge, forcePixel=False):
    """
    ## Dividing
    Derived from the behavior of the classic CGRectDivide, which takes a rectangle
    and breaks it into two pieces, based on a pixel amount and an edge. So if you
    want to break a rectangle 300 pixels wide into a left-hand rectangle 100 pixels
    wide and a right-hand rectangle 200 pixels wide, you could either say:
    `left, right = divide([0, 0, 300, 100], 100, Edge.MinX)`
    _or_
    `right, left = divide([0, 0, 300, 100], 200, Edge.MaxX)`
    where MaxX is the rightmost edge, and MinX is the leftmost edge

    ## Centering
    A special use-case is if you want to break a rectangle into _three_ rectangles
    based on the center "edge", you can do something like this
    `left, center, right = divide([0, 0, 300, 100], 200, Center.MinX)`
    This will result in three rectangles, always left-to-right, where
    left is 50px wide, then center is 200px wide, then right is also 50px wide —
    anything not in the center will be evenly distributed between left and right,
    or top-and-bottom in the case of a Y edge
    """
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


def subdivide(rect, count, edge):
    """
    Like `divide`, but here you specify the number of equal pieces you want
    (like columns or rows), and then what edge to start at, i.e.
    `a, b, c, d, e = subdivide([0, 0, 500, 100], 5, Edge.MaxX)
    will get you five 100-px wide rectangles, right-to-left
    N.B. Does not support center edges, as that makes no sense
    """
    r = rect
    subs = []
    if hasattr(count, "__iter__"):
        amounts = count
        i = len(amounts) + 1
        a = 0
        while i > 1:
            s, r = divide(r, amounts[a], edge)
            subs.append(s)
            i -= 1
            a += 1
        subs.append(r)
        return subs
    else:
        i = count
        while i > 1:
            s, r = divide(r, 1/i, edge)
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
    """
    Like `divide`, but here it just returns the "first" rect from a divide call,
    not all the resulting pieces, i.e. you can "take" 200px from the center of a
    rectangle by doing this
    `take([0, 0, 300, 100], 200, Edge.CenterX)`
    which will result in
    `[50, 0, 200, 100]`
    """
    if edge == Edge.CenterX or edge == Edge.CenterY:
        _, r, _ = divide(rect, amount, edge, forcePixel=forcePixel)
        return r
    else:
        r, _ = divide(rect, amount, edge, forcePixel=forcePixel)
        return r


def subtract(rect, amount, edge):
    """
    The opposite of `take`ing, this will remove and not return a piece of the
    given amount from the given edge.
    Let's say you have a 100px-wide square and you want to drop 10px from the
    right-hand side, you would do:
    `subtract([0, 0, 100, 100], 10, Edge.MaxX)`
    that leaves you with
    `[0, 0, 90, 100]`
    Actually maybe `drop` would be a better name for this, to fit a functional-
    programming vocabulary?
    """
    _, r = divide(rect, amount, edge)
    return r


def drop(rect, amount, edge):
    return subtract(rect, amount, edge)


def inset(rect, dx, dy):
    """
    Creates padding in the amount of dx and dy
    Also does expansion with negative values, or both at once
    """
    x, y, w, h = rect
    return [x + dx, y + dy, w - (dx * 2), h - (dy * 2)]


def offset(rect, dx, dy):
    x, y, w, h = rect
    if MINYISMAXY:
        return [x + dx, y - dy, w, h]
    else:
        return [x + dx, y + dy, w, h]


def expand(rect, amount, edge):
    if edge == Edge.MinX:
        x, y, w, h = rect
        w += amount
        x -= amount
    elif edge == Edge.MaxX:
        x, y, w, h = rect
        w += amount
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

    def from_obj(obj):
        p = Point((0, 0))
        try:
            p.x = obj.x
            p.y = obj.y
        except:
            pass
        return p

    def offset(self, dx, dy):
        return Point((self.x + dx, self.y + dy))

    def rect(self, w, h):
        return Rect((self.x-w/2, self.y-h/2, w, h))

    def xy(self):
        return self.x, self.y
    
    def flip(self, frame):
        return Point((self.x, frame.h - self.y))
    
    def flipSelf(self, frame):
        x, y = self.flip(frame)
        self.x = x
        self.y = y

    def __repr__(self):
        return "<furn-Point" + str(self.xy()) + ">"

    def __getitem__(self, key):
        return self.xy()[key]

    def __setitem__(self, key, value):
        if key == 0:
            self.x = value
        elif key == 1:
            self.y = value
        else:
            raise IndexError(
                "Invalid index for point assignment, must be 0 or 1")


class Rect():
    def FromCenter(center, w, h):
        x, y = center
        return Rect((x - w/2, y - h/2, w, h))

    def __init__(self, *rect):
        if isinstance(rect[0], int) or isinstance(rect[0], float):
            x, y, w, h = rect
        else:
            x, y, w, h = rect[0]
        self.x = x
        self.y = y
        self.w = w
        self.h = h

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
        return Rect(sw[0], sw[1], ne[0] - sw[0], ne[1] - sw[1])

    def FromMnMnMxMx(extents):
        xmin, ymin, xmax, ymax = extents
        return Rect(xmin, ymin, xmax - xmin, ymax - ymin)

    def mnmnmxmx(self):
        return (self.x, self.y, self.x + self.w, self.y + self.h)

    def page():
        if db:
            return Rect((0, 0, db.width(), db.height()))
        else:
            raise ImportError(
                "DrawBot was not found, so `page` cannot be called")

    def __getitem__(self, key):
        return self.rect()[key]

    def __repr__(self):
        return "<furn-Rect" + str(self.rect()) + ">"

    def rect(self):
        return [self.x, self.y, self.w, self.h]

    def xy(self):
        return [self.x, self.y]

    def wh(self):
        return [self.w, self.h]

    def square(self):
        return Rect(centered_square(self.rect()))

    def divide(self, amount, edge, forcePixel=False):
        edge = txt_to_edge(edge)
        if edge == Edge.CenterX or edge == Edge.CenterY:
            a, b, c = divide(self.rect(), amount, edge, forcePixel=forcePixel)
            return Rect(a), Rect(b), Rect(c)
        else:
            a, b = divide(self.rect(), amount, edge, forcePixel=forcePixel)
            return Rect(a), Rect(b)

    def subdivide(self, amount, edge):
        edge = txt_to_edge(edge)
        return [Rect(x) for x in subdivide(self.rect(), amount, edge)]

    def subdivide_with_leadings(self, count, leadings, edge):
        edge = txt_to_edge(edge)
        leadings = leadings + [0]
        full = self.w if edge == Edge.MinX or edge == Edge.MaxX else self.h
        unit = (full - sum(leadings)) / count
        amounts = [val for pair in zip([unit] * count, leadings)
                   for val in pair][:-1]
        return [Rect(x) for x in subdivide(self.rect(), amounts, edge)][::2]
    
    def transform(self, t):
        pts = ["NW", "NE", "SE", "SW"]
        x1, x2, x3, x4 = [t.transformPoint(self.point(pt)) for pt in pts]
        return Rect.FromExtents([x1, x2, x3, x4])

    def scale(self, s, x_edge=Edge.CenterX, y_edge=Edge.CenterY):
        x_edge = txt_to_edge(x_edge)
        y_edge = txt_to_edge(y_edge)
        return Rect(scale(self.rect(), s, x_edge, y_edge))
    
    def union(self, otherRect):
        return Rect.FromMnMnMxMx(unionRect(self.mnmnmxmx(), otherRect.mnmnmxmx()))

    def take(self, amount, edge, forcePixel=False):
        edge = txt_to_edge(edge)
        return Rect(take(self.rect(), amount, edge, forcePixel=forcePixel))

    def takeOpposite(self, amount, edge, forcePixel=False):
        edge = txt_to_edge(edge)
        return self.divide(amount, edge, forcePixel=forcePixel)[1]

    def subtract(self, amount, edge):
        edge = txt_to_edge(edge)
        return Rect(subtract(self.rect(), amount, edge))

    def expand(self, amount, edge):
        edge = txt_to_edge(edge)
        return Rect(expand(self.rect(), amount, edge))

    def inset(self, dx, dy=None):
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
        xs = [row.subdivide(columns, Edge.MinX)
              for row in self.subdivide(rows, Edge.MaxY)]
        return [item for sublist in xs for item in sublist]

    def pieces(self, amount, edge):
        edge = txt_to_edge(edge)
        return [Rect(x) for x in pieces(self.rect(), amount, edge)]

    def edge(self, edge):
        edge = txt_to_edge(edge)
        return edgepoints(self.rect(), edge)

    def center(self):
        return Point(centerpoint(self.rect()))
    
    def flip(self, h):
        return Rect([self.x, h - self.h - self.y, self.w, self.h])
    
    def p(self, s):
        return self.point(s)

    def point(self, eh, ev=Edge.MinX):
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

if __name__ == "__main__":
    #print(Rect(0, 0, 100, 100).inset(20, 20).expand(20, "minx"))
    #r = Rect(0, 0, 100, 100)
    #t = Transform().scale(0.5, 0.5)
    #print(r.transform(t))

    print(Rect(100, 0, 500, 500).union(Rect(400, 400, 300, 300)))