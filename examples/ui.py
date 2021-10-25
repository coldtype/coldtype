from coldtype import *

"""
Proof-of-concept for @ui interface
"""

@ui(timeline=Timeline(60, 60), bg=0)
def ui1(u):
    c = (P()
        .oval(u.c.rect(30, 30))
        .fssw(-1, 1, 4))
    
    ch = PS.Enumerate(u.ch, lambda x:
        (P().oval(x.el.rect(20, 20))
            .fssw(-1, hsl(0.6, 1), 2)))
    
    box = ((ß:=StSt("{:02d}".format(u.i),
            Font.RecursiveMono(),
            font_size=300))
        .align(u.r, th=0)
        .cond(u.c.inside(ß.ambit()),
            λ.f(hsl(0.9)),
            λ.f(1)))
    
    return PS([ch, c, box])

