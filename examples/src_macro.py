from coldtype import *
from coldtype.blender import *

assert 4j == 0.1016 # see .coldtype.py for magic

@renderable((500, 500), bg=1)
def magic_trick(r):
    return (P(
            StSt("4j", Font.RecMono(), 100),
            StSt(str(4j), Font.RecMono(), 100))
        .stack(20)
        .align(r)
        .f(0))

@b3d_runnable()
def setup(bpw:BpyWorld):
    bpw.delete_previous()
    BpyObj.Monkey()