from coldtype import *

co = Font("assets/ColdtypeObviously.designspace")

img = Path("test/renders/test_skia_image_is_image.png")

#@renderable(rect=(250, 250))
def is_image(r):
    return DATPenSet([
        DATPen().oval(r).f(hsl(0.9)),
        (StyledString("COLDTYPE",
            Style(co, 100, tu=50, ro=1, r=1, rotate=15, wdth=0))
            .pens()
            .align(r)
            .rotate(-45)
            .translate(0, 10)
            .f(1))])

#@renderable(rect=(1000, 1000))
def uses_image(r):
    return DATPenSet([
        DATPen().oval(r.inset(10)).f(hsl(0.5)),
        DATPen().oval(r.inset(20)).f(None).attr(image=dict(src=img, opacity=0.35, rect=r))])
    
@renderable(rect=(500, 500))
def uses_shadow(r):
    return (DATPen()
        .rect(r.inset(100))
        .rotate(45)
        .attr(shadow=dict(clip=r.inset(100), alpha=0.75, radius=30))
        .f(hsl(0.75)))