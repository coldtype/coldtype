from coldtype import *
from coldtype.midi.controllers import LaunchControlXL
import skia

co = Font.Cacheable("assets/ColdtypeObviously-VF.ttf")

def cut(mp=127, w=5):
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

colorMatrix = [
    0.5, 0.5, 0.5, 0, 0,
    0.5, 0.5, 0.5, 0, 0,
    0.5, 0.5, 0.5, 0, 0,
    0, 0, 0, 1, 0,
]

@renderable(bg=0, rstate=1)
def with_image(r, rstate):
    nxl, _ = LaunchControlXL(rstate.midi)

    dp = (StyledString("COLD",
        Style(co, 700, wdth=0.25, tu=50, r=1, ro=1))
        .pens()
        .align(r)
        .f(1)
        #.understroke(s=0, sw=20)
        .precompose(SkiaPen, r)
        .attr(skp=dict(
            ImageFilter=skia.BlurImageFilter.Make(nxl(20)*90, 15),
            #ColorFilter=skia.TableColorFilter.MakeARGB(ct, None, None, None),
        )))
    
    dps = (DATPenSet([
        #DATPen().rect(r).f(0),
        dp])
        .precompose(SkiaPen, r)
        .attr(skp=dict(
            #BlendMode=skia.BlendMode.kScreen,
            #ColorFilter=skia.ColorFilters.Matrix(colorMatrix)
            ColorFilter=skia.TableColorFilter.MakeARGB(cut(nxl(10)*255, 1), None, None, None),
            ImageFilter=skia.BlurImageFilter.Make(1, 1)
            )))
    
    return dps