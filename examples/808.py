from coldtype import *

hyperscrypt = Font("ç/NumericHyperScrypt.ufo")

@animation(duration=60, bg=0)
def render(f):
    pens = StyledString("808", Style(hyperscrypt, 400)).pens().align(f.a.r)

    # nudge the upper piece between the 8 and 0
    m2 = lambda c: c.translate(0, 50)
    pens[0].mod_contour(0, m2)
    pens[1].mod_contour(0, m2)

    # nudge the lower piece between the 0 and 8
    m1 = lambda c: c.translate(0, -50)
    pens[1].mod_contour(3, m1)
    pens[2].mod_contour(3, m1)

    # rotate the center
    r1 = lambda c: c.rotate(f.a.progress(f.i).e*360, point=f.a.r.point("C"))
    pens[1].mod_contour(4, r1)
    pens[1].mod_contour(5, r1)

    h = f.a.progress(f.i).e
    return [
        DATPen().rect(f.a.r).f(complex(0, h), 0.25, 0.25),
        pens.pen().removeOverlap().f(complex(0, h), 0.65, 0.65)
    ]