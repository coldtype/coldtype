from coldtype.renderer.state import RendererState
from coldtype.test import *

letters = "COLDTYPE"
tl = Timeline(len(letters))

@animation(rstate=1, timeline=tl)
def stub(f, rs:RendererState):
    r = f.a.r
    txt = (StyledString(letters[f.i], Style(co, 1000))
        .fit(r.w-50)
        .pen()
        .f(0)
        .align(r))

    rs.render_external(DPS([
        DP(r).f(hsl(0.3)),
        txt.copy().f(1)
    ]))
    return txt