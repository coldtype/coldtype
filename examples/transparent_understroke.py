from coldtype import *
from functools import partial

@renderable((1080, 680))
def understroke_cut(r):
    def cut(line, i, p):
        if i > 0:
            return p.difference(line[i-1].copy().outline(10, drawOuter=False))

    return (StSt("COLD\nTYPE", Font.ColdObvi(), 300, tu=-100, ro=1)
        .f(hsl(0.9))
        .map(lambda p: p.map(partial(cut, p)))
        .map(lambda p: p.track(50))
        .align(r))