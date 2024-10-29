from coldtype import *

@renderable()
def scratch(r):
    return (P()
        .rect(r.inset(150)))
