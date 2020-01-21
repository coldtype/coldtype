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

    def with_alpha(self, alpha):
        self.a = alpha
        return self
    
    def ints(self):
        return [self.r*255, self.g*255, self.b*255, self.a]

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
    
    def from_hsl(h, s, l, a=1):
        r, g, b = hsl_to_rgb(h, s, l)
        return Color(r, g, b, a)
