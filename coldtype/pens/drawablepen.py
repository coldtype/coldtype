# Mixin for attribute-application
if __name__ == "__main__":    
    import os
    import sys
    dirname = os.path.realpath(os.path.dirname(__file__))
    sys.path.append(f"{dirname}/../..")

from coldtype.pens.datpen import DATPen, DATPenSet
from coldtype.color import Gradient, Color

class DrawablePenMixin(object):
    def fill(self, el, color):
        raise Exception("Pen does not implement fill function")
    
    def stroke(self, el, weight=1, color=None):
        raise Exception("Pen does not implement stroke function")

    def shadow(self, el, clip=None, radius=10, alpha=0.3, color=Color.from_rgb(0,0,0,1)):
        raise Exception("Pen does not implement shadow function")

    def image(self, el, src=None, opacity=None, rect=None):
        raise Exception("Pen does not implement image function")

    def applyDATAttribute(self, attribute):
        k, v = attribute
        if k == "shadow":
            self.shadow(**v)
        elif k == "fill":
            self.fill(v)
        elif k == "stroke":
            self.stroke(**v)
        elif k == "image":
            self.image(**v)
    
    def findStyledAttrs(self, style):
        if style and style in self.dat.attrs:
            attrs = self.dat.attrs[style]
        else:
            attrs = self.dat.attrs["default"]
        for attr in attrs.items():
            yield attr

    def FindPens(pens):
        if isinstance(pens, DATPen):
            pens = [pens]
        elif isinstance(pens, DATPenSet):
            pens = pens.flatten().pens
        for pen in pens:
            if pen:
                if hasattr(pen, "pens"):
                    for _p in pen.flatten().pens:
                        if _p:
                            yield _p
                else:
                    yield pen