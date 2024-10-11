from coldtype import *
from coldtype.fx.skia import phototype
from random import randint

# a variation on https://github.com/djrrb/Python-for-Visual-Designers-Fall-2023/blob/main/session-4/challenges/snakes.py

r = Rect(1000, 1000)
segmentLength = r.h/5
handleLength = segmentLength*1
total = 5

rxs = random_series(-400, 400, 0, mod=int, spread=200)

def build_snake(seed):
    snake = P()
    snake.moveTo((0, 0))
    prevX = 0
    prevY = 0
    for idx in range(0, total):
        y = prevY + segmentLength
        if idx < total-1:
            x = rxs[(idx+2)+seed*10]
        else:
            x = 0
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
        build_snake(x.el)
            .t(x.el*20, 0)
            .outline(2)
            .f(1))
        .align(r)
        .ch(phototype(r.inset(-10), 3, 110, 17))
        )