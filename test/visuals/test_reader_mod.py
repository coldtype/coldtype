from coldtype.test import *

@test((1000, 350))
def test_xstretch(r):
    st = Style.StretchX(20, debug=1,
        A=(200, 230),
        B=(1500, 190),
        C=(200, 290))
    style = Style(mutator, 500, mods=st, wght=0.25)
    return (StyledString("ABC", style)
        .pen()
        .align(r)
        .scale(0.5)
        .f(hsl(0.2, a=0.1))
        .s(hsl(0.5))
        .sw(2))

@test((1000, 350))
def test_xstretch_slnt(r):
    st = Style.StretchX(20, debug=1,
        L=(500, (400, 750/2), -14),
        O=(1000, (385, 750/2), -14))
    return (StSt("LOL", co, 500, mods=st)
        .align(r)
        .scale(0.5)
        .fssw(hsl(0.2, a=0.1), hsl(0.5), 2))

@test((1000, 400))
def test_ystretch(r):   
    st = Style.StretchY(20, debug=1, E=(500, 258))
    style = Style(mutator, 300, mods=st, wght=0.5)
    return (StyledString("TYPE", style)
        .pen()
        .align(r, tx=1, ty=1)
        .f(hsl(0.2, a=0.1))
        .s(hsl(0.5))
        .sw(2))

@test((1000, 400))
def test_ystretch_slnt(r):
    st = Style.StretchY(20, debug=1,
        E=(500, (258, 750/2), 35))
    style = Style(co, 300, mods=st, wght=0.5)
    return (StyledString("TYPE", style)
        .pen()
        .align(r, tx=1, ty=1)
        .f(hsl(0.2, a=0.1))
        .s(hsl(0.5))
        .sw(2)
        )