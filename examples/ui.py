from coldtype import *

"""
Proof-of-concept for @ui interface
"""

@ui(timeline=Timeline(60, 60), bg=0)
def ui1(u):
    mouse = (P()
        .oval(u.m.rect(50, 50))
        .f(1))
    
    box = ((ß:=StSt("{:02d}".format(u.i),
            Font.RecursiveMono(),
            font_size=300))
        .align(u.r, th=0)
        .cond(u.m.inside(ß.ambit()),
            λ.f(hsl(0.9)),
            λ.f(1)))
    
    return PS([mouse, box])

