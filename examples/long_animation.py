from coldtype import *

@animation(timeline=Timeline(600))
def stub(f):
    return (DATPen()
        .oval(f.a.r.inset(50))
        .f(hsl(f.a.progress(f.i).e)))
