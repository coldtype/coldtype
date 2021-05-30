from fontTools.pens.transformPen import TransformPen
from fontTools.pens.basePen import BasePen
from pathlib import Path

try:
    import cairo
except:
    print(">>> No cairo installation found!")


from drafting.pens.drawablepen import DrawablePenMixin
from drafting.color import Color, Gradient
from drafting.beziers import raise_quadratic


class CairoPen(DrawablePenMixin, BasePen):
    def __init__(self, dat, h, ctx, style=None):
        super().__init__(None)
        self.dat = dat
        self.h = h
        self.ctx = ctx
        self._value = []
        tp = TransformPen(self, (1, 0, 0, -1, 0, h))
        
        attrs = list(self.findStyledAttrs(style))
        methods = [a[0] for a in attrs]

        if True or "shadow" not in methods:
            for attrs, attr in self.findStyledAttrs(style):
                method, *args = attr
                self.ctx.save()
                if method in ["fill", "stroke"]:
                    dat.replay(tp)
                self.applyDATAttribute(attrs, attr)
                self.ctx.restore()

    def _moveTo(self, p):
        self.ctx.move_to(p[0], p[1])
        self._value.append(p)

    def _lineTo(self, p):
        self.ctx.line_to(p[0], p[1])
        self._value.append(p)

    def _curveToOne(self, p1, p2, p3):
        self.ctx.curve_to(p1[0], p1[1], p2[0], p2[1], p3[0], p3[1])
        self._value.extend([p1, p2, p3])

    def _qCurveToOne(self, p1, p2):
        start = self._value[-1]
        q1, q2, q3 = raise_quadratic(start, (p1[0], p1[1]), (p2[0], p2[1]))
        self.ctx.curve_to(q1[0], q1[1], q2[0], q2[1], q3[0], q3[1])
        self._value.extend([q1, q2, q3])

    def _closePath(self):
        self.ctx.close_path()
    
    def fill(self, color=None):
        if color:
            if isinstance(color, Gradient):
                self.gradient(color)
            else:
                self.ctx.set_source_rgba(color.r, color.g, color.b, color.a)
            self.ctx.fill()
    
    def stroke(self, weight=1, color=None, dash=None):
        self.ctx.set_source_rgba(color.r, color.g, color.b, color.a)
        self.ctx.set_line_width(weight)
        self.ctx.stroke()
    
    def gradient(self, gradient):
        pat = cairo.LinearGradient(*[p for s in reversed(gradient.stops) for p in s[1]])
        for idx, stop in enumerate(gradient.stops):
            c = stop[0]
            pat.add_color_stop_rgba(idx, c.r, c.g, c.b, c.a)
        self.ctx.set_source(pat)
    
    def image(self, src=None, opacity=None, rect=None):
        image_surface = cairo.ImageSurface.create_from_png(src)
        pattern = cairo.SurfacePattern(image_surface)
        pattern.set_extend(cairo.Extend.REPEAT)
        if rect:
            self.ctx.scale(rect.h/self.h/2, rect.h/self.h/2)
        else:
            self.ctx.scale(0.5, 0.5)
        #self.ctx.translate(left, top)
        self.ctx.set_source(pattern)
        #self.ctx.set_source_surface(pattern)
        self.ctx.paint_with_alpha(opacity)
    
    def shadow(self, clip=None, radius=10, alpha=0.3, color=Color.from_rgb(1,0,0,1)):
        pass
    
    def Composite(pens, rect, image_path, save=True, style=None):
        ip = Path(image_path)
        if ip.suffix == ".png":
            surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, int(rect.w*2), int(rect.h*2))
            ctx = cairo.Context(surface)
            ctx.scale(2, 2)
            for pen in CairoPen.FindPens(pens):
                CairoPen(pen, rect.h, ctx, style=style)
            if save:
                surface.write_to_png(image_path)
            else:
                print("Should write to base64 and return — not yet supported")
        elif ip.suffix == ".pdf":
            surface = cairo.PDFSurface(str(ip), int(rect.w), int(rect.h))
            #print(surface)
            ctx = cairo.Context(surface)
            #ctx.scale(2, 2)
            for pen in CairoPen.FindPens(pens):
                CairoPen(pen, rect.h, ctx, style=style)
        else:
            raise Exception(f"CairoPen cannot print to format {ip.suffix}")