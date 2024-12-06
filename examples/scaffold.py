from coldtype import *

@renderable()
def boxes(r):
    l = (Scaffold(r)
        .cssgrid(r"auto 30%", r"50% auto", "x y / z q", {
            "x": ("200 a", "a a", "a b / a c"),
            "x/c": ("a a", "a a", "g a / i a"),
            "q": ("a a", "a a", "q b / c d")
        }))

    return P(
        l.view(),
        StSt("X", Font.MuSan(), 200, wght=1).align(l["x"]),
        StSt("Y", Font.MuSan(), 200, wght=1).align(l["y"]),
        StSt("Z", Font.MuSan(), 200, wght=1).align(l["z"]),
        StSt("Q", Font.MuSan(), 200, wght=1).align(l["q"]),
        StSt("A", Font.RecMono(), 100).align(l["a"]).f(hsl(0.9)),
        StSt("B", Font.RecMono(), 100).align(l["b"]).f(hsl(0.9)),
        StSt("C", Font.RecMono(), 100).align(l["c"]).f(hsl(0.9)),
        StSt("G", "Comic Sans", 50).align(l["g"]).f(0),
        StSt("A", "Comic Sans", 50).align(l["x/c/a"]).f(0),
        StSt("I", "Comic Sans", 50).align(l["i"]).f(0),
        P().oval(l["x/c/a"]).fssw(-1, hsl(0.3, a=0.5), 10),
        StSt("Q/Q", "Comic Sans", 50).align(l["q/q"]).f(0),)

@renderable((1080, 540))
def boxes2(r):
    l = Scaffold(r).grid(2, 2)
    
    return P(
        l.view(),
        P().oval(l[0].rect.square().inset(10)).fssw(-1, hsl(0.9, 1), 2))

@renderable((1080, 540))
def boxes3(r):
    l = Scaffold(r).numeric_grid(5)
    
    return P(
        l.view(),
        P().oval(l["3|1"].rect.square().inset(10)).fssw(-1, hsl(0.9, 1), 2)
        )

@renderable((1080, 540), solo=0)
def boxes4(r):
    d = 15
    
    l = Scaffold(r.inset(4).square()).numeric_grid(d, gap=1, annotate_rings=True)
    
    return (P().enumerate(l.cells(), lambda x:
        P(x.el.r)
            .f(hsl(x.el.data("ring_e")*2, 0.6, 0.6))
            .tag(x.el.tag()))
        .find_("3|12", lambda p: p.f(0))
        .find_("11|2", lambda p: p.f(1)))