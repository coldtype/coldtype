from coldtype.renderer.state import RendererState
from coldtype import *

@renderable(rstate=1)
def stub(r, rs:RendererState):
    rs.render_external(DP().oval(r.inset(100)).f(hsl(random())))
    
    return (DATPen()
        .oval(r.inset(50))
        .f(0.8))
