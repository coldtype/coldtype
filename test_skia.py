from coldtype import *

tl = Timeline(26, fps=18)

@animation(rect=(540, 540), timeline=tl, bg=1)
def render(f):
    letter = StSt("B", Font.MuSan(), 500).pen().removeOverlap().align(f.a.r)
    print(letter._val.value)
    return letter
    #return P().oval(f.a.r.inset(100)).f(hsl(0.65)) + letter