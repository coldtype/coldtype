from coldtype import *
from functools import partial
from random import Random


co = Font("assets/ColdtypeObviously.designspace")
mutator = Font("assets/MutatorSans.ttf")

Style.RegisterShorthandPrefix("≈", "~/Type/fonts/fonts")


def add_grid(render, result):
    return DATPenSet([
        DATPenSet(result),
        DATPen().gridlines(render.rect).s(0, 0.1)
    ])


def show_error(r, txt):
    return StyledString(txt.upper(), Style(mutator, 100)).pen().align(r)


class test(renderable):
    def __init__(self, rect=(1000, 500), bg=1, postfn=add_grid, **kwargs):
        super().__init__(rect=rect, bg=bg, postfn=postfn, **kwargs)