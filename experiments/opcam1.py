import cv2
import numpy as np
from coldtype.test import *
from random import randint
from coldtype.pens.datimage import DATImage
from drafting.text.richtext import RichText
from time import sleep

fnt1 = Font.Cacheable("~/Type/fonts/fonts/_script/BancoPro.otf")
fnt2 = Font.Cacheable("~/Type/fonts/fonts/_script/MistralD.otf")

tl = Timeline(60)

@animation((1080, 1080), rstate=1, timeline=tl)
def stub(f, rs):
    print(f.i)
    #sleep(3)

    r = f.a.r
    txt = (RichText(f.a.r,
        "FULLY\nvaccinated[v]",
        {"default":Style(fnt1, 270),
        "v":Style(fnt2, 200)})
        .pen()
        .f(0)
        .align(r)
        .cast(DP)
        .translate(0, -650+1300*f.a.progress(f.i).e)
        )
    
    #return DPS([
    #    DP(r).f(0),
    #    txt.copy().f(1)])

    rs.render_external(f.a.r, DPS([
        DP(r).f(0),
        txt.copy().f(1)
        #DP().oval(r.inset(100)).f(hsl(0.3))
        ]))

    return txt

    sleep(0.5)

    capture = cv2.VideoCapture(0)
    _, frame = capture.read()
    save_to = f"experiments/media/capture0.jpg"
    cv2.imwrite(save_to, frame)
    capture.release()

    txt = DPS([
        DP(r).f(0),
        (DATImage(save_to)
            .align(r)
            .precompose(r, as_image=False)
            .phototype(r, blur=2, cutw=50, cut=150)
            )])
    
    return DPS([
        DP(r).f(1),
        txt.precompose(r)#.blendmode(skia.BlendMode.kDifference)
    ]).precompose(r)#.phototype(r, fill=0, cutw=30)