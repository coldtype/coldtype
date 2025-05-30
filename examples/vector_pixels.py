from coldtype import *
from coldtype.fx.skia import vector_pixels

@renderable((1080, 540))
def scratch(r:Rect):
    return (StSt("ABC", Font.MuSan(), 500, wght=0.25)
        .align(r)
        .ch(vector_pixels(r, scale=0.05, combine=True, lut={
            (0, 50, 100, 100): (c:=hsl(0.65)),
            (0, 37, 74, 74): c.lighter(0.1),
            (0, 25, 50, 50): c.lighter(0.2),
            (0, 12, 25, 25): c.lighter(0.3),
        }))
        .align(r)
        .print())
