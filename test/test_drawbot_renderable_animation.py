from coldtype import *
from drawBot import *
import re


co = Font("assets/ColdtypeObviously.designspace")
tl = Timeline(50, storyboard=[0, 22])


@drawbot_animation(rect=(900, 500), svg_preview=0, bg=0.5, timeline=tl)
def db_script_test(f):
    e = f.a.progress(f.i, loops=1, easefn="eeio").e

    def pco(d, tolerance=0.05):
        x1, y1 = ((1-d)-tolerance, 0)
        x2, y2 = ((1-d)+tolerance, 1)
        c = (x1**3 * y2 - x2**3 * y1)/(x1**3 * x2 - x1 * x2**3)
        a = (y2 - c * x2) / x2**3
        return [0, c, 0, a]

    (StyledString("COLDTYPE",
        Style(co, 150, tu=100+-730*e, ro=1, r=1))
        .pens()
        .align(f.a.r)
        .rotate(15*(1-e))
        .skew(e*0.5)
        .filmjitter(e, speed=(20, 30), scale=(3, 4))
        .f(hsl(e, s=1, l=1-e*0.35))
        .understroke(sw=20)
        .scale(1-1*e*0.5)
        .db_drawPath(f.a.r, [ # TODO autogenerate signatures to make these autocomplete-able?
            ["gaussianBlur", {"radius":3+20*e}],
            #["colorPolynomial", {"alphaCoefficients":pco(0.25, 0.1)}]
        ]))