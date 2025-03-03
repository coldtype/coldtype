import math
from coldtype.geometry.edge import Edge
from fontTools.misc.arrayTools import sectRect, unionRect


MINYISMAXY = False

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


def centered_square_outside(rect):
    x, y, w, h = rect
    if w < h:
        return [x + (w - h) / 2, y, h, h]
    else:
        return [x, y + (h - w) / 2, w, w]


def centered_square_inside(rect):
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


def subtract(rect, amount, edge, forcePixel=False):
    _, r = divide(rect, amount, edge, forcePixel=forcePixel)
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