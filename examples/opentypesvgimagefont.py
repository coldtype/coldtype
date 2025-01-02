from coldtype import *
from coldtype.raster import text_image, fill

fnt = "California Oranges"

@renderable((1080, 540), bg=1)
def texter(r):
    return (P(
        StSt("Hello", fnt, 500, annotate=1)
            .align(r, ty=1)
            .ch(text_image(r))
            .ch(fill(hsl(0.6, 0.7, 0.5)))),
        StSt("Hello", fnt, 500)
            .align(r, ty=1)
            .fssw(-1, hsl(0.9, 0.9, 0.6, 0), 2))