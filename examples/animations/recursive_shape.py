from coldtype import *
from coldtype.raster import *

def postprocess(render, result):
    return P(
        P(render.rect).f(1),
        P().gridlines(render.rect, 30, 30).fssw(-1, hsl(0.65, 0.65, 0.95), 1),
        result.ch(luma(render.rect, hsl(0.93, 1.00, 0.65))))

@animation((1080, 1080)
    , timeline=90
    , composites=1
    , bg=0
    , post_render=postprocess
    , release=lambda x: x.export("h264", loops=4))
def recursive_composite(f):
    return (P(
        f.lastRender(lambda img: img
            .resize(0.997)
            .align(f.a.r)
            .translate(1, -3)),
        (P(Rect(200, 200))
            .align(f.a.r.inset(100, 100), "NW")
            .rotate(f.e("eeio", 0)*-360)
            .translate(f.a.r.w*0.6*f.e("ceio", 1), 0)
            .fssw(0, 1, 10) # invert for phototype
            ))
        .ch(phototype(f.a.r,
            fill=1, blur=3, cut=133, cutw=30)))