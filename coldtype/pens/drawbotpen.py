try:
    import drawBot as db
except:
    pass
from coldtype.pens.datpen import DATPen
from drafting.geometry import Rect, Edge, Point
from coldtype.pens.drawablepen import DrawablePenMixin, Gradient
from drafting.color import Color


def get_image_rect(src):
    w, h = db.imageSize(str(src))
    return Rect(0, 0, w, h)


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
    
    def stroke(self, weight=1, color=None, dash=None):
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
            for attrs, attr in self.findStyledAttrs(style):
                self.applyDATAttribute(attrs, attr)
            db.drawPath(self.bp)
    
    def Composite1(pens, rect, save_to, paginate=False, scale=2):
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
    
    def Composite(pens, rect, save_to, scale=2):
        db.newDrawing()
        rect = rect.scale(scale)
        db.newPage(rect.w, rect.h)

        def draw(pen, state, data):
            if state == 0:
                DrawBotPen(pen, rect).draw(scale=scale)
            elif state == -1:
                imgf = pen.data.get("imgf")
                if imgf:
                    im = db.ImageObject()
                    im.lockFocus()
                    db.size(rect.w+300, rect.h+300)
                    db.translate(150, 150)
                    db.scale(scale)
                    pen.data["im"] = im
            elif state == 1:
                imgf = pen.data.get("imgf")
                im = pen.data.get("im")
                if imgf and im:
                    im.unlockFocus()
                    imgf(im)
                    x, y = im.offset()
                    db.translate(-150, -150)
                    db.image(im, (x, y))
        
        if isinstance(pens, DATPen):
            pens = [pens]
        for dps in pens:
            dps.walk(draw)
        
        db.saveImage(str(save_to))
        db.endDrawing()
