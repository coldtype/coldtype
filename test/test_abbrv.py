from coldtype import *
from coldtype.pens.abbr import *

@renderable()
def test_pen(r):
    return pen(
        oval(r.inset(100)),
        fill(hsl(random(), l=0.8)),
        rotate(45),
        flatten(10),
        roughen(145),
        smooth(),
        intersection(pen(
            rect(r.inset(100)),
            translate(100, 200))))

@renderable()
def test_pens(r):
    return pens(
        text("TYPE"),
        font("assets/ColdtypeObviously-VF.ttf"),
        #ƒ("assets/MutatorSans.ttf"),
        style(500, wdth=0.25, rotate=20, ro=1, tu=100),
        #ƒƒ(1000, wdth=0, rotate=0, ro=1, tu=-300),
        fsw(None, hsl(random(), l=0.5), 10),
        align(r))