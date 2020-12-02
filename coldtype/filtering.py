import skia
from functools import reduce

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