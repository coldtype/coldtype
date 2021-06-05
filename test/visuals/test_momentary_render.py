from coldtype.test import *
from time import sleep

@animation(preview_only=1, momentary=True)
def test_momentary_render_before(f):
    return (StSt(str(f.i), recmono, 50, wdth=0)
        .f(hsl(0, 1))
        .align(f.a.r))

@animation(deferred=True)
def test_momentary_render_after(f):
    return (StSt(str(f.i), recmono, 50, wdth=0)
        .f(hsl(0.6, 1)).align(f.a.r))