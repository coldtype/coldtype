from coldtype import *
from coldtype.axidraw import *

@axidrawing()
def sheet(r):
    s = Scaffold(r.inset(20)).grid(5, 5)
    
    cells = (s.borders().tag("cells"))
    
    letters = (P().enumerate(s, lambda x:
        StSt("A", Font.MutatorSans(), 150, wght=x.e)
            .align(x.el)
            .removeOverlap())
        .tag("letters"))
    
    return P(
        P(r.inset(20)).tag("border"),
        cells,
        letters)

numpad = {
    1: sheet.draw("border"),
    2: sheet.draw("cells"),
    3: sheet.draw("letters"),
}