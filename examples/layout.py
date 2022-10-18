from coldtype import *

@renderable()
def boxes(r):
    l = (Layout(r)
        .cssgrid(r"auto 30%", r"50% auto", "x y / z q",
            x=("200 a", "a a", "a b / a c"),
            c=("a a", "a a", "g a / i a")))

    #print(l.tree())

    print(l["x/c/a"])

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
        StSt("I", "Comic Sans", 50).align(l["i"]).f(0))