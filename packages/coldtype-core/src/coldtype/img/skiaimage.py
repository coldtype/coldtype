import skia
from coldtype.img.abstract import AbstractImage
from coldtype.fx.skia import precompose
from coldtype.skiashim import canvas_drawImage, paint_withFilterQualityHigh, image_resize
from coldtype.runon.path import P

class SkiaImage(AbstractImage):
    @staticmethod
    def FromBase64(b64):
        import base64
        
        if b64.startswith("data:image/"):
            b64 = b64.split(",")[1]
        
        image_data = base64.b64decode(b64)
        skia_image = skia.Image.MakeFromEncoded(skia.Data.MakeWithCopy(image_data))

        return SkiaImage(skia_image)

    def load_image(self, src):
        return skia.Image.MakeFromEncoded(skia.Data.MakeFromFileName(str(src)))
    
    def width(self):
        return self._img.width()
    
    def height(self):
        return self._img.height()
    
    def copy(self):
        return SkiaImage(self._img)

    def _resize(self, fx, fy):
        # should preserve the offset?
        # or somehow keep the alignment?
        
        self._img = image_resize(self._img,
            round(self._img.width()*fx),
            round(self._img.height()*fy))
    
    def _precompose_fn(self):
        return precompose
    
    def css_scale(self, x, y=None):
        if y is None:
            y = x
        self._img = self._redraw(lambda canvas, paint: canvas.scale(x, y))
        return self
    
    def _redraw(self, modifier):
        from coldtype.fx.skia import SKIA_CONTEXT
        from coldtype.pens.skiapen import SkiaPen

        frame = self.data("frame")

        def rotator(canvas):
            paint = paint_withFilterQualityHigh()
            modifier(canvas, paint)
            canvas_drawImage(canvas, self._img, 0, 0, paint)
        
        return SkiaPen.Precompose(rotator, frame.inset(0), context=SKIA_CONTEXT)
    
    def css_translate(self, x, y=None):
        self._img = self._redraw(lambda canvas, paint: canvas.translate(x, y))
    
    def css_matrix(self, a, b, c, d, tx, ty):
        matrix = skia.Matrix([a, c, tx, b, d, ty, 0, 0, 1])
        self._img = self._redraw(lambda canvas, paint: canvas.setMatrix(matrix))
        return self
    
    def _rotate(self, degrees, point=None):
        #self.transforms.append(["rotate", degrees, point or self.data("frame").pc])

        from coldtype.fx.skia import SKIA_CONTEXT
        from coldtype.pens.skiapen import SkiaPen
        
        frame = self.data("frame")
        rotated = P(frame).rotate(degrees, point)
        rotated_frame = rotated.ambit()#.zero()
        dx, dy = rotated_frame.x - frame.x, rotated_frame.y - frame.y

        width, height = self.width(), self.height()
        center_x, center_y = width / 2, height / 2

        def rotator(canvas):
            paint = paint_withFilterQualityHigh()
            canvas.translate(-dx, -dy)
            canvas.translate(center_x, center_y)
            canvas.rotate(-degrees)
            canvas.translate(-center_x, -center_y)
            canvas_drawImage(canvas, self._img, 0, 0, paint)
        
        img = SkiaPen.Precompose(rotator, rotated_frame, context=SKIA_CONTEXT)
        return SkiaImage(img)#.translate(dx, dy)
    
    def write(self, path):
        self._img.save(str(path), skia.kPNG)
        return self