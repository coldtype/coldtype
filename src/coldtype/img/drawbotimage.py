from coldtype.img.abstract import AbstractImage

try:
    import drawBot as db
except ImportError:
    print("No DrawBot installed! `pip install git+https://github.com/typemytype/drawbot`")

class DrawBotImage(AbstractImage):
    def load_image(self, src):
        w, h = db.imageSize(src)
        im = db.ImageObject()
        with im:
            db.size(w, h)
            db.image(src, (0, 0))
        return im
    
    def width(self):
        return db.imageSize(self.src)[0]
    
    def height(self):
        return db.imageSize(self.src)[1]

    # def _resize(self, fx, fy):
    #     self._img = self._img.resize(
    #         int(self._img.width()*fx),
    #         int(self._img.height()*fy))
    
    # def _precompose_fn(self):
    #     return precompose
    
    # def write(self, path):
    #     self._img.save(str(path), skia.kPNG)
    #     return self