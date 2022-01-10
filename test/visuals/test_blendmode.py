from coldtype.test import *

@test()
def clear(r):
    return [(ß().oval(r).f(hsl(0.3))),
        (ß(r.inset(50)).blendmode(BlendMode.Clear).f(hsl(0.8)))]

@test()
def overlay(r):
    return [(ß().oval(r).f(hsl(0.3))),
        (ß(r.inset(50)).blendmode(BlendMode.Overlay).f(hsl(0.8)))]

@test()
def modulate(r):
    return [(ß().oval(r).f(hsl(0.3))),
        (ß(r.inset(50)).blendmode(BlendMode.Modulate).f(hsl(0.8)))]