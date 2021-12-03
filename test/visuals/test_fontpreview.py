from coldtype.test import *

@fontpreview(r"Times", bg=1)
def preview(f, m):
    return StSt(str(m.stem), m, 72).align(f.a.r).f(0)