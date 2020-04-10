from coldtype import *
from functools import partial
from random import Random


co = Font("ç/ColdtypeObviously.designspace")

def add_grid(render, result):
    return DATPenSet([
        DATPenSet(result),
        DATPen().gridlines(render.rect).s(0, 0.1)
    ])

test = partial(renderable, rect=(1000, 500), bg=1, postfn=add_grid)