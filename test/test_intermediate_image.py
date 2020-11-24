from coldtype import *
import coldtype.filtering as fl
import skia

co = Font.Cacheable("assets/ColdtypeObviously-VF.ttf")

@animation(bg=hsl(0.65, l=0.83), rstate=1, storyboard=[15], timeline=Timeline(30))
def render(f, rstate):
    p = f.a.progress(f.i, loops=1, easefn="qeio").e

    return (StyledString("COLDTYPE",
        Style(co, 700, wdth=(p)*0.1, tu=-85+(p*50), r=1, ro=1, rotate=10*p))
        .pens()
        .align(f.a.r)
        .f(1)
        .understroke(s=0, sw=30)
        .precompose(f.a.r)
        .attr(skp=dict(
            ImageFilter=skia.BlurImageFilter.Make(10, 10),
            ColorFilter=skia.LumaColorFilter.Make()
        ))
        .precompose(f.a.r)
        .attr(skp=dict(
            ColorFilter=fl.compose(
                fl.as_filter(fl.contrast_cut(200+p*30, 5)),
                fl.fill(hsl(0.9, l=0.5, s=0.7)),
            ))))