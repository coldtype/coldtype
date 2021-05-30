from coldtype.test import *
from coldtype.renderer.state import RendererState

@renderable(rstate=1)
def editable(r, rs:RendererState):
    return (DATPen()
        .rect(r.inset(200))
        .f(hsl(0.8))
        .editable("r1"))