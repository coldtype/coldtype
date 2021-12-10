from coldtype import *
from coldtype.fx.skia import phototype, potrace

co = Font.Cacheable("assets/ColdtypeObviously-VF.ttf")

@animation(bg=bw(0), timeline=Timeline(30))
def render(f):
    raw = (StSt("COLD", co, 700
        , wdth=0.5
        , tu=-155*f.e()
        , r=1
        , ro=1
        , rotate=10)
        .align(f.a.r)
        .f(1))
    
    letter = (raw.copy()
        .ch(phototype(f.a.r, 15, 200)))
    
    return [
        (letter.copy()
            .ch(potrace(f.a.r, ["-O", 1]))
            .f(Gradient.Vertical(f.a.r, hsl(0.5), hsl(0.7))))]