from coldtype.test import *

def two_styles(r):
    return (DATPen()
        .oval(r.inset(50).square())
        .f(hsl(0.8))
        .attr("alt", fill=hsl(0.3)))

@test()
def no_style_set(r):
    return two_styles(r)

@test(style="alt")
def style_set(r):
    return two_styles(r)

def lattr_styles(r):
    return (DATPen()
        .oval(r.inset(50).square())
        .f(hsl(0.5)).s(hsl(0.7)).sw(5)
        .lattr("alt", lambda p: p.f(hsl(0.7)).s(hsl(0.5)).sw(15)))

@test()
def lattr_no_style(r):
    return lattr_styles(r)

@test(style="alt")
def lattr_style_set(r):
    return lattr_styles(r)