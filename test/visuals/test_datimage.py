from coldtype.test import *
from coldtype.pens.datimage import DATImage

src = "test/renders/test_chetbaker3/stub/stub_0000.png"

@renderable()
def crop_image(r):
    return DATPens([
        DATImage(src).resize(0.5).align(r).rotate(25).to_pen(r),
        #DATText("Hello", Style("Times", 120, load_font=0), r),
        #DATPen().rect(r).scale(0.85).rotate(25).f(hsl(0.3, a=0.3))
    ])

@renderable(solo=0)
def translate_images(r):
    return DATPens([
        DP(r).f(hsl(0.3)),
        (DATImage(src)
            .resize(0.5)
            #.precompose(r)
            .align(r)
            .rotate(25)
            .to_pen(r)
            .translate(-170, -100)),
        (DATImage(src)
            .resize(0.25)
            #.precompose(r)
            .align(r)
            .rotate(-25)
            #.precompose(r)
            .to_pen(r)
            .translate(0, 100))
    ]).translate(250, 0)