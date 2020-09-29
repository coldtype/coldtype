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
    0, 0, 0, 0, 0.2,
    0, 0, 0, 0, 0.5,
    0, 0, 0, 0, 1,
    0, 0, 0, 1, 0,
]

@animation(bg=hsl(0.65, l=0.3), rstate=1, storyboard=[15], timeline=Timeline(30))
def render(f, rstate):
    nxl, _ = LaunchControlXL(rstate.midi)
    p = f.a.progress(f.i, loops=1, easefn="qeio").e

    return (StyledString("COLDTYPE",
        Style(co, 700, wdth=(p)*0.1, tu=-85+(p*50), r=1, ro=1, rotate=10*p))
        .pens()
        .align(f.a.r)
        .f(1)
        .understroke(s=0, sw=20)
        .precompose(SkiaPen, f.a.r)
        .attr(skp=dict(
            ImageFilter=skia.BlurImageFilter.Make(10, 10),
            ColorFilter=skia.LumaColorFilter.Make()
        ))
        .precompose(SkiaPen, f.a.r)
        .attr(skp=dict(
            ColorFilter=skia.ColorFilters.Compose(
                skia.TableColorFilter.MakeARGB(cut(200+p*30, 3), None, None, None),
                hsl(0.95, l=0.7, s=0.7).skiaMatrix(),
            ),
            ImageFilter=skia.BlurImageFilter.Make(1, 1))))