from coldtype import *
from coldtype.pens.skiapen import SkiaPathPen
from random import randint
import skia

co = Font("assets/ColdtypeObviously.designspace")
tl = Timeline(60)

@animation(rect=(1200, 550), timeline=tl, storyboard=[5], bg=0.5, layers=["__default__", "circle"])
def render(f):
    t = tl.progress(f.i, loops=0, easefn="linear")
    l = tl.progress(f.i, loops=1, easefn="eeio")
    
    return DATPenSet([
        (StyledString("COLDTYPE",
            Style(co, 350, tu=-100, ro=1, r=1, rotate=15, wdth=0.25))
            .pens()
            .align(f.a.r)
            .rotate(-5)
            .translate(0, 10)
            .f(1, 1, 0)
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
                MaskFilter=skia.MaskFilter.MakeBlur(
                    skia.kNormal_BlurStyle, 20.0)))
            .tag("circle"))])