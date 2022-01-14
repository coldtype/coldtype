from coldtype.img.datimage import DATImage
from coldtype.fx.skia import precompose
import skia

class SkiaImage(DATImage):    
    def load_image(self, src):
        return skia.Image.MakeFromEncoded(skia.Data.MakeFromFileName(str(src)))
    
    def width(self):
        return self._img.width()
    
    def height(self):
        return self._img.height()

    def _resize(self, fx, fy):
        self._img = self._img.resize(
            int(self._img.width()*fx),
            int(self._img.height()*fy))
    
    def _precompose_fn(self):
        return precompose
    
    def write(self, path):
        self._img.save(str(path), skia.kPNG)
        return self