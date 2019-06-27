from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.misc.transform import Transform

import os
import sys
import math
dirname = os.path.realpath(os.path.dirname(__file__))

if True:
    sys.path.insert(0, os.path.expanduser("~/Type/furniture"))

from furniture.geometry import Rect, Edge, Point
from grapefruit import Color
import textwrap
from collections import OrderedDict
from lxml import etree


def flip_rect(r, h):
    return Rect((r.x, h - r.h - r.y, r.w, r.h))


class SVGPen(SVGPathPen):
    def __init__(self, dat, h):
        super().__init__(None)
        self.defs = []
        self.uses = []
        self.dat = dat
        self.h = h
        tp = TransformPen(self, (1, 0, 0, -1, 0, h))
        dat.replay(tp)
    
    def fill(self, path, color):
        if color:
            if isinstance(color, str):
                path.set("fill", color)
            if isinstance(color, Color):
                path.set("fill", self.rgba(color))
            else:
                path.set("fill", f"url('#{self.gradient(color)}')")
        else:
            path.set("fill", "transparent")
    
    def stroke(self, path, weight=1, color=None):
        path.set("stroke-width", str(weight))
        path.set("stroke", self.rgba(color))
    
    def rgba(self, color):
        r, g, b = color.ints
        return f"rgba({r}, {g}, {b}, {color.alpha})"
    
    def rect(self, rect):
        r = etree.Element("rect")
        fr = flip_rect(rect, self.h)
        r.set("x", str(fr.x))
        r.set("y", str(fr.y))
        r.set("width", str(fr.w))
        r.set("height", str(fr.h))
        return r
    
    def shadow(self, path, clip=None, radius=10, alpha=0.3):
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
        fe.set("flood-opacity", str(alpha))
        f.append(fe)
        self.defs.append(f)
        if clip:
            cp = etree.Element("clipPath")
            cp.set("id", f"clip-path_{hsh}")
            cp.append(self.rect(clip))
            self.defs.append(cp)
        #path.set("fill", "rgba(0, 0, 0, 0.3)")
        path.set("filter", f"url(#{f.get('id')})")
        if clip:
            path.set("clip-path", f"url(#clip-path_{hsh})")

    def gradient(self, gradient):
        lg = etree.Element("linearGradient")
        lg.set("id", f"gradient-{hash(self.getCommands())}")
        if gradient[1][1].x == gradient[0][1].x:
            lg.set("gradientTransform", "rotate(90)")
        s1 = etree.Element("stop", offset="0%")
        s1.set("stop-color", self.rgba(gradient[0][0]))
        s2 = etree.Element("stop", offset="100%")
        s2.set("stop-color", self.rgba(gradient[1][0]))
        lg.append(s1)
        lg.append(s2)
        self.defs.append(lg)
        return lg.get("id")
    
    def image(self, path, src=None, opacity=None, rect=None):
        hsh = {hash(self.getCommands())}
        img = etree.Element("image")
        img.set("x", str(rect.x or 0))
        img.set("y", str(rect.y or 0))
        img.set("width", str(rect.w or 100))
        img.set("height", str(rect.h or 100))
        img.set("opacity", str(opacity))
        img.set("image-href", f"data:image/png;base64,{src}")
        pattern = etree.Element("pattern", x="0", y="0", width="100", height="100", patternUnits="userSpaceOnUse")
        pattern.set("id", f"pattern-{hsh}")
        pattern.append(img)
        self.defs.append(pattern)
        path.set("fill", f"url(#pattern-{hsh})")
    
    def asSVG(self):
        path = etree.Element("path")
        for k, v in self.dat.attrs.items():
            if k == "shadow":
                self.shadow(path, **v)
                #self.fill(path, Color.from_rgb(1, 0, 0.5, 0.01))
            elif k == "fill":
                self.fill(path, v)
            elif k == "stroke":
                self.stroke(path, **v)
            elif k == "image":
                self.image(path, **v)
        path.set("d", self.getCommands())
        g = etree.Element("g")
        defs = etree.Element("defs")
        for d in self.defs:
            defs.append(d)
        g.append(defs)
        g.append(path)
        for u in self.uses:
            g.append(u)
        return g
    
    def Composite(pens, rect, offset=False):
        docroot = etree.Element("svg")
        docroot.set("xmlns", "http://www.w3.org/2000/svg")
        docroot.set("width", str(rect.w))
        docroot.set("height", str(rect.h))
        if offset:
            docroot.set("style", f"left:{rect.x}px;bottom:{rect.y}px;")
        for pen in pens:
            if pen:
                sp = SVGPen(pen, rect.h)
                docroot.append(sp.asSVG())
        return etree.tostring(docroot, pretty_print=True).decode("utf-8").replace("image-href", "xlink:href")


if __name__ == "__main__":
    sys.path.insert(0, os.path.realpath("."))
    from coldtype.pens.datpen import DATPen
    from coldtype.viewer import previewer

    r = Rect((0, 0, 500, 500))
    dp1 = DATPen(fill=Color.from_html("deeppink"))
    dp1.oval(r.inset(200, 200))
    
    with previewer() as p:
        p.send(SVGPen.Composite([dp1], r), rect=r)