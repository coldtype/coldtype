from coldtype import *

@renderable((540, 540), bg=1)
def circles(r):
    circle = (P().oval(r.inset(140))
        .fssw(-1, hsl(0.9, a=0.5), 6))
    
    return (P(
        circle,
        StSt("ABC", Font.MuSan(), 100, wght=0.5, wdth=0, tu=-90)
            .distribute_on_path(circle, baseline=1, apply_tangent=1)
            .f(hsl(0.7)),
        StSt("ABC", Font.MuSan(), 100, wght=0.5, wdth=0, tu=500)
            .distribute_on_path(circle, 0, apply_tangent=1, baseline=0)
            .f(hsl(0.3))
    ))