from pathlib import Path
from coldtype.pens.datpen import DATPen, DATPens
from coldtype.geometry import Rect
from coldtype.img.blendmode import BlendMode


class DATImage(DATPen):
    def __init__(self, src, img=None):
        if isinstance(src, Path) or isinstance(src, str):
            self.src = Path(str(src)).expanduser().absolute()
            if not self.src.exists():
                raise Exception("Image src does not exist", self.src)
            if img:
                self._img = img
            else:
                self._img = self.load_image(self.src)
        else:
            self.src = None
            self._img = src
        self.transforms = []
        self.visible = True
        super().__init__()
        self.addFrame(self.rect())
    
    def load_image(self, src):
        raise NotImplementedError()
    
    def rect(self):
        return Rect(self.width(), self.height())
    
    def bounds(self):
        return self._frame
    
    def img(self):
        return None
    
    def width(self):
        raise NotImplementedError()
    
    def height(self):
        raise NotImplementedError()
    
    def align(self, rect, x="mdx", y="mdy"):
        self.addFrame(self.rect().align(rect, x, y))
        return self
    
    def _resize(self, fx, fy):
        raise NotImplementedError()
    
    def resize(self, factor, factor_y=None):
        fx, fy = factor, factor
        if factor_y is not None:
            fy = factor_y
        
        if fx == 1 and fy == 1:
            return self

        self._resize(fx, fy)
        self.addFrame(
            self.rect().align(self._frame, "mnx", "mny"))
        return self
    
    def rotate(self, degrees, point=None):
        self.transforms.append(["rotate", degrees, point or self._frame.pc])
        return self
    
    def _precompose_fn(self):
        raise NotImplementedError()
    
    def precompose(self, rect, as_image=True):
        res = DATPens([self]).ch(self._precompose_fn()(rect))
        if as_image:
            return type(self).FromPen(res, original_src=self.src)
        else:
            return res
    
    def crop(self, crop, mutate=True):
        if callable(crop):
            crop = crop(self)
        
        xo, yo = -crop.bounds().x, -crop.bounds().y

        cropped = DATPens([
            (self.in_pen().translate(xo, yo)),
            (DATPen()
                .rect(self.bounds())
                .difference(crop)
                .f(0, 1)
                .blendmode(BlendMode.Clear)
                .translate(xo, yo))
            ]).ch(self._precompose_fn()(
                crop.bounds().zero()))
        
        if mutate:
            self._img = cropped.img().get("src")
            self.addFrame(self.rect())
            return self
        else:
            return DATImage(self.src, img=cropped.img().get("src"))
        
        #return self
    
    def in_pen(self):
        return (DATPen(self.bounds())
            .img(self._img, self.bounds(), pattern=False))
        
    def to_pen(self, rect=None):
        return self.precompose(rect or self._frame, as_image=False)
    
    def FromPen(pen:DATPen, original_src=None):
        return DATImage(original_src, img=pen.img().get("src"))
    
    def __str__(self):
        if self.src:
            return f"<DATImage({self.src.relative_to(Path.cwd())})/>"
        else:
            return f"<DATImage(in-memory)/>"