import skia
from functools import reduce
from random import Random, randint
from drafting.color import bw


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
    return ct


def as_filter(lut, a=1, r=0, g=0, b=0):
    args = [lut if x else None for x in [a, r, g, b]]
    return skia.TableColorFilter.MakeARGB(*args)


def compose(*filters):
    # TODO check if ColorFilter or something else?
    return reduce(lambda acc, el: skia.ColorFilters.Compose(el, acc) if acc else el, reversed(filters), None)


def fill(color):
    r, g, b, a = color
    return skia.ColorFilters.Matrix([
        0, 0, 0, 0, r,
        0, 0, 0, 0, g,
        0, 0, 0, 0, b,
        0, 0, 0, a, 0,
    ])

def blur(blur):
    try:
        xblur, yblur = blur
    except:
        xblur, yblur = blur, blur

    return skia.BlurImageFilter.Make(xblur, yblur)


def improved_noise(e, xo=0, yo=0, xs=1, ys=1, base=1):
    noise = skia.PerlinNoiseShader.MakeImprovedNoise(0.015, 0.015, 3, base)
    matrix = skia.Matrix()
    matrix.setTranslate(e*xo, e*yo)
    #matrix.setRotate(45, 0, 0)
    matrix.setScaleX(xs)
    matrix.setScaleY(ys)
    return noise.makeWithLocalMatrix(matrix)


def spackle(pen, xo=None, yo=None, xs=0.85, ys=0.85, base=None, cut=240, cutw=5):
    r1 = Random()
    r1.seed(0)

    if not xo:
        xo = r1.randint(-500, 500)
    if not yo:
        yo = r1.randint(-500, 500)

    if base is None:
        base = randint(0, 5000)    

    return (pen.f(1)
        .attr(skp=dict(
            Shader=(improved_noise(1, xo=xo, yo=yo, xs=xs, ys=ys, base=base)
                .makeWithColorFilter(compose(
                    fill(bw(1)),
                    as_filter(contrast_cut(cut, cutw)),
                    skia.LumaColorFilter.Make()))))))


def spackler(xo=None, yo=None, xs=0.85, ys=0.85, base=None, cut=240, cutw=5):
    def _spackle(pen):
        return spackle(pen, xo=xo, yo=yo, xs=xs, ys=ys, base=base, cut=cut, cutw=cutw)
    return _spackle