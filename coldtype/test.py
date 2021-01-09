from coldtype import *
from functools import partial
from random import Random
from pprint import pprint


co = Font.Cacheable("assets/ColdtypeObviously-VF.ttf")
mutator = Font.Cacheable("assets/MutatorSans.ttf")
recmono = Font.Cacheable("assets/RecMono-CasualItalic.ttf")

Style.RegisterShorthandPrefix("≈", "~/Type/fonts/fonts")


def add_grid(render, result):
    return DATPens([
        DATPens(result),
        DATPen().gridlines(render.rect).s(0, 0.1).sw(1).f(None)
    ])


def show_error(r, txt):
    return StyledString(txt.upper(), Style(mutator, 100)).pen().align(r)


class test(renderable):
    def __init__(self, rect=(1000, 500), bg=1, postfn=add_grid, **kwargs):
        super().__init__(rect=rect, bg=bg, postfn=postfn, **kwargs)