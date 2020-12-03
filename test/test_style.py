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
