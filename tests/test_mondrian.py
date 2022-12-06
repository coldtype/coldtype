from coldtype.test import *

from coldtype.runon.runon import RunonSearchException, RunonException


@test((500, 500))
def test_auto_recursion(r):
    l = Scaffold(r)
    assert l.depth() == 0
    assert l.v == l.r
    assert l.v == l.rect

    l.divide(0.5, "N")
    assert l.depth() == 1
    assert l.rect.w == 500
    assert l.rect.h == 500
    assert l[0].rect.w == 500
    assert l[0].rect.h == 250
    assert l[1].rect.h == 250

    l.divide(200, "W")
    assert l.depth() == 2
    assert l.rect.w == 500
    assert l.rect.h == 500
    assert l[0].rect.w == 500
    assert l[0].rect.h == 250
    assert l[1].rect.h == 250
    assert l[0][0].rect.w == 200
    assert l[1][0].rect.w == 200
    
    l[1][1].subdivide(3, "W")
    assert l[1][1][1].rect.w == 100

    return P(l[0])

@test((500, 500))
def test_duck(r):
    l = Scaffold(r)
    l.grid(2, 2, "abcd")

    assert l.val_present() == False
    assert l[0].tag() == "a"
    assert l[-1].tag() == "d"

    txt = (StSt("ASDF", Font.MutatorSans(), 50))
    assert txt.ambit().x == 0
    
    txt1 = txt.copy().align(l["b"])
    txt2 = txt.copy().align(l["b"].rect)
    
    assert txt.ambit().x == 0
    assert txt1.ambit().x == 333.725
    assert txt2.ambit().x == 333.725

    return txt1, P(l[0])

@test((500, 500))
def test_cssgrid(_r):
    l = (Scaffold(Rect(500, 500))
        .cssgrid(r"auto 30%", r"50% auto", "x y / z q",
            x=("200 a", "a a", "a b / a c"),
            c=("a a", "a a", "g a / i a"),
            q=("a a", "a a", "q b / c d")))
    
    assert l.depth() == 3
    assert l["x"] is not None
    assert l["x/c"] is not None
    assert l["x/c/a"] is not None
    
    assert l.get("x/c/q") is None

    with pytest.raises(RunonSearchException) as context:
        l["x/c/z"]

    assert l["x/a"] != l["x/c/a"]
    assert l["x/c/a"] != l["a"]
    assert l["q"] != l["q/q"]

    return P(l["x/a"]) + P(l["q"])
