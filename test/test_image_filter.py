from coldtype import *
from coldtype.midi.controllers import LaunchControlXL
import skia

def hide(a):
    return DATPen()


ct = bytearray(256)
for i in range(256):
    x = (i - 96) * 255 // 64
    ct[i] = min(255, max(0, x))
    #print(x, ct[i])


def filter(rstate) -> skia.Paint:
    nxl, _ = LaunchControlXL(rstate.midi)

    scale = nxl(10)
    translate = (-.5 * scale + .5)

    colorMatrix = [
        1, 0, 0, scale, 0,
        0, 1, 0, scale, 0,
        0, 0, 1, scale, 0,
        0, 0, 0, scale, nxl(13),
    ]

    matrix = skia.Matrix()
    matrix.setScale(1, 1)
    b = nxl(23)*10
    return skia.Paint(dict(
        AntiAlias=True,
        #ColorFilter=skia.ColorFilters.Matrix(colorMatrix),
        ColorFilter=skia.TableColorFilter.MakeARGB(None, None, ct, None),
        #ImageFilter=skia.BlurImageFilter.Make(b, b)
        ))

obv = Font.Cacheable("~/Type/fonts/fonts/ObviouslyVariable.ttf")

@renderable(rstate=1, filter=filter)
def vector(r, rstate):
    nxl, _ = LaunchControlXL(rstate.midi)
    return [
        (DATPen().oval(r)),
        (StyledString("COLD",
            Style(obv, 500, wdth=0.25, wght=nxl(20), tu=-100, r=1, ro=1))
            .pens()
            .align(r)
            .f(hsl(0.8))
            .understroke(sw=30)
            .attr(skp=dict(
                AntiAlias=True,
                BlendMode=skia.BlendMode.kScreen,
                MaskFilter=skia.MaskFilter.MakeBlur(
                    skia.kNormal_BlurStyle, nxl(11)*50.0)))),
        (StyledString("TYPE",
            Style(obv, 500, wdth=0.25, wght=1-nxl(20), tu=-150, r=1, ro=1))
            .pens()
            .align(r)
            .rotate(nxl(30)*180))
            .f(hsl(0.2, a=nxl(40)))
            .understroke(sw=100)
            .attr(skp=dict(
                AntiAlias=True,
                MaskFilter=skia.MaskFilter.MakeBlur(
                    skia.kNormal_BlurStyle, 5
                )))]