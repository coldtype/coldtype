from coldtype import *
from coldtype.abbr import *

@renderable()
def test_pen(r):
    return (pen()
        + oval(r.inset(100))
        + fill(hsl(0.5, l=0.5))
        + flatten(10)
        + roughen(145)
        + smooth()
        + intersection(pen()
            + rect(r.inset(100))
            + translate(100, 200))
        + align(r)).realize()

@renderable((1080, 500))
def test_pens(r):
    return (pens()
        + text("TYPE")
        + font("assets/ColdtypeObviously-VF.ttf")
        + style(500, wdth=0.25, rotate=-20, ro=1, tu=100)
        + f(hsl(0.9, l=0.8))
        + align(r)).realize()


@renderable((1080, 350))
def render(r):
    c1 = hsl(random(), 0.7)
    c2 = hsl(0.23, 0.6)
    return ((pen()
            + rect(r.inset(10))
            + outline(10)
            + f(G.H(r, c2.lighter(0.2), c1.lighter(0.1))))
        + (pens()
            + text("ABBRVTN")
            + font("assets/MutatorSans.ttf")
            + style(250,
                wdth=0, wght=1, tu=-270, r=1, rotate=15,
                kp={"P/E":-150, "T/Y":-50})
            + align(r)
            + f(G.H(r, c1, c2))
            + understroke(s=1, sw=5)
            - rotate(20)))