from coldtype.test import *
from coldtype.renderer.state import RendererState

@renderable(rstate=1)
def editable(r, rs:RendererState):
    saved, shape = rs.polygon_selection()
    return shape