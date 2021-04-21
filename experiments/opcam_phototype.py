from coldtype.test import *
from coldtype.pens.datimage import DATImage

tl = Timeline(120)

@animation((1080, 1080), timeline=tl)
def opcam8(f):
    r = f.a.r

    img = Path("experiments/media/bmpcc/capture{:04d}.jpg".format(f.i))

    txt = DPS([
        DP(r).f(0),
        (DATImage(img)
            .align(r)
            .precompose(r, as_image=False)
            .phototype(r, blur=2, cutw=50, cut=90)
            )])
    
    return DPS([
        DP(r).f(1),
        txt.precompose(r).blendmode(skia.BlendMode.kDifference)
    ]).precompose(r)#.phototype(r, fill=0, cutw=30)