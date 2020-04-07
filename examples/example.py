from coldtype import *
from coldtype.pens.datpen import warp_fn

font = Font("ç/ColdtypeObviously.designspace")

@renderable(rect=(1500, 300))
def coldtype(r):
    kp = kern_pairs={("L","D"):-5, ("T","Y"):-20, ("Y","P"):10,("P","E"):-100}
    style = Style(font, 650, fill="random", wdth=1, tu=-50, r=1, ro=1, kp=kp)
    pens = StyledString("COLDTYPE", style).fit(1250).pens().align(r)
    pens.pmap(lambda idx, p: p.f(complex(0, 0.25+idx/len(pens)*0.5), 0.55, 0.65).flatten(5).nonlinear_transform(warp_fn(mult=35)))
    return pens.understroke().rotate(5).scale(0.4)