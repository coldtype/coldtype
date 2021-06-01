from coldtype import *
from coldtype.fx.skia import phototype

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
        .ch(phototype(f.a.r, 10, 250)))
    return [
        (letter.copy()
            .potrace(f.a.r, ["-O", 1])
            .f(Gradient.Vertical(f.a.r, hsl(0.5), hsl(0.7))))]