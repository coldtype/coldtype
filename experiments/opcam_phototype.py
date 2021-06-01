from coldtype.test import *
from coldtype.img.skiaimage import SkiaImage
from coldtype.capture import read_frame
from coldtype.fx.skia import phototype, precompose

tl = Timeline(120, fps=30)

@animation((1080, 1080), timeline=tl, cv2caps=[0], composites=1, rstate=1)
def opcam8(f:Frame, rs):
    img = read_frame(rs.cv2caps[0])

    txt = DPS([
        #DP(f.a.r).f(hsl(0.65, 1)),
        (SkiaImage(img)
            .align(f.a.r)
            .ch(phototype(f.a.r,
                blur=1, cutw=3, cut=80, fill=hsl(0.70))))
                ])
    return DPS([
        #DP(f.a.r).f(hsl(0.8)),
        #f.last_render(lambda p: p.translate(30, 30).scale(0.9)),
        (txt.ch(precompose(f.a.r))
            .blendmode(BlendMode.Screen)
            )])