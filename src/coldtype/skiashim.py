try:
    import skia
    SKIA_87 = int(skia.__version__.split(".")[0]) <= 87
except ImportError:
    skia = None
    SKIA_87 = False

def image_makeShader(image, matrix):
    if SKIA_87:
        return image.makeShader(skia.TileMode.kRepeat, skia.TileMode.kRepeat, matrix)
    else:
        return image.makeShader(skia.TileMode.kRepeat, skia.TileMode.kRepeat, skia.SamplingOptions(), matrix)


def canvas_drawImage(canvas, image, x, y, paint=None):
    if SKIA_87:
        canvas.drawImage(image, x, y, paint)
    else:
        so = skia.SamplingOptions()
        #so = skia.SamplingOptions(skia.FilterMode.kLinear, skia.MipmapMode.kLinear)
        so = skia.SamplingOptions(skia.CubicResampler.CatmullRom())
        #so = skia.SamplingOptions(skia.CubicResampler.Mitchell())
        canvas.drawImage(image, x, y, so, paint)


def imageFilters_Blur(xblur, yblur):
    if SKIA_87:
        return skia.BlurImageFilter.Make(xblur, yblur)
    else:
        return skia.ImageFilters.Blur(xblur, yblur)


def paint_withFilterQualityHigh():
    if SKIA_87:
        return skia.Paint(AntiAlias=True, FilterQuality=skia.FilterQuality.kHigh_FilterQuality)
    else:
        #SamplingOptions=skia.SamplingOptions(skia.CubicResampler.Mitchell())
        return skia.Paint(AntiAlias=True)
    

def image_resize(img, width, height):
    if SKIA_87:
        return img.resize(width, height)
    else:
        so = skia.SamplingOptions(skia.CubicResampler.CatmullRom())
        #so = skia.SamplingOptions()
        return img.resize(width, height, so)


def make_improved_noise(e, xo, yo, xs, ys, x, y, scale, base):
    if SKIA_87:
        noise = skia.PerlinNoiseShader.MakeImprovedNoise(x, y, scale, base)
    else:
        noise = skia.PerlinNoiseShader.MakeTurbulence(x, y, scale, base)
    matrix = skia.Matrix()
    matrix.setTranslate(e*xo, e*yo)
    #matrix.setRotate(45, 0, 0)
    matrix.setScaleX(xs)
    matrix.setScaleY(ys)
    return noise.makeWithLocalMatrix(matrix)