from coldtype.test import *

@fontpreview("/System/Library/Fonts", r"SFNSText", bg=1)
def preview(r, m):
    return [
        StyledString(str(m.stem), Style(str(m), 72)).pens().align(r).f(0),
    ]