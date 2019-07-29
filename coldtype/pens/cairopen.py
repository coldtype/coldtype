from fontTools.pens.transformPen import TransformPen
from fontTools.misc.transform import Transform
from fontTools.pens.basePen import BasePen

try:
    import cairo
except:
    pass

if __name__ == "__main__":
    import sys
    import os
    dirname = os.path.realpath(os.path.dirname(__file__))
    sys.path.append(f"{dirname}/../..")

from coldtype.geometry import Rect, Edge, Point
from coldtype.pens.drawablepen import DrawablePenMixin
from coldtype.color import Color, Gradient


class CairoPen(DrawablePenMixin, BasePen):
    def __init__(self, dat, h, ctx, style=None):
        super().__init__(None)
        self.dat = dat
        self.h = h
        self.ctx = ctx
        tp = TransformPen(self, (1, 0, 0, -1, 0, h))
        for attr in self.findStyledAttrs(style):
            self.ctx.save()
            dat.replay(tp)
            self.applyDATAttribute(attr)
            self.ctx.restore()

    def _moveTo(self, p):
        self.ctx.move_to(p[0], p[1])

    def _lineTo(self, p):
        self.ctx.line_to(p[0], p[1])

    def _curveToOne(self, p1, p2, p3):
        self.ctx.curve_to(p1[0], p1[1], p2[0], p2[1], p3[0], p3[1])

    def _qCurveToOne(self, p1, p2):
        print("NOT SUPPORTED")
        # self.ctx.quad_to(*p1+p2)

    def _closePath(self):
        self.ctx.close_path()
    
    def fill(self, color=None):
        if color:
            if isinstance(color, Gradient):
                self.gradient(color)
            else:
                self.ctx.set_source_rgba(color.red, color.green, color.blue, color.alpha)
            self.ctx.fill()
    
    def stroke(self, weight=1, color=None):
        self.ctx.set_source_rgba(color.red, color.green, color.blue, color.alpha)
        self.ctx.set_line_width(weight)
        self.ctx.stroke()
    
    def gradient(self, gradient):
        pat = cairo.LinearGradient(*[p for s in reversed(gradient.stops) for p in s[1]])
        for idx, stop in enumerate(gradient.stops):
            c = stop[0]
            pat.add_color_stop_rgba(idx, c.red, c.green, c.blue, c.alpha)
        self.ctx.set_source(pat)
    
    def Composite(pens, rect, image_path, save=True, style=None):
        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, int(rect.w*2), int(rect.h*2))
        ctx = cairo.Context(surface)
        ctx.scale(2, 2)
        for pen in CairoPen.FindPens(pens):
            CairoPen(pen, rect.h, ctx, style=style)
        if save:
            surface.write_to_png(image_path)
        else:
            print("Should write to base64 and return — not yet supported")

if __name__ == "__main__":
    from coldtype.pens.datpen import DATPen
    from coldtype.pens.svgpen import SVGPen
    from coldtype.viewer import viewer
    from random import random
    
    r = Rect((0, 0, 500, 500))
    p = os.path.realpath(f"{dirname}/../../test/artifacts/cairopen_test2.png")
    
    dp = DATPen(fill=Gradient.Random(r), stroke=dict(weight=20, color="royalblue"))
    dp.attr("dark", fill="black", stroke="hotpink", strokeWidth=20)
    dp.oval(r.inset(100, 100))
    
    with viewer() as pv:
        pv.send(SVGPen.Composite([dp], r), r)
        CairoPen.Composite([dp], r, p, style="default")
        pv.send(p, r, image=True)