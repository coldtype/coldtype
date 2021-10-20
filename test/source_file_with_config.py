from coldtype import *

# .coldtype
WINDOW_PIN = "SW"

@renderable()
def test1(r):
    return (StSt("COLDTYPE", Font.ColdtypeObviously())
        .align(r))

@renderable()
def test2(r):
    return (StSt("COLDTYPE", Font.MutatorSans())
        .align(r))