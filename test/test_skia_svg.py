from coldtype import *
import skia

co = Font("assets/ColdtypeObviously.designspace")
src = Path("test/renders/test_skia_svg_create_svg.svg")
print(src.exists())
#svg = skia.Image.MakeFromEncoded(skia.Data.MakeFromFileName(str(src)))

#@renderable(rect=(1000, 1000))
def create_svg(r):
    return (StyledString("COLD",
        Style(co, 1000, wdth=0))
        .pens()
        .align(r)
        .f(hsl(0.7, 0.6, 0.6)))

@renderable(rect=(1000, 1000))
def show_svg(r):
    return (DATPen()
        .oval(r)
        .f(hsl(0.5))
        #.attr(image=dict(src=src, opacity=0.35, rect=r))
        )