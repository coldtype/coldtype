from coldtype.test import *
from coldtype.animation import *


@test(layers=["oval", "rect"])
def test_static_layers(r):
    out = DATPenSet([
        DATPen().oval(r.square()).f("hr",0.5,0.5,0.5).tag("oval"),
        DATPenSet([DATPen().roundedRect(r.square(), 10, 10).f("hr",0.5,0.5,0.5)]).tag("rect"),
    ])
    return out


@animation(layers=["oval", "rect"])
def test_layered_animation(f):
    out = [
        DATPen().oval(f.a.r.square()).f("hr",0.5,0.5,0.5).tag("oval"),
        DATPen().roundedRect(f.a.r.square(), 10, 10).f("hr",0.5,0.5,0.5).tag("rect")
    ]
    return out