from coldtype import *
from coldtype.warping import warp_fn

"""If you add this code to a file in the coldtype repo, you can run it as `coldtype name-of-file.py`"""

obv = Font.Cacheable("assets/ColdtypeObviously-VF.ttf")
logos = raw_ufo("assets/logos.ufo")

@renderable((1200, 600))
def nameplate(r, fontSize=500, wdth=0.25, rotate=0):
    return (DATPenSet([
        DATPen().rect(r).f(0),
        (StyledString("COLDTYPE",
            Style(obv, fontSize, wdth=wdth, tu=-50, r=1, rotate=rotate))
            .pens()
            .f(1)
            .understroke(sw=35)
            .align(r)
            .color_phototype(r, cutw=10)),
        (DATPen()
            .glyph(logos["goodhertz_logo_2019"])
            .scale(0.5)
            .align(r)
            .f(hsl(0.61, s=0.7, l=0.6))
            .flatten(5)
            .nlt(warp_fn(mult=90))
            .color_phototype(r, blur=8)
            .blendmode(skia.BlendMode.kMultiply))])
        .color_phototype(r, blur=1, cutw=50))

@renderable()
def square(r):
    hr = r.take(0.3333, "mny").round()
    return (nameplate.func(hr, 350, 0.5, 20)
        + nameplate.func(hr, 350, 0.4, 10).translate(0, hr.h)
        + nameplate.func(hr, 350, 0.25, 0).translate(0, hr.h*2))