from coldtype.test import *

@test()
def clear(r):
    return DATPens([
        (DATPen()
            .oval(r)
            .f(hsl(0.3))),
        (DATPen()
            .rect(r.inset(50))
            .blendmode(skia.BlendMode.kClear)
            .f(hsl(0.8)))])

@test()
def overlay(r):
    return DATPens([
        (DATPen()
            .oval(r)
            .f(hsl(0.3))),
        (DATPen()
            .rect(r.inset(50))
            .blendmode(skia.BlendMode.kOverlay)
            .f(hsl(0.8)))])

@test()
def modulate(r):
    return DATPens([
        (DATPen()
            .oval(r)
            .f(hsl(0.3))),
        (DATPen()
            .rect(r.inset(50))
            .blendmode(skia.BlendMode.kModulate)
            .f(hsl(0.8)))])