from coldtype.test import *
from coldtype.fx.xray import *

r = Rect(1000, 1000)

@test(250)
def test_lookup(_r):
    out = P()

    t = StSt("A", Font.MutatorSans(), 1000).pen().fssw(-1, 0, 2)
    lk = skeletonLookup(t)
    t.attach(out)
    
    assert len(lk["moveTo"]) == 4
    assert len(lk["lineTo"]) == 16
    assert len(lk["curveOn"]) == 0
    assert len(lk["qCurveOn"]) == 0

    t = StSt("B", Font.MutatorSans(), 1000).pen().fssw(-1, 0, 2)
    lk = skeletonLookup(t)
    t.attach(out)
    
    assert len(lk["moveTo"]) == 2
    assert len(lk["lineTo"]) == 14
    assert len(lk["curveOn"]) == 0
    assert len(lk["qCurveOn"]) == 23

    t = StSt("C", Font.MutatorSans(), 1000, wght=1).pen().fssw(-1, 0, 2)
    lk = skeletonLookup(t)
    t.copy().layer(None, skeleton()).attach(out)
    
    assert len(lk["moveTo"]) == 1
    assert len(lk["lineTo"]) == 6
    assert len(lk["curveOn"]) == 0
    assert len(lk["qCurveOn"]) == 24

    return out.distribute().scale(0.25).align(_r)