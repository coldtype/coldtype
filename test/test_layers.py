from coldtype.test import *
from coldtype.animation import *


#@test(layers=["oval", "rect"])
def test_static_layers(r):
    out = DATPenSet([
        DATPen().oval(r.square()).f("hr",0.5,0.5,0.5).tag("oval"),
        DATPenSet([DATPen().roundedRect(r.square(), 10, 10).f("hr",0.5,0.5,0.5)]).tag("rect"),
    ])
    return out


@animation(layers=["oval", "rect", "__default__"], rect=(1920, 1080))
def test_layered_animation(f):
    out = DATPenSet()
    if "oval" in f.layers:
        out += StyledString(chr(65+f.i), Style(mutator, 1000)).pen().f("random").tag("oval").align(f.a.r, th=0)
    if "rect" in f.layers:
        out += StyledString(chr(65+f.i), Style(mutator, 1000, wght=1)).pen().f("hr",0.5,0.5,0.5).tag("rect").align(f.a.r, th=0)
    out += StyledString(chr(65+f.i), Style(mutator, 1000, wght=0.5)).pen().f(hsl(0.5, a=0.25)).tag("rect").align(f.a.r, th=0).tag("__default__")
    return out