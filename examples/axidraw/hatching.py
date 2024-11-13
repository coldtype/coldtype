from coldtype import *
from coldtype.axidraw import *

co = Font.ColdtypeObviously()
script = Font.JBMono()

@axidrawing(flatten=50)
def test_draw(r):
    border = P(r.inset(50)).tag("border")
    
    letters = (StSt("COLD", co, 900, wdth=0.15, ro=1)
        .pen()
        .align(r)
        .tag("letters")
        .flatten(10))

    hatch_rs = r.inset(20).subdivide(150, "N")

    hatches = (P().enumerate(hatch_rs, lambda x:
            P(x.el) if x.i%2==0 else None)
        .pen()
        .intersection(letters.copy())
        .explode()
        .map(lambda _, p: P().line(p.ambit().es))
        .s(0, 0.25)
        .tag("hatches"))

    typ = (StSt("type", script, 500
        , ro=1
        , tu=-120
        , kp={"y.italic/p":-20})
        .align(r, ty=1)
        .translate(0, -20)
        .s(hsl(0.65))
        .tag("type"))
    
    return P(border, letters, typ, hatches)

numpad = {
    1: test_draw.draw("border"),
    2: test_draw.draw("letters"),
    3: test_draw.draw("type"),
    4: test_draw.draw("hatches"),
}
