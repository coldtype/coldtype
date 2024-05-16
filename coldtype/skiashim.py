import skia

SKIA_87 = skia.__version__.split(".")[0] == "87"
print(f"skia: m87={SKIA_87} ({skia.__version__})")

def image_makeShader(image, matrix):
    if SKIA_87:
        return image.makeShader(skia.TileMode.kRepeat, skia.TileMode.kRepeat, matrix)
    else:
        return image.makeShader(skia.TileMode.kRepeat, skia.TileMode.kRepeat, skia.SamplingOptions(), matrix)


def canvas_drawImage(canvas, image, x, y, paint=None):
    if SKIA_87:
        canvas.drawImage(image, x, y, paint)
    else:
        canvas.drawImage(image, x, y, skia.SamplingOptions(), paint)


def imageFilters_Blur(xblur, yblur):
    if SKIA_87:
        return skia.BlurImageFilter.Make(xblur, yblur)
    else:
        return skia.ImageFilters.Blur(xblur, yblur)