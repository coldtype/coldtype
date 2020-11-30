from coldtype.test import *
import coldtype.filtering as fl
from random import randint
from noise import pnoise1

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
    c = f.a.r.point("C")
    return (StyledString("C", Style(co, 1000, wdth=1))
        #.oval(f.a.r.take(100, "mdy").square())
        #.scale(1+t.e*8)
        .pen()
        .align(f.a.r)
        .f(0)
        #.s(Gradient.Horizontal(f.a.r, hsl(0.2, s=1), hsl(0.5, s=1)))
        .attr(skp=dict(
            #Shader=skia.GradientShader.MakeSweep(cx=c.x, cy=c.y, colors=[hsl(0.9).skia(), hsl(0.7).skia(), hsl(0.3).skia(), hsl(0.9).skia()]),
            Shader=skia.PerlinNoiseShader.MakeFractalNoise(0.01, 0.01, 2, 5),
            #Shader=skia.PerlinNoiseShader.MakeImprovedNoise(0.01, 0.01, 1, t.e*2),
            #Shader=improved(t.e, 500, 100)
        ))
        .precompose(f.a.r)
        .attr(skp=dict(
            AntiAlias=True,
            #ImageFilter=skia.BlurImageFilter.Make(10, 10)
        ))
        .precompose(f.a.r)
        .attr(skp=dict(
            #ColorFilter=fl.as_filter(contrast_cut(100+pnoise1(t.e)*30, 10), a=1, r=0, g=1, b=0),
            ColorFilter=skia.TableColorFilter.MakeARGB(ct, ct, ct, ct)
        )))