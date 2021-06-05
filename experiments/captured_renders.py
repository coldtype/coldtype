from coldtype import *
from coldtype.img.skiaimage import SkiaImage
from coldtype.fx.skia import phototype, color_phototype, potrace
from string import ascii_uppercase

dir = Path("experiments/renders/capturing_renders/to_be_captured")

fnt = Font.Cacheable("~/Type/fonts/fonts/Pilowlava-Regular.otf")

@animation((1080, 1080), timeline=Timeline(len(ascii_uppercase), 12), watch_render=dir, rstate=1)
def captured_display(f, rs):
    src = dir / "to_be_captured_{:04d}.png".format(f.i)
    return DPS([
        DP(f.a.r).f(hsl(0.7, 1, 0.3)),
        (SkiaImage(src)
            .align(f.a.r)
            #.crop(DP(f.a.r.inset(100)))
            .ch(phototype(f.a.r, blur=3, cut=180, cutw=13, fill=hsl(0.8, 1, 0.8)))
            #.ch(potrace(f.a.r))
            #.f(1)
            ),
        ßhide(StSt(ascii_uppercase[f.i], fnt, 50)
            .align(f.a.r.inset(100), "mnx", "mxy")
            .f(1))])
