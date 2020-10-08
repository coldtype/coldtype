from coldtype import *
import coldtype.filtering as fl
import skia

co = Font.Cacheable("assets/ColdtypeObviously-VF.ttf")

@animation(bg=bw(0), rstate=1, storyboard=[0], timeline=Timeline(30))
def render(f, rstate):
    raw = (StyledString("COLD",
        Style(co, 700, wdth=0.5, tu=-85, r=1, ro=1, rotate=10))
        .pens()
        .align(f.a.r)
        .f(1)
        .understroke(s=0, sw=30))
    letter = (raw
        .copy()
        .precompose(SkiaPen, f.a.r)
        .attr(skp=dict(
            ImageFilter=skia.BlurImageFilter.Make(10, 10),
            ColorFilter=skia.LumaColorFilter.Make()
        ))
        .precompose(SkiaPen, f.a.r)
        .attr(skp=dict(
            ColorFilter=fl.compose(
                fl.as_filter(fl.contrast_cut(250, 3)),
                #fl.fill(hsl(0.75, l=0.5, s=0.7)),
                fl.fill(bw(1)),
            ),
            #ImageFilter=skia.BlurImageFilter.Make(1, 1)
            )))
    return [
        #raw,
        letter.copy(),
        letter.copy().potrace(SkiaPen, f.a.r, "-O", 1).f(hsl(0.85, l=0.6, a=0.8)).scale(1.05)
    ]