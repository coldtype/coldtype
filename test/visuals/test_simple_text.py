from coldtype.test import *

@test()
def stub(r):
    return (StSt("Yy", "Mistral", 500)
        .align(r)
        .f(hsl(0.7))
        .î(0, lambda p: p.a(0.1)))