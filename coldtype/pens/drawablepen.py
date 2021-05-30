# Mixin for attribute-application

from coldtype.pens.draftingpen import DraftingPen
from coldtype.color import Gradient, Color

class DrawablePenMixin(object):
    def fill(self, el, color):
        raise Exception("Pen does not implement fill function")
    
    def stroke(self, el, weight=1, color=None, dash=None):
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
        if style and style in self.dat.attrs:
            attrs = self.dat.attrs[style]
        else:
            attrs = self.dat.attrs["default"]
        for attr in attrs.items():
            if attr and attr[-1]:
                yield attrs, attr

    def FindPens(pens):
        if isinstance(pens, DraftingPen):
            pens = pens.collapse()._pens
        
        for pen in pens:
            if pen:
                if hasattr(pen, "_pens"):
                    for _p in pen.collapse()._pens:
                        if _p:
                            yield _p
                else:
                    yield pen