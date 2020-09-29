from coldtype import *
from coldtype.pens.skiapen import SkiaPathPen
from random import randint
import skia

mutator = Font("assets/MutatorSans.ttf")

#co = Font("assets/ColdtypeObviously.designspace")
tl = Timeline(60)

@animation(rect=(1200, 550), timeline=tl, storyboard=[0], bg=0.25, layers=["__default__", "circle"])
def render(f):
    t = tl.progress(f.i, loops=0, easefn="linear")
    l = tl.progress(f.i, loops=1, easefn="eeio")
    
    return DATPenSet([
        (StyledString("COLD",
            Style(mutator, 350, tu=-100-100*t.e, ro=1, r=1, rotate=15, wdth=0.25, wght=1))
            .pens()
            .align(f.a.r)
            .rotate(-5)
            .translate(0, 10)
            .f(0, 1, 0)
            .understroke(sw=30)
            .tag("__default__")),
        (DATPen()
            .oval(f.a.r.take(100, "mdy").square())
            .scale(1+t.e*8)
            .f(None)
            .s(Gradient.Horizontal(f.a.r, hsl(0.2), hsl(0.9)))
            .sw(50)
            .attr(skp=dict(
                AntiAlias=True,
                MaskFilter=skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 20.0)))
            .tag("circle"))])