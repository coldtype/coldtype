from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.misc.transform import Transform

if __name__ == "__main__":    
    import os
    import sys
    dirname = os.path.realpath(os.path.dirname(__file__))
    sys.path.append(f"{dirname}/../..")

from coldtype.geometry import Rect, Edge, Point
from coldtype.color import Gradient
from coldtype.pens.drawablepen import DrawablePenMixin
from coldtype.pens.datpen import DATPen, DATPenSet

import math
from grapefruit import Color
import textwrap
from collections import OrderedDict
from lxml import etree


class SVGPen(DrawablePenMixin, SVGPathPen):
    def __init__(self, dat, h):
        super().__init__(None)
        self.defs = []
        self.uses = []
        self.dat = dat
        self.h = h
        tp = TransformPen(self, (1, 0, 0, -1, 0, h))
        dat.round(2).replay(tp)
    
    def _endPath(self):
        """
        >>> pen = SVGPathPen(None)
        >>> pen.endPath()
        >>> pen._commands
        ['Z']
        """
        #self._closePath()
        self._lastCommand = None
        self._lastX = self._lastY = None
    
    def fill(self, color):
        if color:
            if isinstance(color, Gradient):
                self.path.set("fill", f"url('#{self.gradient(color)}')")
            elif isinstance(color, Color):
                self.path.set("fill", self.rgba(color))
        else:
            self.path.set("fill", "transparent")
    
    def stroke(self, weight=1, color=None):
        self.path.set("stroke-width", str(weight))
        if color:
            if isinstance(color, Gradient):
                self.path.set("stroke", f"url('#{self.gradient(color)}')")
            elif isinstance(color, Color):
                self.path.set("stroke", self.rgba(color))
        else:
            self.path.set("stroke-width", 0)
            self.path.set("stroke", "transparent")
    
    def rgba(self, color):
        r, g, b = color.ints
        return f"rgba({r}, {g}, {b}, {color.alpha})"
    
    def rect(self, rect):
        r = etree.Element("rect")
        fr = rect.flip(self.h)
        r.set("x", str(fr.x))
        r.set("y", str(fr.y))
        r.set("width", str(fr.w))
        r.set("height", str(fr.h))
        return r
    
    def shadow(self, clip=None, radius=10, alpha=0.3, color=Color.from_rgb(0,0,0,1)):
        hsh = {hash(self.getCommands())}
        f = etree.Element("filter")
        f.set("x", "0")
        f.set("y", "0")
        f.set("width", "1000%")
        f.set("height", "1000%")
        f.set("x", "-500%")
        f.set("y", "-500%")
        f.set("id", f"shadow-{hsh}")
        fe = etree.Element("feDropShadow")
        fe.set("dx", "0")
        fe.set("dy", "0")
        fe.set("stdDeviation", str(radius))
        #fe.set("slope", str(alpha))
        fe.set("flood-color", self.rgba(color))
        fe.set("flood-opacity", str(alpha))
        f.append(fe)
        self.defs.append(f)
        if clip:
            cp = etree.Element("clipPath")
            cp.set("id", f"clip-path_{hsh}")
            cp.append(self.rect(clip))
            self.defs.append(cp)
        #self.path.set("fill", "rgba(0, 0, 0, 0.3)")
        self.path.set("filter", f"url(#{f.get('id')})")
        if clip:
            self.path.set("clip-path", f"url(#clip-path_{hsh})")

    def gradient(self, gradient):
        lg = etree.Element("linearGradient")
        lg.set("id", f"gradient-{hash(self.getCommands())}")
        if gradient.stops[1][1].x == gradient.stops[0][1].x:
            lg.set("gradientTransform", "rotate(90)")
        s1 = etree.Element("stop", offset="0%")
        s1.set("stop-color", self.rgba(gradient.stops[0][0]))
        s2 = etree.Element("stop", offset="100%")
        s2.set("stop-color", self.rgba(gradient.stops[1][0]))
        lg.append(s1)
        lg.append(s2)
        self.defs.append(lg)
        return lg.get("id")
    
    def image(self, src=None, opacity=None, rect=None):
        hsh = {hash(self.getCommands())}
        img = etree.Element("image")
        img.set("x", str(rect.x or 0))
        img.set("y", str(rect.y or 0))
        img.set("width", str(rect.w or 100))
        img.set("height", str(rect.h or 100))
        img.set("opacity", str(opacity))
        img.set("image-href", f"data:image/png;base64,{src}")
        pattern = etree.Element("pattern")
        pattern.set("x", img.get("x"))
        pattern.set("y", img.get("y"))
        pattern.set("width", img.get("width"))
        pattern.set("height", img.get("height"))
        pattern.set("patternUnits", "userSpaceOnUse")
        pattern.set("id", f"pattern-{hsh}")
        pattern.append(img)
        self.defs.append(pattern)
        self.path.set("fill", f"url(#pattern-{hsh})")
    
    def asSVG(self, style=None):
        self.path = etree.Element("path")
        if style and style in self.dat.attrs:
            attrs = self.dat.attrs[style]
        else:
            attrs = self.dat.attrs["default"]
        for attr in attrs.items():
            self.applyDATAttribute(attr)
        self.path.set("d", self.getCommands())
        g = etree.Element("g")
        defs = etree.Element("defs")
        for d in self.defs:
            defs.append(d)
        g.append(defs)
        g.append(self.path)
        for u in self.uses:
            g.append(u)
        return g
    
    def Composite(pens, rect, offset=False, style=None):
        docroot = etree.Element("svg")
        docroot.set("xmlns", "http://www.w3.org/2000/svg")
        docroot.set("width", str(rect.w))
        docroot.set("height", str(rect.h))
        if offset:
            docroot.set("style", f"left:{rect.x}px;bottom:{rect.y}px;")
        
        for pen in SVGPen.FindPens(pens):
            sp = SVGPen(pen, rect.h)
            docroot.append(sp.asSVG(style=style))
        
        return etree.tostring(docroot, pretty_print=True).decode("utf-8").replace("image-href", "xlink:href")


if __name__ == "__main__":
    sys.path.insert(0, os.path.realpath("."))
    from coldtype.viewer import previewer
    from coldtype.svg import read_svg_to_pen

    with previewer() as p:
        r = Rect((0, 0, 1000, 1000))
        dp1 = DATPen(fill="darkorchid")
        dp1.oval(r.inset(200, 200))
        path = os.path.expanduser("~/Type/grafprojects/vulfsans/alternate_vulfs.svg")
        dp = read_svg_to_pen(path, "lombardic-vulf")
        dp.scale(1.5)
        dp.align(r)
        dp.translate(-6, 0)
        dp.attr(fill=Color.from_rgb(1, 1, 1))
        p.send(SVGPen.Composite([dp1, dp], r), rect=r)