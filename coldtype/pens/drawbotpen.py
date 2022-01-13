try:
    import drawBot as db
except:
    pass

from coldtype.runon.path import P
from coldtype.geometry import Rect, Edge, Point
from coldtype.pens.drawablepen import DrawablePenMixin
from coldtype.color import Color, Gradient


def get_image_rect(src):
    w, h = db.imageSize(str(src))
    return Rect(0, 0, w, h)


class DrawBotPen(DrawablePenMixin, P):
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
    
    def stroke(self, weight=1, color=None, dash=None, miter=None):
        db.strokeWidth(weight)
        if dash:
            db.lineDash(dash)
        if color:
            if isinstance(color, Gradient):
                pass # possible?
            elif isinstance(color, Color):
                db.stroke(color.r, color.g, color.b, color.a)
        else:
            db.stroke(None)
        
    def image(self, src=None, opacity=1, rect=None, rotate=0, repeating=False, scale=True):
        bounds = self.dat.bounds()
        src = str(src)
        if not rect:
            rect = bounds
        try:
            img_w, img_h = db.imageSize(src)
        except ValueError:
            print("DrawBotPen: No image")
            return
        x = bounds.x
        y = bounds.y
        if repeating:
            x_count = bounds.w / rect.w
            y_count = bounds.h / rect.h
        else:
            x_count = 1
            y_count = 1
        _x = 0
        _y = 0
        while x <= (bounds.w+bounds.x) and _x < x_count:
            _x += 1
            while y <= (bounds.h+bounds.y) and _y < y_count:
                _y += 1
                with db.savedState():
                    r = Rect(x, y, rect.w, rect.h)
                    #db.fill(1, 0, 0.5, 0.05)
                    #db.oval(*r)
                    if scale == True:
                        db.scale(rect.w/img_w, center=r.point("SW"))
                    elif scale:
                        try:
                            db.scale(scale[0], scale[1], center=r.point("SW"))
                        except TypeError:
                            db.scale(scale, center=r.point("SW"))
                    db.rotate(rotate)
                    db.image(src, (r.x, r.y), alpha=opacity)
                y += rect.h
            y = 0
            x += rect.w
    
    def shadow(self, clip=None, radius=10, alpha=0.3, color=Color.from_rgb(0,0,0,1)):
        if clip:
            cp = P(clip).f(None)
            bp = db.BezierPath()
            cp.replay(bp)
            db.clipPath(bp)
        #elif self.rect:
        #    cp = P(fill=None).rect(self.rect).xor(self.dat)
        #    bp = db.BezierPath()
        #    cp.replay(bp)
        #    db.clipPath(bp)
        db.shadow((0, 0), radius*3, list(color.with_alpha(alpha)))

    def gradient(self, gradient):
        stops = gradient.stops
        db.linearGradient(stops[0][1], stops[1][1], [list(s[0]) for s in stops], [0, 1])
    
    def draw(self, scale=1, style=None):
        if len(self.dat) > 0:
            for p in self.dat._els:
                DrawBotPen(p, rect=self.rect).draw(scale=scale)
        else:
            with db.savedState():
                db.scale(scale)
                for attrs, attr in self.findStyledAttrs(style):
                    self.applyDATAttribute(attrs, attr)
                db.drawPath(self.bp)
        return self
    
    def draw_with_filters(self, rect, filters):
        im = db.ImageObject()
        with im:
            db.size(*rect.wh())
            self.draw()
        for filter_name, filter_kwargs in filters:
            getattr(im, filter_name)(**filter_kwargs)
        x, y = im.offset()
        db.image(im, (x, y))
        return self