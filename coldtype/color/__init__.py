from random import random
from coldtype.color.html import NAMED_COLORS
from coldtype.interpolation import norm

try:
    import skia
except ImportError:
    skia = None

try:
    from fontTools.ttLib.tables.C_P_A_L_ import Color as FTCPALColor
except ImportError:
    FTCPALColor = None


def norm(value, start, stop):
    return start + (stop-start) * value

def lerp(start, stop, amt):
    return float(amt-start) / float(stop-start)


# inspired by https://github.com/xav/Grapefruit/blob/master/grapefruit.py
# but more shorthand-oriented


def hue2rgb(n1, n2=None, h=None):
    h %= 6.0
    if h < 1.0:
        return n1 + ((n2-n1) * h)
    if h < 3.0:
        return n2
    if h < 4.0:
        return n1 + ((n2-n1) * (4.0 - h))
    return n1


def hsl_to_rgb(h, s=0, l=0):
    if s == 0:
        return (l, l, l)
    if l < 0.5:
        n2 = l * (1.0 + s)
    else:
        n2 = l+s - (l*s)
    n1 = (2.0 * l) - n2
    h /= 60.0
    r = hue2rgb(n1, n2, h + 2)
    g = hue2rgb(n1, n2, h)
    b = hue2rgb(n1, n2, h - 2)
    return (r, g, b)


def rgb_to_hsl(r, g=None, b=None):
    minVal = min(r, g, b)
    maxVal = max(r, g, b)

    l = (maxVal + minVal) / 2.0
    if minVal == maxVal:
        return (0.0, 0.0, l)

    d = maxVal - minVal

    if l < 0.5:
        s = d / (maxVal + minVal)
    else:
        s = d / (2.0 - maxVal - minVal)

    dr, dg, db = [(maxVal-val) / d for val in (r, g, b)]

    if r == maxVal:
        h = db - dg
    elif g == maxVal:
        h = 2.0 + dr - db
    else:
        h = 4.0 + dg - dr

    h = (h*60.0) % 360.0
    return (h, s, l)


class Color:
    def __init__(self, *values):
        r, g, b = [float(v) for v in values[:3]]
        self.r = float(values[0])
        self.g = float(values[1])
        self.b = float(values[2])
        if len(values) > 3:
            self.a = float(values[3])
        else:
            self.a = 1
        h, s, l = rgb_to_hsl(r, g, b)
        self.h = h
        self.s = s
        self.l = l
        self.html = self.to_html()
    
    def __eq__(self, other):
        if isinstance(other, Color):
            return self.r == other.r and self.g == other.g and self.b == other.b and self.a == other.a
        else:
            return False
    
    def __str__(self):
        return "<Color:rgb({:.1f},{:.1f},{:.1f})/a={:.1f}>".format(self.r, self.g, self.b, self.a)
    
    def to_code(self):
        if self.a == 1:
            if self.s == 0:
                return f"bw({self.l})"
        elif self.a < 1:
            if self.s == 0:
                return f"bw({self.l}, {self.a})"
        
        return f"hsl({round(self.h/360.0, 2)}, {round(self.s, 2)}, {round(self.l, 2)}, {round(self.a, 2)})"

    def with_alpha(self, alpha):
        return Color(self.r, self.g, self.b, alpha)

    def ints(self):
        return [self.r*255, self.g*255, self.b*255, self.a]
    
    def __getitem__(self, index):
        return [self.r, self.g, self.b, self.a][index]

    def from_rgb(r, g, b, a=1):
        return Color(r, g, b, a)

    def from_html(html, a=1):
        html = html.strip().lower()
        if html[0] == '#':
            html = html[1:]
        elif html in NAMED_COLORS:
            html = NAMED_COLORS[html][1:]
        if len(html) == 6:
            rgb = html[:2], html[2:4], html[4:]
        elif len(html) == 3:
            rgb = ['%c%c' % (v, v) for v in html]
        else:
            raise ValueError("input #%s is not in #RRGGBB format" % html)
        return Color(*[(int(n, 16) / 255.0) for n in rgb], a)
    
    def to_html(self):
        return '#%02x%02x%02x' % tuple((min(round(v*255), 255) for v in (self.r, self.g, self.b)))
    
    def lighter(self, level):
        return Color.from_hsl(self.h, self.s, min(self.l + level, 1), self.a)
    
    def desaturate(self, level):
        return Color.from_hsl(self.h, max(self.s - level, 0), self.l, self.a)
    
    def saturate(self, level):
        return Color.from_hsl(self.h, min(self.s + level, 1), self.l, self.a)
    
    def darker(self, level):
        return Color.from_hsl(self.h, self.s, max(self.l - level, 0), self.a)

    def from_hsl(h, s, l, a=1):
        r, g, b = hsl_to_rgb(h, s, l)
        return Color(r, g, b, a)
    
    def rgba(self):
        return self.r, self.g, self.b, self.a
    
    def hsl_interp(self, v, other):
        return hsl(norm(v, self.h, other.h)/360.0, norm(v, self.s, other.s), norm(v, self.l, other.l), norm(v, self.a, other.a))
    
    def rgb_interp(self, v, other):
        return rgb(norm(v, self.r, other.r), norm(v, self.g, other.g), norm(v, self.b, other.b), norm(v, self.a, other.a))
    
    def __repr__(self):
        return "<Color:({:0.2f},{:0.2f},{:0.2f})/({:0.2f},{:0.2f},{:0.2f})a={:0.2f}/>".format(self.r, self.g, self.b, self.h, self.s, self.l, self.a)
    
    def skia(self):
        if skia:
            return skia.Color4f(self.r, self.g, self.b, self.a)
        else:
            raise Exception("Skia installation not found")

def lighten_max(color, maxLightness=0.55):
    return Color.from_hsl(color.h, color.s, max(maxLightness, color.l))


def color_var(*rgba):
    c = [random() if x == -1 or x == "random" or x == "rand" or x == "R" else x for x in rgba]
    if len(c) == 1:
        return Color.from_rgb(c[0], c[0], c[0])
    elif len(c) == 2:
        return Color.from_rgb(c[0], c[0], c[0], c[1])
    elif len(c) == 3:
        return Color.from_rgb(c[0], c[1], c[2])
    elif len(c) == 4:
        return Color.from_rgb(c[0], c[1], c[2], c[3])


def hex_to_tuple(h):
    return tuple([c/255 for c in (palette.r, palette.g, palette.b, palette.a)])


def find_random(v):
    if isinstance(v, str):
        if v == "random" or v == "r":
            return random()
        elif v.startswith("r"):
            v = v[1:]
            if "-" in v:
                limits = [float(x.strip()) for x in v.split("-")]
                return random() * (limits[1]-limits[0]) + limits[0]
            elif "," in v:
                options = [float(x.strip()) for x in v.split(",")]
                return options[randint(0, len(options))]
    try:
        return float(v)
    except:
        return v


def normalize_color(v):
    if v is None:
        return Color.from_rgb(0,0,0,0)
    elif isinstance(v, Color):
        return v
    elif isinstance(v, Gradient):
        return v
    elif isinstance(v, float) or isinstance(v, int):
        return Color.from_rgb(v, v, v)
    elif FTCPALColor and isinstance(v, FTCPALColor):
        return Color.from_rgb(v.red/255, v.green/255, v.blue/255, v.alpha/255)
    elif isinstance(v, str):
        if v == "random" or v == -1:
            return Color.from_rgb(random(), random(), random())
        elif v == "none":
            return Color.from_rgb(0,0,0,0)
        else:
            return Color.from_html(v)
    else:
        if len(v) == 1:
            if v[0] == "random":
                return Color.from_rgb(random(), random(), random(), 1)
            if v[0] == None:
                return Color.from_rgb(0,0,0,0)
            elif isinstance(v[0], str):
                return Color.from_html(v[0])
            elif isinstance(v[0], Gradient):
                return v[0]
            else:
                try:
                    iter(v[0])
                    return normalize_color(v[0])
                except TypeError:
                    return Color.from_rgb(v[0], v[0], v[0])
        elif len(v) == 2:
            if v[0] == "random" or v[0] == -1:
                return Color.from_rgb(random(), random(), random(), float(v[1]))
            elif isinstance(v[0], str):
                return Color.from_html(v[0]).with_alpha(v[1])
            else:
                c = Color.from_rgb(v[0], v[0], v[0], v[1])
                return c
        else:
            if isinstance(v[0], complex):
                vs = [find_random(x) for x in v]
                return Color.from_hsl(v[0].imag*360, *vs[1:])
            if isinstance(v[0], str) and v[0].startswith("h"):
                v = list(v)
                v[0] = v[0][1:]
                vs = [find_random(x) for x in v]
                return Color.from_hsl(vs[0]*360, *vs[1:])
            else:
                vs = [random() if _v == "random" else _v for _v in v]
                return Color.from_rgb(*vs)


def hsl(h, s=0.5, l=0.5, a=1):
    return Color.from_hsl(h*360, s, l, a)

def rgb(r, g, b, a=1):
    return Color.from_rgb(r, g, b, a)

def bw(c, a=1):
    return Color.from_rgb(c, c, c, a)


class Gradient():
    def __init__(self, *stops):
        self.stops = []
        for c, p in stops:
            self.addStop(c, p)
    
    def addStop(self, color, point):
        self.stops.append([normalize_color(color), point])
    
    def Vertical(rect, a, b):
        return Gradient([a, rect.point("N")], [b, rect.point("S")])
    
    def Horizontal(rect, a, b):
        return Gradient([a, rect.point("W")], [b, rect.point("E")])
    
    def Random(rect, opacity=0.5):
        return Gradient([("random", opacity), rect.point("SE")], [("random", opacity), rect.point("NW")])
    
    V = Vertical
    H = Horizontal
    R = Random