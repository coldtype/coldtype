from coldtype import *
from coldtype.axidraw import *

co = Font.ColdtypeObviously()
mis = Font.Find("Mistral")

@axidrawing()
def test_draw(r):
    border = P(r.inset(50)).tag("border")
    
    letters = (StSt("COLD", co, 900, wdth=0.15, ro=1)
        .pen()
        .align(r)
        .tag("letters"))

    hatch_rs = r.inset(20).subdivide(250, "N")
    hatches = (PS.Enumerate(hatch_rs, lambda x:
        P(x.el) if x.i%2==0 else None)
        .pen()
        .intersection(letters.copy())
        .explode()
        .map(lambda _,p: P().line(p.ambit().ecy))
        .tag("hatches"))

    typ = (StSt("type", mis, 650)
        .pen()
        .align(r, tv=1)
        .translate(0, -50)
        .removeOverlap()
        .tag("type"))
    
    return PS([
        border,
        hatches,
        typ
    ])

numpad = {
    1: test_draw.draw("border"),
    2: test_draw.draw("hatches"),
    3: test_draw.draw("type")
}