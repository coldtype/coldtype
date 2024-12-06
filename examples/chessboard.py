from coldtype import *
from string import ascii_uppercase

fill = hsl(0.38, 0.7, 0.7)

chessfont = Font.LibraryFind(r"AppleSymbols")

@renderable(bg=1)
def board(r):
    def cell(x):
        if x.el.data("checker"):
            return P().oval(x.el.r).f(fill)
        else:
            return P().rect(x.el.r.inset(1)).f(fill)

    s = Scaffold(r.inset(100)).numeric_grid(8, gap=20)

    board = P().enumerate(s.cells(), cell)
    borders = s.borders().ssw(hsl(0.6, 0.6, 0.7), 2)

    style = Style(Font.JBMono(), 30, wght=1)

    labels = (P(
        P().enumerate(s.rows()[0], lambda x:
            StSt(ascii_uppercase[x.i], style)
                .align(x.el.r)
                .f(0)
                .t(0, x.el.r.h-10)
                .rotate(180)),
        P().enumerate(s.rows()[-1], lambda x:
            StSt(ascii_uppercase[x.i], style)
                .align(x.el.r)
                .f(0)
                .t(0, -x.el.r.h+10)),
        P().enumerate(s.cols()[0], lambda x:
            StSt(str(8-x.i), style)
                .align(x.el.r)
                .f(0)
                .t(-x.el.r.w+10, 0)),
        P().enumerate(s.cols()[-1], lambda x:
            StSt(str(8-x.i), style)
                .align(x.el.r)
                .f(0)
                .t(x.el.r.w-10, 0)
                .rotate(180))))
    
    rows = s.rows()
    
    player1 = (P().enumerate("♖♘♗♕♔♗♘♖", lambda x:
        StSt(x.el, chessfont, 50)
            .align(rows[0][x.i])
            .rotate(180)
            .f(0)))
    
    pawns1 = (StSt("♙", chessfont, 50).f(0)
        .pen()
        .unframe()
        .rotate(180)
        .replicate(rows[1]))
    
    player2 = (P().enumerate("♜♞♝♛♚♝♞♜", lambda x:
        StSt(x.el, chessfont, 50)
            .align(rows[-1][x.i])
            .f(0)))
    
    pawns2 = (StSt("♟", chessfont, 50).f(0)
        .pen()
        .unframe()
        .replicate(rows[-2]))

    return P(borders, board, labels, player1, pawns1, player2, pawns2)