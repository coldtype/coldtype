from fontTools.pens.transformPen import TransformPen
from fontTools.misc.transform import Transform
from fontTools.pens.basePen import BasePen
from furniture.geometry import Rect, Edge, Point
from grapefruit import Color

try:
    import cairo
except:
    pass


class CairoPen(BasePen):
    def __init__(self, dat, h, ctx):
        super().__init__(None)
        self.dat = dat
        self.h = h
        self.ctx = ctx
        tp = TransformPen(self, (1, 0, 0, -1, 0, h))
        for k, v in self.dat.attrs.items():
            self.ctx.save()
            dat.replay(tp)
            if k == "fill":
                self.fill(v)
            elif k == "stroke":
                self.stroke(**v)
            self.ctx.restore()
    
    def _moveTo(self, p):
        self.code.append("{:s}.startNewSubPath({:.02f}f, {:.02f}f);".format(self.p, *p))

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
        self.ctx.set_source_rgba(color.red, color.green, color.blue, color.alpha)
        self.ctx.fill()
    
    def stroke(self, weight=1, color=None):
        self.ctx.set_source_rgba(color.red, color.green, color.blue, color.alpha)
        self.ctx.set_line_width(weight)
        self.ctx.stroke()
    
    def rect(self, rect, t="int"):
        return f"Rectangle<{t}>({t}({rect.x}), {t}({rect.y}), {t}({rect.w}), {t}({rect.h}))"
    
    def color(self, color):
        return "Colour::fromFloatRGBA({:.02f}f, {:.02f}f, {:.02f}f, {:.02f}f)".format(*color.rgba)
    
    def gradient(self, colors):
        gradient = []
        for color, position in colors:
            gradient.extend([self.color(color), "{:f}f".format(position.x), "{:f}f".format(self.h-position.y)])
        return "ColourGradient({:s}, false)".format(",".join(gradient))
    
    def shadow(self, clip=None, radius=14, alpha=0.3):
        d = f"drop_{self.penID}"
        self.code.append(f"DropShadow {d};")
        self.code.append("{:s}.radius = {:.02f}f;".format(d, radius))
        self.code.append(f"{d}.colour = Colours::black.withAlpha({alpha}f);") # TODO configurable
        if clip:
            self.code.append(f"{self.dp}.setDropShadow({d}, {self.rect(flip_rect(clip, self.h))});")
        else:
            self.code.append(f"{self.dp}.setDropShadow({d});")

    def image(self, image):
        bgf = f"bgFill_{self.penID}"
        self.code.append("MemoryOutputStream mo;")
        self.code.append(f"""Base64::convertFromBase64(mo, "{image}");""")
        self.code.append(f"FillType {bgf};")
        self.code.append(f"{bgf}.setTiledImage(PNGImageFormat::loadFrom(mo.getData(), mo.getDataSize()), AffineTransform().scale(1.f / (2.f)));") #g.getInternalContext().getPhysicalPixelScaleFactor()
        self.code.append(f"{bgf}.setOpacity(0.3f);")
        self.code.append(f"{self.dp}.setFill({bgf});")
    
    def Composite(pens, rect, image_path):
        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, int(rect.w), int(rect.h))
        ctx = cairo.Context(surface)
        ctx.scale(1, 1)

        for pen in pens:
            if pen:
                CairoPen(pen, rect.h, ctx)
        
        surface.write_to_png(image_path)

if __name__ == "__main__":
    import os
    import sys
    dirname = os.path.realpath(os.path.dirname(__file__))
    sys.path.insert(0, os.path.realpath("."))
    from coldtype.pens.datpen import DATPen
    from coldtype.viewer import viewer
    from random import random
    
    r = Rect((0, 0, 500, 500))
    p = os.path.realpath(f"{dirname}/../../test/artifacts/cairopen_test2.png")
    dp = DATPen(
        fill=Color.from_rgb(random(), random(), random()),
        stroke=dict(weight=20, color=Color.from_rgb(random(), random(), random()))
        )
    dp.oval(r.inset(100, 100))
    CairoPen.Composite([dp], r, p)
    
    with viewer() as pv:
        pv.send(f"<img style='background:white' src='file:///{p}?q={random()}' width={r.w/2}/>", r.scale(0.5))