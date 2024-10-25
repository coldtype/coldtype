from coldtype import *

at = AsciiTimeline(2, """
                                                         <
A    A      B     B       C     C         D        D
        E             F              G                H
""")

r = Rect(1000)
s = Scaffold(r).labeled_grid(4, 4)

rs = dict(
    keyframes={
        "A": dict(r=s["a0"].r, ro=0, wght=0),
        "B": dict(r=s["d2"].r, ro=0, wght=1),
        "C": dict(r=s["c0"].r, ro=90, wght=0.5),
        "D": dict(r=s["b3"].r, ro=0, wght=1)})

txt = dict(
    keyframes={
        "E": dict(txt="A"),
        "F": dict(txt="B"),
        "G": dict(txt="C"),
        "H": dict(txt="D")})

@animation(r, tl=at, bg=1)
def scratch(f):
    kfs1 = f.t.kf(**rs)
    kfs2 = f.t.kf(**txt)

    return (StSt(kfs2["txt"], Font.MuSan(), 100
        , wght=kfs1["wght"])
        .f(1)
        .align(kfs1["r"])
        .insert(0, P(kfs1["r"].inset(10)).f(0))
        .rotate(kfs1["ro"])) + s.borders()