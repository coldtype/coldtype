from pathlib import Path
from coldtype.runon.path import P
from coldtype.geometry import Rect
from coldtype.img.blendmode import BlendMode


class AbstractImage(P):
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
        self.alpha = 1

        super().__init__()
        self.data(frame=self.rect())
    
    def load_image(self, src):
        raise NotImplementedError()
    
    def write(self, path):
        raise NotImplementedError()
    
    def rect(self):
        return Rect(self.width(), self.height())
    
    def bounds(self):
        return self.data("frame")
    
    def img(self):
        return None
    
    def a(self, alpha=None):
        if alpha is None:
            return self.alpha
        else:
            self.alpha = alpha
        return self
    
    def width(self):
        raise NotImplementedError()
    
    def height(self):
        raise NotImplementedError()
    
    def align(self, rect, x="mdx", y="mdy", round_result=True, tx=True, ty=True):
        """
        tx and ty are here for keyword compatibility, they don't do anything
        """
        self.data(frame=self.rect().align(rect, x, y, round_result=round_result))
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
        self.data(frame=
            self.rect().align(self.data("frame"), "mnx", "mny"))
        return self
    
    def rotate(self, degrees, point=None):
        self.transforms.append(["rotate", degrees, point or self.data("frame").pc])
        return self
    
    def matrix(self, a, b, c, d, e, f):
        self.transforms.append(["matrix", [a, b, c, d, e, f]])
        return self
    
    def _precompose_fn(self):
        raise NotImplementedError()
    
    def precompose(self, rect, as_image=True):
        res = P([self]).ch(self._precompose_fn()(rect))
        if as_image:
            return type(self).FromPen(res, original_src=self.src)
        else:
            return res
    
    def crop(self, crop, mutate=True):
        if callable(crop):
            crop = crop(self)
        
        xo, yo = -crop.bounds().x, -crop.bounds().y

        cropped = P([
            (self.in_pen().translate(xo, yo)),
            (P()
                .rect(self.bounds())
                .difference(crop)
                .f(-1)
                .blendmode(BlendMode.Clear)
                .translate(xo, yo))
            ]).ch(self._precompose_fn()(
                crop.bounds().zero()))
        
        if mutate:
            self._img = cropped.img().get("src")
            self.data(frame=self.rect())
            return self
        else:
            return AbstractImage(self.src, img=cropped.img().get("src"))
        
        #return self
    
    def in_pen(self):
        return (P(self.bounds())
            .img(self._img, self.bounds(), pattern=False))
        
    def to_pen(self, rect=None):
        return self.precompose(rect or self.data("frame"), as_image=False)
    
    def FromPen(pen:P, original_src=None):
        return AbstractImage(original_src, img=pen.img().get("src"))
    
    def __str__(self):
        if self.src:
            try:
                return f"<AbstractImage({self.src.relative_to(Path.cwd())})/>"
            except ValueError:
                return f"<AbstractImage({self.src})/>"
        else:
            return f"<AbstractImage(in-memory)/>"