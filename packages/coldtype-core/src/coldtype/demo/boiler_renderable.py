from coldtype import *

@renderable()
def scratch(r:Rect):
    return (P()
        .rect(r.inset(150)))
