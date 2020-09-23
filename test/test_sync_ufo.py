from coldtype import *

co1 = Font("assets/ColdtypeObviously_CompressedBlackItalic.ufo")
co2 = Font("assets/ColdtypeObviously.designspace")

@renderable()
def hello(r):
    return DATPenSet([
        (StyledString("COLD",
            Style(co1, 1000, wdth=1))
            .pens()
            .align(r)
            .f(hsl(0.5))),
        (StyledString("TYPE",
            Style(co2, 500, wdth=1))
            .pens()
            .align(r)
            .rotate(45)
            .f(hsl(0.95, a=0.25)))])