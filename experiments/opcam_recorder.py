from coldtype.renderer.keyboard import KeyboardShortcut
import cv2
import numpy as np
from coldtype.test import *
from random import randint
from coldtype.pens.datimage import DATImage
from drafting.text.richtext import RichText
from time import sleep

fnt1 = Font.Cacheable("~/Type/fonts/fonts/_script/BancoPro.otf")
fnt2 = Font.Cacheable("~/Type/fonts/fonts/_script/MistralD.otf")

tl = Timeline(120)

@animation((1080, 1080), rstate=1, timeline=tl)
def opcam(f, rs):
    sleep(1)

    r = f.a.r

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
            .phototype(r, blur=2, cutw=50, cut=110)
            )])
    
    return DPS([
        DP(r).f(1),
        txt.precompose(r).blendmode(skia.BlendMode.kDifference)
    ]).precompose(r)#.phototype(r, fill=0, cutw=30)