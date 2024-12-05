import skia
from coldtype.img.datimage import DATImage
from coldtype.fx.skia import precompose
from coldtype.skiashim import canvas_drawImage, paint_withFilterQualityHigh, image_resize
from coldtype.runon.path import P

class SkiaImage(DATImage):
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