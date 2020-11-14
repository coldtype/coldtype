import skia, struct

from pathlib import Path

from fontTools.pens.transformPen import TransformPen
from fontTools.misc.transform import Transform
from fontTools.pens.basePen import BasePen

from coldtype.pens.datpen import DATPen, DATText
from coldtype.geometry import Rect, Edge, Point
from coldtype.pens.drawablepen import DrawablePenMixin, Gradient
from coldtype.color import Color


class SkiaPathPen(BasePen):
    def __init__(self, dat, h):
        super().__init__()
        self.dat = dat
        self.path = skia.Path()

        tp = TransformPen(self, (1, 0, 0, -1, 0, h))
        dat.replay(tp)
    
    def _moveTo(self, p):
        self.path.moveTo(p[0], p[1])

    def _lineTo(self, p):
        self.path.lineTo(p[0], p[1])

    def _curveToOne(self, p1, p2, p3):
        self.path.cubicTo(p1[0], p1[1], p2[0], p2[1], p3[0], p3[1])

    def _qCurveToOne(self, p1, p2):
        self.path.quadTo(p1[0], p1[1], p2[0], p2[1])

    def _closePath(self):
        self.path.close()


class SkiaPen(DrawablePenMixin, SkiaPathPen):
    def __init__(self, dat, rect, canvas, scale, style=None):
        super().__init__(dat, rect.h)
        self.scale = scale
        self.canvas = canvas
        self.rect = rect

        all_attrs = list(self.findStyledAttrs(style))
        skia_paint_kwargs = dict(AntiAlias=True)
        for attrs, attr in all_attrs:
            method, *args = attr
            if method == "skp":
                skia_paint_kwargs = args[0]
                if "AntiAlias" not in skia_paint_kwargs:
                    skia_paint_kwargs["AntiAlias"] = True

        for attrs, attr in all_attrs:
            self.paint = skia.Paint(**skia_paint_kwargs)
            method, *args = attr
            if method == "skp":
                pass
            elif method == "skb":
                pass
            elif method == "stroke" and args[0].get("weight") == 0:
                pass
            else:
                canvas.save()
                did_draw = self.applyDATAttribute(attrs, attr)
                if not did_draw:
                    canvas.drawPath(self.path, self.paint)
                canvas.restore()
    
    def fill(self, color):
        self.paint.setStyle(skia.Paint.kFill_Style)
        if color:
            if isinstance(color, Gradient):
                self.gradient(color)
            elif isinstance(color, Color):
                self.paint.setColor(color.skia())
    
    def stroke(self, weight=1, color=None, dash=None):
        self.paint.setStyle(skia.Paint.kStroke_Style)
        if color and weight > 0:
            self.paint.setStrokeWidth(weight)
            if isinstance(color, Gradient):
                self.gradient(color)
            else:
                self.paint.setColor(color.skia())
    
    def gradient(self, gradient):
        self.paint.setShader(skia.GradientShader.MakeLinear([s[1].flip(self.rect).xy() for s in gradient.stops], [s[0].skia() for s in gradient.stops]))
    
    def image(self, src=None, opacity=1, rect=None, pattern=True):
        if isinstance(src, skia.Image):
            image = src
        else:
            image = skia.Image.MakeFromEncoded(skia.Data.MakeFromFileName(str(src)))

        if not image:
            print("image <", src, "> not found, cannot be used")
            return
        
        _, _, iw, ih = image.bounds()
        
        if pattern:
            matrix = skia.Matrix()
            matrix.setScale(rect.w / iw, rect.h / ih)
            self.paint.setShader(image.makeShader(
                skia.TileMode.kRepeat,
                skia.TileMode.kRepeat,
                matrix
            ))
        
        if opacity != 1:
            tf = skia.ColorFilters.Matrix([
                1, 0, 0, 0, 0,
                0, 1, 0, 0, 0,
                0, 0, 1, 0, 0,
                0, 0, 0, opacity, 0
            ])
            cf = self.paint.getColorFilter()
            if cf:
                self.paint.setColorFilter(skia.ColorFilters.Compose(
                    tf, cf))
            else:
                self.paint.setColorFilter(tf)
        
        if not pattern:
            bx, by, bw, bh = self.path.getBounds()
            if rect:
                bx, by = rect.flip(self.rect.h).xy()
                #bx += rx
                #by += ry
            sx = rect.w / iw
            sy = rect.h / ih
            self.canvas.save()
            #self.canvas.setMatrix(matrix)
            self.canvas.clipPath(self.path, doAntiAlias=True)
            self.canvas.scale(sx, sy)
            self.canvas.drawImage(image, bx/sx, by/sy, self.paint)
            self.canvas.restore()
            return True
    
    def shadow(self, clip=None, radius=10, alpha=0.3, color=Color.from_rgb(0,0,0,1)):
        if clip:
            if isinstance(clip, Rect):
                skia.Rect()
                sr = skia.Rect(*clip.scale(self.scale, "mnx", "mny").flip(self.rect.h).mnmnmxmx())
                self.canvas.clipRect(sr)
        self.paint.setColor(skia.ColorBLACK)
        self.paint.setImageFilter(skia.ImageFilters.DropShadow(0, 0, radius, radius, color.with_alpha(alpha).skia()))
        #self.paint.setBlendMode(skia.BlendMode.kClear)
        return
    
    def Composite(pens, rect, save_to, scale=1, context=None):
        if context:
            info = skia.ImageInfo.MakeN32Premul(rect.w, rect.h)
            surface = skia.Surface.MakeRenderTarget(context, skia.Budgeted.kNo, info)
        else:
            print("CPU RENDER")
            surface = skia.Surface(rect.w, rect.h)
        
        with surface as canvas:
            if callable(pens):
                pens(canvas) # direct-draw
            else:
                SkiaPen.CompositeToCanvas(pens, rect, canvas, scale=scale)

        image = surface.makeImageSnapshot()
        image.save(save_to, skia.kPNG)
    
    def PDFOnePage(pens, rect, save_to, scale=1):
        stream = skia.FILEWStream(str(save_to))
        with skia.PDF.MakeDocument(stream) as document:
            with document.page(rect.w, rect.h) as canvas:
                SkiaPen.CompositeToCanvas(pens, rect, canvas, scale=scale)
    
    def PDFMultiPage(pages, rect, save_to, scale=1):
        stream = skia.FILEWStream(str(save_to))
        with skia.PDF.MakeDocument(stream) as document:
            for page in pages:
                with document.page(rect.w, rect.h) as canvas:
                    SkiaPen.CompositeToCanvas(page, rect, canvas, scale=scale)
    
    def CompositeToCanvas(pens, rect, canvas, scale=1):
        if scale != 1:
            pens.scale(scale, scale, Point((0, 0)))

        def draw(pen, state, data):
            if isinstance(pen, DATText):
                if isinstance(pen.style.font, str):
                    font = skia.Typeface(pen.style.font)
                else:
                    font = skia.Typeface.MakeFromFile(str(pen.style.font.path))
                    if len(pen.style.variations) > 0:
                        fa = skia.FontArguments()
                        # h/t https://github.com/justvanrossum/drawbot-skia/blob/master/src/drawbot_skia/gstate.py
                        to_int = lambda s: struct.unpack(">i", bytes(s, "ascii"))[0]
                        makeCoord = skia.FontArguments.VariationPosition.Coordinate
                        rawCoords = [makeCoord(to_int(tag), value) for tag, value in pen.style.variations.items()]
                        coords = skia.FontArguments.VariationPosition.Coordinates(rawCoords)
                        fa.setVariationDesignPosition(skia.FontArguments.VariationPosition(coords))
                        font = font.makeClone(fa)
                pt = pen.frame.point("SW")
                canvas.drawString(
                    pen.text,
                    pt.x,
                    rect.h - pt.y,
                    skia.Font(font, pen.style.fontSize),
                    skia.Paint(AntiAlias=True, Color=pen.style.fill.skia()))
            if state == 0:
                SkiaPen(pen, rect, canvas, scale)
        
        if isinstance(pens, DATPen):
            pens = [pens]
        elif isinstance(pens, DATText):
            pens = [pens]
            # font = sts.style.font
            # print(">>>>>>>>>>", font)
            # if isinstance(font, str):
            #     font = skia.Typeface(font)
            # else:
            #     font = skia.Typeface.MakeFromFile(font.path)
            # print(font)

            # pens = []
        
        for dps in pens:
            dps.walk(draw)
    
    def Precompose(pens, rect, fmt=None, context=None):
        if context:
            info = skia.ImageInfo.MakeN32Premul(rect.w, rect.h)
            surface = skia.Surface.MakeRenderTarget(context, skia.Budgeted.kNo, info)
            assert surface is not None
        else:
            print("CPU PRECOMPOSE")
            surface = skia.Surface(rect.w, rect.h)
        
        with surface as canvas:
            SkiaPen.CompositeToCanvas(pens, rect, canvas)
        return surface.makeImageSnapshot()
    
    def ReadImage(src):
        return skia.Image.MakeFromEncoded(skia.Data.MakeFromFileName(str(src)))