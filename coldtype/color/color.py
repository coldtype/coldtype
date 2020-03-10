from coldtype.color.html import NAMED_COLORS


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
