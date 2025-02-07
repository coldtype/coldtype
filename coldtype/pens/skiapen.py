import skia, struct
from pathlib import Path

from coldtype.pens.drawablepen import DrawablePenMixin, Gradient
from coldtype.pens.skiapathpen import SkiaPathPen
from coldtype.runon.path import P
from coldtype.img.abstract import AbstractImage
from coldtype.geometry import Rect, Point
from coldtype.text.reader import Style
from coldtype.color import Color

import coldtype.skiashim as skiashim
from coldtype.img.skiasvg import SkiaSVG

try:
    from coldtype.text.colr.skia import SkiaShaders
except ImportError:
    pass


class SkiaPen(DrawablePenMixin, SkiaPathPen):
    def __init__(self, dat, rect, canvas, scale, style=None, alpha=1):
        super().__init__(dat, rect.h)
        self.scale = scale
        self.canvas = canvas
        self.rect = rect
        self.blendmode = None
        self.style = style
        self.alpha = alpha

        all_attrs = list(self.findStyledAttrs(style))

        skia_paint_kwargs = dict(AntiAlias=True)
        for attrs, attr in all_attrs:
            method, *args = attr
            if method == "skp":
                skia_paint_kwargs = args[0]
                if "AntiAlias" not in skia_paint_kwargs:
                    skia_paint_kwargs["AntiAlias"] = True
            elif method == "blendmode":
                self.blendmode = args[0].to_skia()

        for attrs, attr in all_attrs:
            filtered_paint_kwargs = {}
            for k, v in skia_paint_kwargs.items():
                if not k.startswith("_"):
                    filtered_paint_kwargs[k] = v
            #filtered_paint_kwargs["AntiAlias"] = False
            self.paint = skia.Paint(**filtered_paint_kwargs)
            if self.blendmode:
                self.paint.setBlendMode(self.blendmode)
            method, *args = attr
            if method == "skp":
                pass
            elif method == "skb":
                pass
            elif method == "blendmode":
                pass
            elif method == "stroke" and args[0].get("weight") == 0:
                pass
            elif method == "dash":
                pass
            else:
                canvas.save()
                
                if method == "COLR":
                    did_draw = False
                    self.colr(args[0], dat)
                else:
                    did_draw = self.applyDATAttribute(attrs, attr)

                self.paint.setAlphaf(self.paint.getAlphaf()*self.alpha)
                if not did_draw:
                    canvas.drawPath(self.path, self.paint)
                canvas.restore()

    def colr(self, data, pen:P):
        method, args = data
        shader_fn = getattr(SkiaShaders, method)
        if shader_fn:
            ss = pen.data("substructure").copy()
            ss.invertYAxis(self.rect.h)
            sval = ss._val.value
            
            if method == "drawPathLinearGradient":
                args["pt1"] = sval[0][1][0]
                args["pt2"] = sval[1][1][0]
            elif method == "drawPathSweepGradient":
                args["center"] = sval[0][1][0]
            elif method == "drawPathRadialGradient":
                args["startCenter"] = sval[0][1][0]
                args["endCenter"] = sval[1][1][0]

            shader = shader_fn(*args.values())
            self.paint.setStyle(skia.Paint.kFill_Style)
            self.paint.setShader(shader)
        else:
            raise Exception("No matching SkiaShaders function for " + method)

    def fill(self, color):
        self.paint.setStyle(skia.Paint.kFill_Style)
        if color:
            if isinstance(color, Gradient):
                self.gradient(color)
            elif isinstance(color, Color):
                self.paint.setColor(color.skia())
        
        if "blur" in self.dat._data:
            args = self.dat._data["blur"]
            try:
                sigma = args[0] / 3
                if len(args) > 1:
                    style = args[1]
                else:
                    style = skia.kNormal_BlurStyle
            except:
                style = skia.kNormal_BlurStyle
                sigma = args / 3
            
            if sigma > 0:
                self.paint.setMaskFilter(skia.MaskFilter.MakeBlur(style, sigma))
        
        if "shake" in self.dat._data:
            args = self.dat._data["shake"]
            self.paint.setPathEffect(skia.DiscretePathEffect.Make(*args))
    
    def stroke(self, weight=1, color=None, dash=None, miter=None):
        self.paint.setStyle(skia.Paint.kStroke_Style)
        if dash:
            self.paint.setPathEffect(skia.DashPathEffect.Make(*dash))
        if color and weight > 0:
            self.paint.setStrokeWidth(weight*self.scale)
            if miter:
                self.paint.setStrokeMiter(miter)
            
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
            self.paint.setShader(skiashim.image_makeShader(image, matrix))
        
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
            if False:
                self.canvas.scale(sx, sy)
            else:
                # TODO scale the image, or maybe that shouldn't be here? this scaling method is horrible for image quality
                self.canvas.scale(sx, sy)
            was_alpha = self.paint.getAlphaf()
            paint = skiashim.paint_withFilterQualityHigh()
            paint.setAlphaf(was_alpha*self.alpha)
            skiashim.canvas_drawImage(self.canvas, image, bx/sx, by/sy, self.paint)
            self.canvas.restore()
            return True
    
    def shadow(self, clip=None, radius=10, color=Color.from_rgb(0,0,0,1)):
        #print("SHADOW>", self.style, clip, radius, color)
        if clip:
            if isinstance(clip, Rect):
                skia.Rect()
                sr = skia.Rect(*clip.scale(self.scale, "mnx", "mny").flip(self.rect.h).mnmnmxmx())
                self.canvas.clipRect(sr)
            elif isinstance(clip, P):
                sp = SkiaPathPen(clip, self.rect.h)
                self.canvas.clipPath(sp.path, doAntiAlias=True)
        self.paint.setColor(skia.ColorBLACK)
        self.paint.setImageFilter(skia.ImageFilters.DropShadow(0, 0, radius, radius, color.skia()))
        return
    
    def Composite(pens, rect, save_to, scale=1, context=None, style=None):
        rect = rect.scale(scale).round()

        if context:
            info = skia.ImageInfo.MakeN32Premul(rect.w, rect.h)
            surface = skia.Surface.MakeRenderTarget(context, skia.Budgeted.kNo, info)
            if not surface:
                print("SURFACE CREATION FAILED, USING CPU...")
                surface = skia.Surface(rect.w, rect.h)
        else:
            #print("CPU RENDER")
            surface = skia.Surface(rect.w, rect.h)
        
        with surface as canvas:
            if callable(pens):
                pens(canvas) # direct-draw
            else:
                SkiaPen.CompositeToCanvas(pens, rect, canvas, scale=scale, style=style)

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
    
    def SVG(pens, rect, save_to, scale=1):
        stream = skia.FILEWStream(str(save_to))
        canvas = skia.SVGCanvas.Make((rect.w, rect.h), stream)
        SkiaPen.CompositeToCanvas(pens, rect, canvas, scale=scale)
        del canvas
        stream.flush()
    
    def CompositeToCanvas(pens, rect, canvas, scale=1, style=None):
        #import inspect
        #curframe = inspect.currentframe()
        #calframe = inspect.getouterframes(curframe, 2)
        #print(calframe[1][3],"-> CompositeToCanvas:", pens)

        style_ = style

        if scale != 1:
            pens.scale(scale, scale, Point((0, 0)))
        
        if not pens.visible:
            return
        
        def draw(pen, state, data):
            if state != 0:
                return

            if not pen.visible:
                return
            
            if "text" in pen._data:
                text = pen.data("text")
                style = pen.data("style")
                frame = pen.ambit()

                if not isinstance(style, Style):
                    style = Style(*style[:-1], **style[-1], load_font=0)
                
                if isinstance(style.font, str):
                    font = skia.Typeface(style.font)
                else:
                    font = skia.Typeface.MakeFromFile(str(style.font.path))
                    if len(style.variations) > 0:
                        fa = skia.FontArguments()
                        # h/t https://github.com/justvanrossum/drawbot-skia/blob/master/src/drawbot_skia/gstate.py
                        to_int = lambda s: struct.unpack(">i", bytes(s, "ascii"))[0]
                        makeCoord = skia.FontArguments.VariationPosition.Coordinate
                        rawCoords = [makeCoord(to_int(tag), value) for tag, value in style.variations.items()]
                        coords = skia.FontArguments.VariationPosition.Coordinates(rawCoords)
                        fa.setVariationDesignPosition(skia.FontArguments.VariationPosition(coords))
                        font = font.makeClone(fa)
                pt = frame.point("SW")
                canvas.drawString(
                    text,
                    pt.x,
                    rect.h - pt.y,
                    skia.Font(font, style.fontSize),
                    skia.Paint(AntiAlias=True, Color=style.fill.skia()))
                return
            elif isinstance(pen, SkiaSVG):
                #print("HELLO?", pen._img, pen.width(), pen.height())
                pen._img.render(canvas)
            elif isinstance(pen, AbstractImage):
                paint = skiashim.paint_withFilterQualityHigh()
                f = pen.data("frame")
                canvas.save()
                for action, *args in pen.transforms:
                    if action == "rotate":
                        deg, pt = args
                        canvas.rotate(-deg, pt.x, rect.h - pt.y)
                    elif action == "matrix":
                        xs = args
                        a, b, c, d, e, f = xs[0]
                        m = skia.Matrix([
                            a, b, e,
                            c, d, f,
                            0, 0, 1
                        ])
                        canvas.setMatrix(m)
                    
                paint.setAlphaf(paint.getAlphaf()*data["alpha"]*pen.alpha)
                bm = pen.blendmode()
                if bm:
                    paint.setBlendMode(bm.to_skia())
                
                skiashim.canvas_drawImage(canvas,
                    pen._img,
                    f.x,
                    rect.h - f.y - f.h,
                    paint)
                canvas.restore()
                return
            
            if state == 0:
                SkiaPen(pen, rect, canvas, scale, style=style_, alpha=data["alpha"])
        
        pens.walk(draw, visible_only=True)
    
    def Precompose(pens, rect, fmt=None, context=None, scale=1, disk=False, style=None):
        rect = rect.round()

        if scale < 0:
            rescale = abs(scale)
            scale = 1
        else:
            rescale = None

        sr = rect
        if scale != 1:
            sr = rect.scale(scale).round()
        rect = rect.round()
        if context:
            info = skia.ImageInfo.MakeN32Premul(sr.w, sr.h)
            surface = skia.Surface.MakeRenderTarget(context, skia.Budgeted.kNo, info)
            assert surface is not None
        else:
            surface = skia.Surface(sr.w, sr.h)
        
        with surface as canvas:
            canvas.save()
            canvas.scale(scale, scale)
            if callable(pens):
                pens(canvas)
            else:
                SkiaPen.CompositeToCanvas(pens.translate(-rect.x, -rect.y), rect, canvas, style=style)
            canvas.restore()
        img = surface.makeImageSnapshot()
        if rescale is not None:
            x, y, w, h = rect.scale(rescale)
            img = img.resize(int(w), int(h))
        
        if disk:
            Path(disk).parent.mkdir(exist_ok=True, parents=True)
            img.save(disk, skia.kPNG)
            #return disk
        return img
    
    def ReadImage(src):
        return skia.Image.MakeFromEncoded(skia.Data.MakeFromFileName(str(src)))