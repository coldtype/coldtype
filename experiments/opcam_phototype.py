from coldtype.test import *
from coldtype.pens.datimage import DATImage
from coldtype.capture import capture_frame
from coldtype.fx.skia import phototype, precompose

tl = Timeline(120)

@animation((1080, 1080), timeline=tl)
def opcam8(f):
    r = f.a.r

    if True:
        img = capture_frame(0)
    else:
        img = Path("experiments/media/bmpcc/capture{:04d}.jpg".format(f.i))

    txt = DPS([
        DP(f.a.r).f(0),
        (DATImage(img)
            .align(f.a.r)
            .ch(precompose(f.a.r, as_image=False))
            .ch(phototype(f.a.r, blur=2, cutw=50, cut=60))
            )])
    
    return DPS([
        DP(r).f(1),
        txt.ch(precompose(f.a.r).blendmode(BlendMode.Difference))
    ]).ch(precompose(f.a.r))