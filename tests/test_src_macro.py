from coldtype.test import *

co = Font.Cacheable("assets/ColdtypeObviously-VF.ttf")
mutator = Font.Cacheable("assets/MutatorSans.ttf")
r = Rect(1000, 500)

assert 4j == 0.1016 # see .coldtype.py for magic

@test(150)
def test_src_macro(_r):
    return (P(
            StSt("4j", Font.RecMono(), fs:=60),
            StSt(str(4j), Font.RecMono(), fs))
        .stack(20)
        .align(_r)
        .f(hsl(0.9)))