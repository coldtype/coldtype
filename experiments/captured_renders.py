from coldtype import *
from coldtype.img.skiaimage import SkiaImage
from coldtype.fx.skia import phototype, color_phototype
from string import ascii_uppercase

dir = Path("experiments/renders/capturing_renders/to_be_captured")

fnt = Font.Cacheable("~/Type/fonts/fonts/gooper/GooperText6-LightItalic.otf")

@animation((1080, 1080), timeline=len(ascii_uppercase))
def captured_display(f):
    src = dir / "to_be_captured_{:04d}.png".format(f.i)
    return DPS([
        DP(f.a.r).f(hsl(0.7, 1, 0.3)),
        (SkiaImage(src)
            .align(f.a.r)
            .ch(phototype(f.a.r, blur=2, cut=220, cutw=30, fill=hsl(0.8, 1, 0.8)))),
        ßhide(StSt(ascii_uppercase[f.i], fnt, 200)
            .align(f.a.r.inset(100), "mnx", "mxy")
            .f(0))])
