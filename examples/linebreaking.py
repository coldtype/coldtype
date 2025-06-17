from coldtype import *

txt = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Pellentesque at aliquet neque, non bibendum nisi. Mauris quis ligula felis."

@renderable(bg=1)
def scratch(r):
    ri = r.inset(50)
    return (StSt(txt, Font.JBMono(), 70)
        .wordPens()
        .linebreak(ri.w)
        .stack("100%")
        .align(ri)
        .f(0))

@renderable(bg=1)
def heterogenous(r):
    ri = r.inset(50)
    a = StSt("Hello", Font.JBMono(), 70, wght=1)
    b = StSt("TYPE", Font.ColdObvi(), 70, wght=1)
    c = StSt("WORLD", Font.MuSan(), 70, wght=1)
    return (P(a, b, c)
        .spread(40)
        .linebreak(500)
        .stack(20)
        .align(ri))