from coldtype import *
from coldtype.pens.skiapen import SkiaPathPen
from random import randint
import skia

co = Font("assets/ColdtypeObviously.designspace")

path_effect = skia.PathEffect.MakeSum(
    skia.DiscretePathEffect.Make(10.0, 5.0),
    skia.DiscretePathEffect.Make(10.0, 5.0, randint(0, 1200)))

colorMatrix = [
    0, 1, 0, 0, 0,
    1, 1, 0, 0, 0,
    1, 1, 0, 0.5, 0,
    0, 0, 0, 0.5, 0
]


@renderable(rect=(1200, 550))
def filters(r):
    spp = DATPen().oval(Rect(0, 0, 10, 6)).cast(SkiaPathPen, 6)

    skp = dict(
        AntiAlias=True,
        #PathEffect=skia.CornerPathEffect.Make(15.0),
        #PathEffect=skia.DiscretePathEffect.Make(10.0, 4.0),
        #ImageFilter=skia.ImageFilters.DropShadow(0, 0, 15, 15, skia.ColorBLACK),
        #PathEffect=skia.Path1DPathEffect.Make(spp.path, 20.0, 100.0, skia.Path1DPathEffect.kRotate_Style),
        ImageFilter=skia.ImageFilters.Dilate(10, 10),
        #ColorFilter=skia.ColorFilters.Matrix(colorMatrix),
        #MaskFilter=skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 5.0),
        PathEffect=skia.PathEffect.MakeCompose(
            skia.CornerPathEffect.Make(1),
            path_effect
        ),
    )

    ss:DATPenSet = (StyledString("COLD",
        Style(co, 350, tu=-50, ro=1, r=1, rotate=30))
        .pens()
        .align(r)
        .rotate(-5)
        .translate(0, 10)
        .f(hsl(0.93, l=0.8))
        .pmap(lambda i, p: p.flatten(10))
        .attr(skp=skp)
        .understroke(sw=30)
        )
    
    #ss[2].attr(skp=skp)
    
    return ss