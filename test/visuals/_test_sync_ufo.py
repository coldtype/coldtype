from coldtype import *

co1 = Font("assets/ColdtypeObviously_CompressedBlackItalic.ufo")
co2 = Font("assets/ColdtypeObviously.designspace")

@renderable()
def hello(r):
    return DATPens([
        (StyledString("COLD",
            Style(co1, 1000, wdth=1))
            .pens()
            .align(r)
            .f(hsl(random()))),
        (StyledString("TYPE",
            Style(co2, 500, wdth=1))
            .pens()
            .align(r)
            .rotate(45)
            .f(hsl(random(), a=0.25)))])