from coldtype import *
from string import ascii_uppercase

@renderable(bg=1)
def board(r):
    def cell(x):
        if x.el.data("ch"):
            return P().oval(x.el.r).f(hsl(0.07, 0.80, 0.6))
        else:
            return P().rect(x.el.r.inset(1)).f(hsl(0.38, 0.7, 0.6))

    s = Scaffold(r.inset(100)).labeled_grid(8, 8, 14, 14)

    board = P().enumerate(s.cells(), cell)
    borders = s.borders().ssw(hsl(0.6, 0.6, 0.7), 2)

    labels = P().enumerate(s.cells().filter(lambda x: x.tag().startswith("h")), lambda x: StSt(ascii_uppercase[x.i], Font.JBMono(), 30, wght=1).align(x.el.r).f(0).t(0, -x.el.r.h+10))

    labels2 = P().enumerate(s.cells().filter(lambda x: x.tag().endswith("0")), lambda x: StSt(str(x.i), Font.JBMono(), 30, wght=1).align(x.el.r).f(0).t(-x.el.r.w+10, 0))

    return P(borders, board, labels, labels2)