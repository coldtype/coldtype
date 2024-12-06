from coldtype import *
from coldtype.fx.skia import phototype, temptone, shake

# a variation on https://github.com/djrrb/Python-for-Visual-Designers-Fall-2023/blob/main/session-4/challenges/snakes.py

r = Rect(1000, 1000)
s = Scaffold(r).numeric_grid(1, 8)

rxs = random_series(-(d:=r.w/2-100), d, 0, mod=int, spread=200)

def build_snake(seed):
    snake = P()
    snake.moveTo((0, 0))
    prevX = 0
    prevY = 0
    for idx, x in enumerate(s):
        y = prevY + s[0].r.h
        if idx < len(s)-1:
            x = rxs[(idx+2)+seed*10]
        else:
            x = 0
        snake.curveTo(
            (prevX, prevY+s[0].r.h),
            (x, y-s[0].r.h),
            (x, y))
        prevX = x
        prevY = y
    return snake.endPath()

@animation(r, bg=0, tl=Timeline(60, 10))
def snakes(f):
    return (P().enumerate(range(0, 7), lambda x:
        build_snake(x.el)
            .t(x.el*20, 0)
            .fssw(-1, 1, 5)
            .ch(shake(4, 2, seed=f.i)))
        .align(f.a.r)
        .ch(phototype(f.a.r.inset(-10), 4, 123, 17))
        .postprocess(lambda res: res.ch(temptone(0.70, 0.10))))