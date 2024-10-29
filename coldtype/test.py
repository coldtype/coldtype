import pytest
from coldtype import *
from functools import partial
from random import Random
from pprint import pprint


co = Font.Cacheable("assets/ColdtypeObviously-VF.ttf")
mutator = Font.Cacheable("assets/MutatorSans.ttf")
recmono = Font.Cacheable("assets/RecMono-CasualItalic.ttf")

Style.RegisterShorthandPrefix("≈", "~/Type/fonts/fonts")


def add_grid(render, result):
    return P([
        P(result),
        P().gridlines(render.rect).s(0, 0.1).sw(1).f(None)
    ])


def show_error(r, txt):
    return StyledString(txt.upper(), Style(mutator, 100)).pen().align(r)


class test(renderable):
    def __init__(self, rect=(800, 200), bg=hsl(0.17, 0.8, 0.7, 0.2), post_preview=add_grid, **kwargs):
        if isinstance(rect, int):
            rect = (800, rect)
        
        super().__init__(rect=rect, bg=bg, post_preview=post_preview, **kwargs)