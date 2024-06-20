import skia

SKIA_87 = int(skia.__version__.split(".")[0]) <= 87

def image_makeShader(image, matrix):
    if SKIA_87:
        return image.makeShader(skia.TileMode.kRepeat, skia.TileMode.kRepeat, matrix)
    else:
        return image.makeShader(skia.TileMode.kRepeat, skia.TileMode.kRepeat, skia.SamplingOptions(), matrix)


def canvas_drawImage(canvas, image, x, y, paint=None):
    if SKIA_87:
        canvas.drawImage(image, x, y, paint)
    else:
        so = skia.SamplingOptions(skia.CubicResampler.Mitchell())
        #so = skia.SamplingOptions()
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