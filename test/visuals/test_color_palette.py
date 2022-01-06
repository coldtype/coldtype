from coldtype.test import *
from coldtype.fx.skia import Skfi, mod_pixels, precompose

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

@animation(timeline=Timeline(120))
def restricted_colors(f):
    c = (StSt("COLD", co, 500, wdth=0.5, ro=1).align(f.a.r))
    
    cap_c = (c
        .copy()
        .f(0)
        .attr(skp=dict(
           Shader=skia.PerlinNoiseShader.MakeFractalNoise(0.01, 0.01, 2, 5)))
        .ch(precompose(f.a.r))
        .attr(skp=dict(
            ImageFilter=skia.BlurImageFilter.Make(5, 5),
            ColorFilter=Skfi.as_filter(
                contrast_cut(f.e("l", 0, r=(50, 190)), 10)
                , a=0, r=1, g=1, b=1),
        ))
        .ch(mod_pixels(f.a.r, 0.1, lambda c: [r10(x) for x in c]))
        )

    #print(cap_c + P(f.a.r))
    #return None
    return cap_c + P(f.a.r).difference(c).f(0)