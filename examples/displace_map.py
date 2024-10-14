from coldtype import *
from coldtype.img.skiaimage import SkiaImage
from coldtype.fx.skia import warp

import numpy as np
#from skimage.transform import swirl

@renderable((540, 540))
def gradient(r):
    return (P(r).f(Gradient.H(r, bw(1), bw(0))))

@renderable((540, 540))
def text(r):
    return (StSt("COLD", Font.ColdObvi(), 500, wdth=0).align(r))

@renderable((540, 540), solo=1, bg=1)
def displace(r):
    def cubic_bezier_curve(t, P0, P1, P2, P3):
        return (1 - t)**3 * P0 + 3 * (1 - t)**2 * t * P1 + 3 * (1 - t) * t**2 * P2 + t**3 * P3

    def vertical_shrink(coords):
        h = r.h
        x, y = coords.T
        t = y / h
        P0, P1, P2, P3 = -0.1, 0.25, 0.75, 1
        y_new = cubic_bezier_curve(t, P0, P1, P2, P3) * h
        return np.vstack((x, y_new)).T
    
    return (P(r).f(1)
        .up()
        .append(P().gridlines(r).fssw(-1, 0, 2))
        .ch(warp(r, vertical_shrink)))