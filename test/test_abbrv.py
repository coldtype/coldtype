from coldtype import *
from coldtype.pens.abbr import *

@renderable()
def test_pen(r):
    return pen(
        oval(r.inset(100)),
        fill(hsl(0.5, l=0.8)),
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
        style(500, wdth=0.25, rotate=20, ro=1, tu=100),
        style(1000, wdth=0, rotate=0, ro=1, tu=-100, r=1),
        fsw(None, hsl(0.7, l=0.5), 10),
        f(hsl(0.9, l=0.8)),
        align(r))


c1 = hsl(0.0, 0.7)
c2 = hsl(0.23, 0.6)

@renderable((1080, 350))
def render(r):
    return pens(
        pen(rect(r.inset(10)),
            outline(10),
            f(G.H(r, c2.lighter(0.3), c1.lighter(0.3)))),
        pens(text("ABBRVTN"),
            font("assets/MutatorSans.ttf"),
            style(250,
                wdth=0, wght=1, tu=-270, r=1, rotate=15,
                kp={"P/E":-150, "T/Y":-50}),
            align(r),
            f(G.H(r, c1, c2)),
            understroke(s=1, sw=5),
            s_translate(0, 20)))