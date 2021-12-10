from coldtype import *

@animation((540, 540), timeline=30)
def hsl_interp(f):
    return (P().oval(f.a.r.inset(100))
        .f(hsl(0.5).hsl_interp(f.e("qeio"), hsl(0.1))))

@animation((540, 540), timeline=120)
def rgb_interp(f):
    return (P(f.a.r.inset(100))
        .f(hsl(0.5).rgb_interp(f.e("eeio"), hsl(0.8))))