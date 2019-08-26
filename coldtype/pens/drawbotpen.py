import drawBot as db

if __name__ == "__main__":    
    import os
    import sys
    dirname = os.path.realpath(os.path.dirname(__file__))
    sys.path.append(f"{dirname}/../..")

from coldtype.geometry import Rect, Edge, Point
from coldtype.pens.drawablepen import DrawablePenMixin, Gradient

import math
from coldtype.color import Color
import textwrap
from collections import OrderedDict
from lxml import etree


class DrawBotPen(DrawablePenMixin):
    def __init__(self, dat):
        super().__init__()
        self.dat = dat
        self.bp = db.BezierPath()
        self.dat.replay(self.bp)
    
    def fill(self, color):
        if color:
            if isinstance(color, Gradient):
                pass
            elif isinstance(color, Color):
                db.fill(color.red, color.green, color.blue, color.alpha)
        else:
            db.fill(None)
    
    def stroke(self, weight=1, color=None):
        db.strokeWidth(weight)
        if color:
            if isinstance(color, Gradient):
                pass # possible?
            elif isinstance(color, Color):
                db.stroke(color.red, color.green, color.blue, color.alpha)
        else:
            db.stroke(None)
    
    def draw(self):
        with db.savedState():
            for attr in self.dat.attrs.items():
                self.applyDATAttribute(attr)
            db.drawPath(self.bp)
    
    def Page(pens, rect):
        db.newPage(rect.w, rect.h)
        for pen in pens:
            if pen:
                if hasattr(pen, "pens"):
                    for p in pen.pens:
                        DrawBotPen(p).draw()
                else:
                    DrawBotPen(pen).draw()
    
    def Save(save_to):
        db.saveImage(save_to)
    
    def Composite(pens, rect, save_to, paginate=False):
        if not paginate:
            db.newPage(rect.w, rect.h)
        for pen in pens:
            if paginate:
                db.newPage(rect.w, rect.h)
            if pen:
                if hasattr(pen, "pens"):
                    for p in pen.pens:
                        DrawBotPen(p).draw()
                else:
                    DrawBotPen(pen).draw()
        db.saveImage(save_to)


if __name__ == "__main__":
    sys.path.insert(0, os.path.realpath("."))
    from coldtype.pens.datpen import DATPen
    from coldtype.viewer import previewer

    with previewer() as p:
        r = Rect((0, 0, 500, 500))
        dp1 = DATPen(fill="random")
        dp1.oval(r.inset(100, 100))
        p = os.path.realpath(f"{dirname}/../../test/artifacts/drawbot_test2.pdf")
        #p.send(SVGPen.Composite([dp1, dp], r), rect=r)
        DrawBotPen.Page([dp1], r)
        
        dp1 = DATPen(fill="random")
        dp1.oval(r.inset(100, 100))
        DrawBotPen.Page([dp1], r)
        
        DrawBotPen.Save(p)