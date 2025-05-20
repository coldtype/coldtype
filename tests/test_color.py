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
        P(m["c"]).f(c)))

@test()
def test_adjust(r):
    m = Scaffold(r).numeric_grid(10, 1)
    return (P().enumerate(m, lambda x: P()
        .roundedRect(x.el.r, 0.5, scale=False)
        # 1 for l will erase hue information
        # a current limitation of the Color class
        # which stores r,g,b channels
        .f(hsl(0.6, 0.6, 0.99)
            .adj(-x.e))))


@test()
def test_theme_backfill(r):
    p1 = P().rect(r.take(0.5, "N").inset(20)).fssw(Theme(hsl(0), alt=hsl(0.6)), -1, 1)
    p2 = P().rect(r.take(0.5, "S").inset(20)).fssw(-1, Theme(hsl(0), alt=hsl(0.6)), 3)
    assert p2.styles()["alt"]["stroke"]["color"] == hsl(0.6)
    assert p2.styles()["alt"]["fill"].a == 0
    return p1, p2