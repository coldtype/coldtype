from coldtype.test import *

@test()
def clip1(r):
    return DATPen().oval(r.square()) + (DATPen()
        .oval(r.inset(50))
        .f(hsl(0.9, a=1))
        #.f(1, 0.5)
        .f(None)
        .s(0).sw(5)
        .shadow(radius=50, color=hsl(0.3, 1), clip=(DATPen()
            .rect(r.inset(50))
            .difference(DATPen().oval(r.inset(50))))))