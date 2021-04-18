import cv2
import numpy as np
from coldtype import *
from random import randint
from coldtype.pens.datimage import DATImage

@renderable((1920, 1080))
def stub(r):
    capture = cv2.VideoCapture(0)
    ret, frame = capture.read()
    #bc, gc, rc = cv2.split(frame)
    #ac = np.ones(bc.shape, dtype=bc.dtype) * 50
    #image = cv2.merge((bc, gc, rc, ac))
    #image = skia.Image.fromarray(frame)
    save_to = f"experiments/media/capture0.jpg"
    cv2.imwrite(save_to, frame)
    capture.release()

    txt = DPS([
        DP(r).f(0),
        (DATImage(save_to)
            .align(r)
            .precompose(r, as_image=False)
            #.phototype(r, blur=5, cutw=35, cut=150)
            )])
    
    return DPS([
        DP(r).f(1),
        txt.precompose(r)#.blendmode(skia.BlendMode.kDifference)
    ])#.precompose(r).phototype(r, fill=hsl(0.3))