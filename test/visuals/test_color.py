from coldtype import *

tl = Timeline(30)

@animation(timeline=tl)
def hsl_interp(f):
    p = f.a.progress(f.i, loops=1, easefn="qeio").e
    return (DATPen()
        .oval(f.a.r.inset(100))
        .f(hsl(0.5).hsl_interp(p, hsl(0.1))))


@animation()
def rgb_interp(f):
    p = f.a.progress(f.i, easefn="qeio").e
    return (DATPen()
        .rect(f.a.r.inset(100))
        .f(hsl(0.5).rgb_interp(p, hsl(0.8))))