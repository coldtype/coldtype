from coldtype import *
import coldtype.filtering as fl
import skia

co = Font.Cacheable("assets/ColdtypeObviously-VF.ttf")

@animation(bg=bw(0), storyboard=[0], timeline=Timeline(30))
def render(f):
    raw = (StyledString("COLD",
        Style(co, 700, wdth=0.5, tu=-155*f.a.progress(f.i).e, r=1, ro=1, rotate=10))
        .pens()
        .align(f.a.r)
        .f(1))
    letter = (raw
        .copy()
        .precompose(f.a.r)
        .attr(skp=dict(
            ImageFilter=skia.BlurImageFilter.Make(10, 10),
            ColorFilter=skia.LumaColorFilter.Make()
        ))
        .precompose(f.a.r)
        .attr(skp=dict(
            ColorFilter=fl.compose(
                fl.as_filter(fl.contrast_cut(250, 3)),
                fl.fill(bw(1)),
            ))))
    return [
        (letter.copy()
            .potrace(f.a.r, ["-O", 1])
            .f(Gradient.Vertical(f.a.r, hsl(0.5), hsl(0.7))))]