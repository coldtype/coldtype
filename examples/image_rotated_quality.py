from coldtype import *
from coldtype.raster import *

@animation(bg=1)
def scratch(f):
    shape = StSt("ABC", Font.MuSan(), 300, wght=1).align(f.a.r)
    if 1:
        img = shape.ch(precompose(f.a.r)).img()["src"]
        img = SkiaImage(img).rotate(36).ch(precompose(f.a.r))
        for _ in range(0, 9*31):
            img = SkiaImage(img.img()["src"]).rotate(36).ch(precompose(f.a.r))
    else:
        img = shape
    return img