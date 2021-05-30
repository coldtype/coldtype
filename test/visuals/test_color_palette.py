from coldtype.test import *
import coldtype.filtering as fl
from random import randint
from noise import pnoise1
import numpy as np
import PIL.Image

def r10(x):
    return int(round(x / 150.0)) * 150

def lut(rgba):
    r, g, b, a = rgba
    if a < 100:
        a = 0
    if r > 100:
        return 255, 0, 100, 255
    elif g > 100:
        return 0, 255, 200, 255
    elif b > 100:
        return 0, 155, 255, 255
    else:
        a = 0
    return (r, g, b, a)

def contrast_cut(mp=127, w=5):
    ct = bytearray(256)
    for i in range(256):
        if i < mp - w:
            ct[i] = 0
        elif i < mp:
            ct[i] = int((255.0/2)*(1-(mp-i)/w))
        elif i == mp:
            ct[i] = 127
        elif i < mp + w:
            ct[i] = int(127+(255.0/2)*((i-mp)/w))
        else:
            ct[i] = 255
            #ct[i] = randint(0, 255)
    return ct

ct = bytearray(256)
for i in range(256):
    x = (i - 96) * 255 // 1
    ct[i] = min(255, max(0, x))

def improved(e, xo=0, yo=0, xs=1, ys=1, base=1):
    noise = skia.PerlinNoiseShader.MakeImprovedNoise(0.01, 0.01, 3, e)
    matrix = skia.Matrix()
    matrix.setTranslate(e*xo, e*yo)
    matrix.setScaleX(xs)
    matrix.setScaleY(ys)
    return noise.makeWithLocalMatrix(matrix)

@animation(timeline=Timeline(120))
def restricted_colors(f):
    t = f.a.progress(f.i, loops=0, easefn="linear")
    cp = f.a.r.point("C")
    
    c:DATPen = (StyledString("COLD", Style(co, 500, wdth=0.5, ro=1))
        #.oval(f.a.r.take(100, "mdy").square())
        #.scale(1+t.e*8)
        .pen()
        .align(f.a.r))
    
    cap_c = (c.copy()
        #.f(Gradient.Horizontal(f.a.r, hsl(0.2, s=1), hsl(0.5, s=1)))
        .f(0)
        .attr(skp=dict(
            #Shader=skia.GradientShader.MakeSweep(cx=cp.x, cy=cp.y, colors=[hsl(0.9).skia(), hsl(0.7).skia(), hsl(0.3).skia(), hsl(0.9).skia()]),
            Shader=skia.PerlinNoiseShader.MakeFractalNoise(0.01, 0.01, 2, 5),
            #Shader=skia.PerlinNoiseShader.MakeImprovedNoise(0.01, 0.01, 1, t.e*2),
            #Shader=improved(t.e, 500, 100)
        ))
        -.precompose(f.a.r)
        -.attr(skp=dict(
            AntiAlias=True,
            ImageFilter=skia.BlurImageFilter.Make(10, 10)
        ))
        .precompose(f.a.r)
        .attr(skp=dict(
            ImageFilter=skia.BlurImageFilter.Make(5, 5),
            ColorFilter=fl.as_filter(contrast_cut(100+pnoise1(t.e)*30, 10), a=0, r=1, g=1, b=1),
            #ColorFilter=skia.TableColorFilter.MakeARGB(ct, ct, ct, ct)
        ))
        #.mod_pixels(f.a.r, 0.1, lambda rgba: lut(rgba))
        .mod_pixels(f.a.r, 0.1, lambda c: [r10(x) for x in c])
        -.precompose(f.a.r)
        -.attr(skp=dict(
            ImageFilter=skia.BlurImageFilter.Make(10, 10)
        ))
        -.phototype(f.a.r, cut=10)
        -.potrace(f.a.r))

    return cap_c + DATPen().rect(f.a.r).difference(c.f(None)).f(0)
    
    return cap_c