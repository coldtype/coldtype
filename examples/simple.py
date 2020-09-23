from coldtype import *

@renderable((1580, 350))
def render(r):
    c1 = hsl(0.65, 0.7)
    c2 = hsl(0.53, 0.6)

    return DATPenSet([
        (DATPen()
            .rect(r.inset(10))
            .outline(10)
            .f(Gradient.Horizontal(r,
                c2.lighter(0.3),
                c1.lighter(0.3)))),
        (StyledString("COLDTYPE",
            Style("assets/ColdtypeObviously-VF.ttf", 250,
                wdth=1, tu=-170, r=1, rotate=15,
                kp={"P/E":-150, "T/Y":-50}))
            .pens()
            .align(r)
            .f(Gradient.Horizontal(r, c1, c2))
            .understroke(s=1, sw=5))
            .translate(0, 5)])