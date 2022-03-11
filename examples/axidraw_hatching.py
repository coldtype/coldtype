from coldtype import *
from coldtype.axidraw import *

co = Font.ColdtypeObviously()
script = Font.RecursiveMono()

@axidrawing(flatten=50)
def test_draw(r):
    border = P(r.inset(50)).tag("border")
    
    letters = (StSt("COLD", co, 900, wdth=0.15, ro=1)
        .pen()
        .align(r)
        .tag("letters"))

    hatch_rs = r.inset(20).subdivide(250, "N")
    hatches = (P().enumerate(hatch_rs, lambda x:
            P(x.el) if x.i%2==0 else None)
        .pen()
        .intersection(letters.copy())
        .explode()
        .map(lambda _, p: P().line(p.ambit().es))
        .tag("hatches"))

    typ = (StSt("type", script, 500
        , tu=-120
        , kp={"y.italic/p":-20})
        .align(r, tv=1)
        .translate(0, -20)
        .pmap(lambda p: p.removeOverlap())
        .tag("type"))
    
    return P(border, letters, typ)

numpad = {
    1: test_draw.draw("border"),
    2: test_draw.draw("letters"),
    3: test_draw.draw("type")
}
