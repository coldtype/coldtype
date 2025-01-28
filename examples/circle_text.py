from coldtype import *

@renderable((540, 540), bg=1)
def circles(r):
    circle = (P().oval(r.inset(140))
        .fssw(-1, hsl(0.9, a=0.5), 6))
    
    return (P(
        circle,
        StSt("ABC", Font.MuSan(), 100, wght=0.5, wdth=0, tu=340)
            .distribute_on_path(circle.copy().scale(1.1), baseline=1)
            .f(hsl(0.7)),
        StSt("ABC", Font.MuSan(), 100, wght=0.5, wdth=0, tu=500)
            .distribute_on_path(circle.copy().scale(0.9).rotate(-180), 0, baseline=0)
            .f(hsl(0.3))))