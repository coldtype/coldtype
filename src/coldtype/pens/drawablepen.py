# Mixin for attribute-application

from coldtype.runon import Runon
from coldtype.color import Gradient, Color

class DrawablePenMixin(object):
    def print(self, *args):
        for a in args:
            if callable(a):
                print(a(self))
            else:
                print(a)
        return self

    def fill(self, el, color):
        raise Exception("Pen does not implement fill function")
    
    def stroke(self, el, weight=1, color=None, dash=None, miter=None):
        raise Exception("Pen does not implement stroke function")

    def shadow(self, el, clip=None, radius=10, alpha=0.3, color=Color.from_rgb(0,0,0,1)):
        raise Exception("Pen does not implement shadow function")

    def image(self, el, src=None, opacity=None, rect=None, pattern=True):
        raise Exception("Pen does not implement image function")

    def applyDATAttribute(self, attrs, attribute):
        k, v = attribute
        if v:
            if k == "shadow":
                return self.shadow(**v)
            elif k == "fill":
                return self.fill(v)
            elif k == "stroke":
                return self.stroke(**v, dash=attrs.get("dash"))
            elif k == "image":
                return self.image(**v)
    
    def findStyledAttrs(self, style):
        attrs = self.dat.style(style)

        for attr in attrs.items():
            if attr and attr[-1]:
                yield attrs, attr

    def FindPens(pens):
        if not isinstance(pens, Runon):
            pens = pens[0]

        found = []
        def walker(pen, pos, data):
            if pos == 0:
                found.append(pen)
        
        pens.walk(walker)

        for pen in found:
            yield pen