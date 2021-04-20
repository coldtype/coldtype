from coldtype.renderer.state import RendererState
from coldtype import *

@renderable(rstate=1)
def stub(r, rs:RendererState):
    print("hello", rs.external_result)
    if rs.external_result:
        return DPS([rs.external_result])