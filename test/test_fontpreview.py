from coldtype.test import *

@fontpreview("", r"Times", bg=1)
def preview(r, m):
    return [
        StyledString(str(m.stem), Style(str(m), 72)).pens().align(r).f(0),
        str(m)
    ]