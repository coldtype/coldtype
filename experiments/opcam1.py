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
def stub(f, rs):
    r = f.a.r
    txt = (RichText(f.a.r,
        "OPTICAL\ncamera effects [v]",
        {"default":Style(fnt1, 270, tu=-50),
        "v":Style(fnt2, 180)})
        .xa()
        .pen()
        .f(0)
        .align(r)
        .cast(DP)
        .translate(0, -650+1300*f.a.progress(f.i, easefn="qeo").e))
    
    return DPS([
        DP(r).f(0),
        txt.f(1)])