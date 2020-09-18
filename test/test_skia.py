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

tl = Timeline(60)

@animation(rect=(1200, 550), timeline=tl, storyboard=[0, 15])
def render(f):
    r = f.a.r
    t = tl.progress(f.i, loops=2, easefn="eeio")
    spp = DATPen().oval(Rect(0, 0, 10, 6)).cast(SkiaPathPen, 6)

    print(f.i, t.e)

    skp = dict(
        AntiAlias=True,
        #PathEffect=skia.CornerPathEffect.Make(15.0),
        #PathEffect=skia.DiscretePathEffect.Make(10.0, 4.0),
        ImageFilter=skia.ImageFilters.DropShadow(5, 5, 10, 10, skia.Color4f(1, 1, 0, 1)),
        #PathEffect=skia.Path1DPathEffect.Make(spp.path, 20.0, 100.0, skia.Path1DPathEffect.kRotate_Style),
        #ImageFilter=skia.ImageFilters.Erode(5, 12),
        #ColorFilter=skia.ColorFilters.Matrix(colorMatrix),
        MaskFilter=skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 2.0),
        # PathEffect=skia.PathEffect.MakeCompose(
        #    skia.CornerPathEffect.Make(15),
        #    path_effect
        # ),
    )

    ss:DATPenSet = (StyledString("COLD",
        Style(co, 350, tu=-80, ro=1, r=1, rotate=15))
        .pens()
        .align(r)
        .rotate(-5)
        .translate(0, 10)
        .f(0.9, 0, 0.8)
        .pmap(lambda i, p: p.flatten(5))
        .attr(skp=skp)
        .understroke(sw=30)
        )
    
    #ss[2].attr(skp=skp)
    
    return ss