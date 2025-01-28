from coldtype.test import *

from coldtype.runon.runon import RunonSearchException, RunonException


@test((500, 250))
def test_auto_recursion(r):
    l = Scaffold(r)
    assert l.depth() == 0
    assert l.v == l.r
    assert l.v == l.rect

    l.divide(0.5, "N")
    assert l.depth() == 1
    assert l.rect.w == 500
    assert l.rect.h == 250
    assert l[0].rect.w == 500
    assert l[0].rect.h == 250/2
    assert l[1].rect.h == 250/2

    l.divide(200, "W")
    assert l.depth() == 2
    assert l.rect.w == 500
    assert l.rect.h == 500/2
    assert l[0].rect.w == 500
    assert l[0].rect.h == 250/2
    assert l[1].rect.h == 250/2
    assert l[0][0].rect.w == 200
    assert l[1][0].rect.w == 200
    
    l[1][1].subdivide(3, "W")
    assert l[1][1][1].rect.w == 100

    return P(l[0])

@test((500, 250))
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

@test((500, 250))
def test_cssgrid(_r):
    l = (Scaffold(Rect(_r))
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

@test((500, 500))
def test_cssgrid_regexs(r):
    # vulf compressor adv (mini)

    s = Scaffold(r).cssgrid("a a a", "a 100 60", "a || b || c _/ d d d _/ e e e", {
            r"^[abc]": ("a a", "a 30", "a b _/ c c"),
            "d": ("a 60", "a a", "a b / c d")})

    assert s["a"].r.w == 166
    assert s["a/b"].r.w == s["b/b"].r.w - 1
    assert s["a/b"].r.w != s["d/b"].r.w
    assert s["d/b"].r.w == 60

    assert s["a"].depth() == 1
    assert s["d"].depth() == 1
    assert s["e"].depth() == 0

    assert s["a/a"].depth() == 0

    return P(
        P(s["a/b"]),
        P(s["b/b"]),
        P(s["c/b"]),
        P(s["d/b"]),
        P(s["e"]))

@test((500, 250))
def test_cssgrid_nested(r):
    s = Scaffold(r).cssgrid("a a a", "a a a", "a b c / d e f / g h i", {
        "a": ("a a", "a a", "a b / c d"),
        "a/b": ("a a a", "a", "a b c"),
        r"h|i": ("a a", "a", "a b"),
    })

    assert s["a/b/b"].r == Rect(110.00,209.00,28.00,41.00)
    assert s["h/b+i/a"].r == Rect(249.00,0.00,167.00,84.00)

    return P(
        P(s["a/b/b"]).f(0),
        P(s["h/b+i/a"]).f(hsl(0.65)),
        )

@test((500, 250))
def test_wildcards(r):
    s = Scaffold(r).cssgrid("a a", "a a", "a b / c d", {
        ".*": ("a a", "a a", "a b / c d"),
        ".*/.*": ("a a", "a", "a b"),
    })
    
    assert s.depth() == 3
    assert len(s) == 4
    assert len(s["a"]) == 4
    assert len(s["a/a"]) == 2
    assert len(s["a/a/a"]) == False
    assert len(s.match("a")) == 1
    assert len(s.match("a/a")) == 1
    assert len(s.match("a/a/.*")) == 2

    s2 = s.copy().collapse()
    
    assert len(s2) == 32
    assert len(s2.match("a")) == 16
    assert len(s2.match("b")) == 16

    return P(
        P(s["a/a/a"]).f(hsl(0.5)),
        P(s["c/b/b"]).f(hsl(0.07, 0.7)),
        P(s["d/d/b"]).f(hsl(0.8)),
    )

@test((500, 500))
def test_labeled_grid(r):
    ri = r.inset(20)
    s = Scaffold.AspectGrid(ri, 4, 5)
    assert s.r.w < ri.w
    assert s.r.h == ri.h
    assert len(s) == 20
    assert s[0].tag() == "0|4"
    assert s[-1].tag() == "3|0"
    return s.view()

@test((500, 500), solo=0)
def test_numeric_grid(r):
    ri = r.inset(20)
    s = Scaffold(ri).numeric_grid(5, gap=4, annotate_rings=1)
    
    assert len(s) == 81
    assert len(s.cells()) == 25

    assert s["2|2"].data("ring") == 0
    assert s["2|2"].data("ring_e") == 0
    assert s["3|2"].data("ring") == 1
    assert s["4|1"].data("ring") == 2
    assert s["4|4"].data("ring_e") == 1
    
    p = (P().enumerate(s.cells(), lambda x: P()
        .oval(x.el.r)
        .f(0)
        .up()
        .append(StSt(x.el.tag(), Font.JBMono(), 24, wght=1)
            .f(1)
            .align(x.el.r))
        .tag(x.el.tag())))

    assert p.find_("4|4").ambit().pne == ri.pne
    assert p.find_("0|0").ambit().psw == ri.psw
    assert p.find_("0|4").ambit().pnw == ri.pnw
    assert p.find_("4|0").ambit().pse == ri.pse

    assert s["0|1*3|2"].r == s["0|1+2|2"].r
    
    assert s["-1|-1"].r == s["4|4"].r
    assert s["0|-1*3|-2"].r == s["0|4+2|3"].r

    return p