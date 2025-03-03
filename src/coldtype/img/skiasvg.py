import skia
from coldtype.img.abstract import AbstractImage


class SkiaSVG(AbstractImage):
    def width(self):
        return self._img.containerSize().width()
    
    def height(self):
        return self._img.containerSize().height()
    
    def copy(self):
        return SkiaSVG(self._img)