from coldtype import *
from coldtype.raster import *

@animation((1080, 1080)
    , timeline=90
    , composites=1
    , bg=0
    , release=lambda x: x.export("h264", loops=4))
def recursive_composite(f):
    def postprocess(result):
        return P(
            P(f.a.r).f(1),
            P().gridlines(f.a.r, 30, 30)
                .fssw(-1, hsl(0.65, 0.65, 0.95), 1),
            result.ch(luma(f.a.r, hsl(0.93, 1.00, 0.65))))

    return (P(
        f.lastRender(lambda img: img
            .resize(0.997)
            .align(f.a.r)
            .translate(1, -3)
            ),
        (P(Rect(200, 200))
            .align(f.a.r.inset(100, 100), "NW")
            .rotate(f.e("eeio", 0)*-360)
            .translate(f.a.r.w*0.6*f.e("ceio", 1), 0)
            .fssw(0, 1, 10) # invert for phototype
            ))
        .ch(phototype(f.a.r,
            fill=1, blur=3, cut=133, cutw=30))
        .postprocess(postprocess))