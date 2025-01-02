from coldtype import *
from coldtype.raster import text_image

fnt, fs = "California Oranges", 200
fnt, fs = "Liebeheide", 100
fnt, fs = "PinkSugar", 500

@renderable((1080, 540), bg=1)
def texter(r):
    return (StSt("OTSVG", fnt, fs, annotate=1)
        .align(r, ty=1)
        .layer(
            lambda p: p.align(r, "N", ty=1).ch(text_image(r)),
            lambda p: p.align(r, "S", ty=1).ch(text_image(r)),
            lambda p: p.mapv(lambda p: p.ch(text_image(r))),
            lambda p: p.fssw(-1, rgb(1, 1, 1), 2)))