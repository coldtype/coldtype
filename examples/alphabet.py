from coldtype import *

glyphs = "abcdefghijklmnopqrstuvwxyz0123456789!.,"

@renderable("letter", bg=1, fmt="pdf")
def alphabet(r):
    s = Scaffold(r.inset(40)).numeric_grid(6, 7)
    return (P().enumerate(glyphs, lambda x:
        StSt(x.el, Font.JBMono(), 60, wght=1)
            .align(s[x.i])
            .f(0)))
