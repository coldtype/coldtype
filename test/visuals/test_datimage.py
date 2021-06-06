from coldtype.test import *
from coldtype.img.skiaimage import SkiaImage

src = "test/visuals/renders/test_chetbaker3/stub/stub_0000.png"

@renderable()
def crop_image(r):
    return DATPens([
        SkiaImage(src).resize(0.5).align(r).rotate(25).to_pen(r),
        #DATText("Hello", Style("Times", 120, load_font=0), r),
        #DATPen().rect(r).scale(0.85).rotate(25).f(hsl(0.3, a=0.3))
    ]).a(0.5).tag("hello")

@renderable(solo=0)
def translate_images(r):
    return DATPens([
        DP(r).f(hsl(0.3)),
        (SkiaImage(src)
            .resize(0.5)
            .align(r)
            .rotate(25)
            .to_pen(r)
            #.a(0.5)
            .translate(-170, -100)),
        (SkiaImage(src)
            .resize(0.25)
            .align(r)
            .rotate(-25)
            .to_pen(r)
            .a(0.5)
            .translate(0, 100))
    ]).translate(250, 0)