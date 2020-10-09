from coldtype import *
from coldtype.pens.dp_abbrev import *

@renderable()
def t1(r):
    return ß(
        oval(r.inset(100)),
        fill(hsl(random(), l=0.8)),
        rotate(45),
        flatten(10),
        roughen(45),
        smooth(),
        intersection(ß(rect(r.inset(100).offset(100, 200)))))