import os

from fontTools.pens.transformPen import TransformPen
from fontTools.pens.basePen import BasePen

from drafting.pens.drawablepen import DrawablePenMixin
from drafting.color import Gradient
from drafting.color import Color
import base64

def path_str(*ps):
    return " ".join([str(int(p)) if float(p).is_integer() else "{:.02f}".format(p) for p in ps])

class JSONPen(DrawablePenMixin, BasePen):
    def __init__(self, dat, rect):
        BasePen.__init__(self, None)
        self.pStr = f""
        self.lastMove = None
        self.dat = dat
        self.serialAttrs = {"tag":dat.tag()}
        self.rect = rect
        if self.rect:
            tp = TransformPen(self, (1, 0, 0, -1, 0, self.rect.h))
            dat.replay(tp)
        else:
            dat.replay(self)

    def _moveTo(self, p):
        self.lastMove = None
        self.pStr += "m {:s} ".format(path_str(*p))

    def _lineTo(self, p):
        self.pStr += "{:s}{:s} ".format("" if self.lastMove == "l " else "l ", path_str(*p))
        self.lastMove = "l "

    def _curveToOne(self, p1, p2, p3):
        self.pStr += "{:s}{:s} ".format("" if self.lastMove == "c " else "c ", path_str(p1[0], p1[1], p2[0], p2[1], p3[0], p3[1]))
        self.lastMove = "c "

    def _qCurveToOne(self, p1, p2):
        self.pStr += "{:s}{:s} ".format("" if self.lastMove == "q " else "q ", path_str(p1[0], p1[1], p2[0], p2[1]))
        self.lastMove = "q "

    def _closePath(self):
        self.pStr += "z "
        self.lastMove = None
    
    def fill(self, color=None):
        if not color or color == "transparent":
            self.serialAttrs["fill"] = None
        elif isinstance(color, Gradient):
            self.serialAttrs["fill"] = ["g", self.gradient(color)]
        elif isinstance(color, Color):
            self.serialAttrs["fill"] = ["f", self.color(color)]
    
    def stroke(self, weight=1, color=None, dash=None):
        if color and weight > 0:
            if color == "transparent":
                self.serialAttrs["stroke"] = None
            elif isinstance(color, Color):
                self.serialAttrs["stroke"] = [self.color(color), weight]
    
    def rectPoints(self, rect):
        return [rect.x, rect.y, rect.w, rect.h]
    
    def color(self, color):
        return [round(c, 2) for c in color.rgba()]
    
    def gradient(self, gradient):
        _gradient = []
        for color, position in gradient.stops:
            _gradient.extend([[self.color(color), [position.x, self.rect.h-position.y]]])
        return _gradient
    
    def shadow(self, clip=None, radius=14, color=Color.from_rgb(0,0,0,0.3)):
        if clip:
            self.serialAttrs["shadow"] = [radius, color.a, self.rectPoints(clip.flip(self.rect.h)), self.color(color.with_alpha(1))]
        else:
            self.serialAttrs["shadow"] = [radius, color.a, None]

    def image(self, src=None, opacity=1, rect=None):
        self.serialAttrs["pattern"] = [opacity-0.025, base64.b64encode(open(src, "rb").read()).decode('utf-8')]

    def asCode(self, bounds, style=None):
        #attrs = self.dat.attrs["dark"] if "dark" in self.dat.attrs else self.dat.attrs["default"]
        allSerialAttrs = dict()
        for style, attrs in self.dat.attrs.items():
            self.serialAttrs = dict()
            for attr in attrs.items():
                self.applyDATAttribute(attrs, attr)
            allSerialAttrs[style] = self.serialAttrs
        allSerialAttrs["d"] = self.pStr
        if bounds:
            allSerialAttrs["bounds"] = self.rectPoints(bounds)
        allSerialAttrs["tag"] = self.dat.tag()
        return allSerialAttrs
    
    def Composite(pens, rect):
        out = []
        for pen in JSONPen.FindPens(pens):
            jp = JSONPen(pen, rect)
            out.append(jp.asCode(rect))
        return out