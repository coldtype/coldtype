from coldtype import *
from coldtype.fx.skia import phototype
from random import randint

# a variation on https://github.com/djrrb/Python-for-Visual-Designers-Fall-2023/blob/main/session-4/challenges/snakes.py

segmentLength = 200
handleLength = segmentLength*1

wiggles = random_series(-400, 400, 1, mod=int, spread=200)

def build_snake(r, seed):
    snake = P()
    snake.moveTo((0, 0))
    prevX = 0
    prevY = 0
    for idx, y in enumerate(range(segmentLength, r.h+10, segmentLength)):
        x = wiggles[(idx+2)+seed*10]
        snake.curveTo(
            (prevX, prevY+handleLength),
            (x, y-handleLength),
            (x, y))
        prevX = x
        prevY = y
    return snake.endPath()

@renderable(Rect(1000, 1000), bg=0)
def snakes(r):
    return (P().enumerate(range(0, 10), lambda x:       
        build_snake(r, x.el)
            .t(x.el*20, 0)
            .outline(2)
            .f(1)
            .scale(1, 1.2))
        .align(r, "N")
        .ch(phototype(r, 3, 110, 17)))