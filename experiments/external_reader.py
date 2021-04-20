from coldtype.renderer.state import RendererState
from coldtype import *

@renderable(rstate=1)
def stub(r, rs:RendererState):
    if rs.external_result:
        return rs.external_result
        #return eval(rs.external_result)