from coldtype import *
from coldtype.pens.skiapen import SkiaPathPen
from random import randint
import skia

co = Font("assets/ColdtypeObviously.designspace")

path_effect = skia.PathEffect.MakeSum(
    skia.DiscretePathEffect.Make(10.0, 5.0),
    skia.DiscretePathEffect.Make(10.0, 5.0, randint(0, 1200)))

tl = Timeline(60)

@animation(rect=(1200, 550), timeline=tl, storyboard=[0, 15], bg=0, layers=["__default__", "circle"])
def render(f):
    r = f.a.r
    t = tl.progress(f.i, loops=1, easefn="qeio")
    spp = DATPen().oval(Rect(0, 0, 5, 5)).cast(SkiaPathPen, 5)

    rd = math.radians(t.e*180)
    colorMatrix = [
        math.cos(rd), math.sin(rd), 0, 0, 0,
        -math.sin(rd), math.cos(rd), 0, 0, 0,
        0, 0, 1, 0, 0,
        0, 0, 0, 1, 0
    ]

    #noise = skia.PerlinNoiseShader.MakeFractalNoise(0.01, 0.01, 1, 5.0)
    #noise = skia.PerlinNoiseShader.MakeImprovedNoise(0.01, 0.01, 1, t.e)

    skp = dict(
        AntiAlias=True,
        #Shader=noise,
        #ImageFilter=skia.ImageFilters.Magnifier(skia.Rect(0, 0, t.e*200, 50), 50.0),
        #PathEffect=skia.CornerPathEffect.Make(15.0),
        #PathEffect=skia.DiscretePathEffect.Make(10.0, 4.0),
        #ImageFilter=skia.ImageFilters.DropShadow(5, 5, 10, 10, skia.Color4f(1, 1, 0, 1)),
        #PathEffect=skia.Path1DPathEffect.Make(spp.path, 8.0, t.e*100, skia.Path1DPathEffect.kRotate_Style),
        #ImageFilter=skia.ImageFilters.Erode(5, 12),
        ColorFilter=skia.ColorFilters.Matrix(colorMatrix),
        #MaskFilter=skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 5.0),
        # PathEffect=skia.PathEffect.MakeCompose(
        #    skia.CornerPathEffect.Make(15),
        #    path_effect
        # ),
    )

    ss:DATPenSet = (StyledString("COLD",
        Style(co, 350, tu=-100, ro=1, r=1, rotate=15))
        .pens()
        .align(r)
        .rotate(-5)
        .translate(0, 10)
        #.f(1)
        .f(Gradient.Horizontal(f.a.r, hsl(0.5, s=0.7), hsl(0.9, s=0.7)))
        .pmap(lambda i, p: p.flatten(5))
        .attr(skp=skp)
        .understroke(sw=30, s=Gradient.Horizontal(f.a.r, hsl(0.9, s=0.9), hsl(0.5, s=0.9)))
        .tag("__default__"))
    
    circle = (DATPen()
        .oval(f.a.r.inset(100).square())
        .translate(-500+t.e*1000, 0)
        .f(1)
        .attr(skp=dict(
            AntiAlias=True,
            MaskFilter=skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 50.0),
        ))
        .tag("circle"))
    
    return DATPenSet([ss, circle])