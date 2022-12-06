from coldtype.test import *

@test()
def test_interp(r):
    a = hsl(0.1).hsl_interp(0, hsl(0.9))
    assert a.hp == pytest.approx(0.1)

    b = hsl(0.1).hsl_interp(1, hsl(0.9))
    assert b.hp == pytest.approx(0.9)

    c = hsl(0.2).hsl_interp(0.5, hsl(0.6))
    assert c.hp == pytest.approx(0.4)

    m = Scaffold(r).cssgrid("a a a", "a", "a b c")

    return (P(
        P().rect(m["a"]).f(a),
        P().oval(m["b"]).f(b),
        P(m["c"]).f(c),
    ))