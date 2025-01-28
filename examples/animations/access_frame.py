from coldtype import *
from coldtype.raster import *

@animation(Rect(540, 540), bg=1)
def numbers(f:Frame):
    # Do an inline rasterization
    # which returns a skia.Image, which can do lots
    # of things
    # https://github.com/kyamagu/skia-python/blob/main/notebooks/Python-Image-IO.ipynb

    skia_image = (StSt(str(f.i), Font.JBMono(), 300)
        .align(f.a.r)
        .chain(rasterized(f.a.r, wrapped=False)))
    
    print(type(skia_image)) # skia.Image

    # to return it to the standard coldtype renderer,
    # you’ll need to wrap it with a SkiaImage (from coldtype.raster)
    
    return SkiaImage(skia_image)


# alternate method — access disk-rendered frames from first animation (only works if you render all the frames of the first animation, by hitting the 'a' key with the viewer open)

@animation(Rect(540, 540), bg=1)
def numbers_from_rendered(f:Frame):
    path = numbers.pass_path(f.i)
    if path.exists():
        print(type(path)) # pathlib.Path
        return SkiaImage(path)