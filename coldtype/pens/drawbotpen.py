import drawBot as db

if __name__ == "__main__":    
    import os
    import sys
    dirname = os.path.realpath(os.path.dirname(__file__))
    sys.path.append(f"{dirname}/../..")

from coldtype.pens.datpen import DATPen
from coldtype.geometry import Rect, Edge, Point
from coldtype.pens.drawablepen import DrawablePenMixin, Gradient

import math
from coldtype.color import Color
import textwrap
from collections import OrderedDict
from lxml import etree


class DrawBotPen(DrawablePenMixin):
    def __init__(self, dat, rect=None):
        super().__init__()
        self.rect = rect
        self.dat = dat
        self.bp = db.BezierPath()
        self.dat.replay(self.bp)
    
    def fill(self, color):
        if color:
            if isinstance(color, Gradient):
                self.gradient(color)
            elif isinstance(color, Color):
                db.fill(color.r, color.g, color.b, color.a)
        else:
            db.fill(None)
    
    def stroke(self, weight=1, color=None):
        db.strokeWidth(weight)
        if color:
            if isinstance(color, Gradient):
                pass # possible?
            elif isinstance(color, Color):
                db.stroke(color.r, color.g, color.b, color.a)
        else:
            db.stroke(None)
        
    def image(self, src=None, opacity=None, rect=None, rotate=0):
        bounds = self.dat.bounds()
        try:
            img_w, img_h = db.imageSize(src)
        except:
            print("DrawBotPen: No image")
            return
        x = bounds.x
        y = bounds.y
        x_count = bounds.w / rect.w
        y_count = bounds.h / rect.h
        while x <= bounds.w:
            while y <= bounds.h:
                with db.savedState():
                    r = Rect(x, y, rect.w, rect.h)
                    #db.fill(1, 0, 0.5, 0.05)
                    #db.oval(*r)
                    db.scale(rect.w/img_w, center=r.point("SW"))
                    db.rotate(rotate)
                    db.image(src, (r.x, r.y), alpha=opacity)
                y += rect.h
            y = 0
            x += rect.w
    
    def shadow(self, clip=None, radius=10, alpha=0.3, color=Color.from_rgb(0,0,0,1)):
        if clip:
            cp = DATPen(fill=None).rect(clip)
            bp = db.BezierPath()
            cp.replay(bp)
            db.clipPath(bp)
        #elif self.rect:
        #    cp = DATPen(fill=None).rect(self.rect).xor(self.dat)
        #    bp = db.BezierPath()
        #    cp.replay(bp)
        #    db.clipPath(bp)
        db.shadow((0, 0), radius*3, list(color.with_alpha(alpha)))

    def gradient(self, gradient):
        stops = gradient.stops
        db.linearGradient(stops[0][1], stops[1][1], [list(s[0]) for s in stops], [0, 1])
    
    def draw(self, scale=2, style=None):
        with db.savedState():
            db.scale(scale)
            for attr in self.findStyledAttrs(style):
                self.applyDATAttribute(attr)
            db.drawPath(self.bp)
    
    def Composite(pens, rect, save_to, paginate=False, scale=2):
        db.newDrawing()
        rect = rect.scale(scale)
        if not paginate:
            db.newPage(rect.w, rect.h)
        for pen in DrawBotPen.FindPens(pens):
            if paginate:
                db.newPage(rect.w, rect.h)
            DrawBotPen(pen, rect).draw(scale=scale)
        db.saveImage(str(save_to))
        db.endDrawing()


if __name__ == "__main__":
    sys.path.insert(0, os.path.realpath("."))
    from coldtype.pens.datpen import DATPen
    from coldtype.viewer import previewer

    with previewer() as pv:
        r = Rect((0, 0, 500, 500))

        r0 = Rect(0, 0, 250, 250)
        dp0 = DATPen(fill="random").rect(r0.inset(100, 100)).rotate(45)
        p0 = os.path.realpath(f"{dirname}/../../test/artifacts/drawbot_test3_pattern.png")
        DrawBotPen.Composite([dp0], r0, p0, scale=2)
        pv.send(p0, r0, image=True)
        
        dp1 = DATPen(fill=("random", 0.25), stroke=("random", 0.5), strokeWidth=30)
        dp1.oval(r.inset(30, 30))
        dp2 = DATPen(fill=Gradient.Random(r.inset(100, 100)), shadow=dict(
            #clip=r.take(150, "centery"),
            alpha=0.6, radius=100))
        dp2.oval(r.inset(100, 100))
        dp3 = DATPen(fill=None, image=dict(src=p0, opacity=0.3, rect=Rect(0, 0, 53, 53))).rect(r)

        dp5 = DATPen(fill=None, stroke=("random", 0.5), strokeWidth=30).rect(r.inset(100, 100)).rotate(45)

        p = os.path.realpath(f"{dirname}/../../test/artifacts/drawbot_test2.png")
        p2 = os.path.realpath(f"{dirname}/../../test/artifacts/drawbot_test5.png")

        DrawBotPen.Composite([dp3, dp1, dp2], r, p, scale=2)
        DrawBotPen.Composite([dp5], r, p2, scale=2)

        pv.send([p, p2], r, image=True)