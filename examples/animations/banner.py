from coldtype import *
from coldtype.time.nle.ascii import AsciiTimeline
from coldtype.fx.skia import phototype

at = AsciiTimeline(3, 30, """
                                       <
0     0  1       2    3    3   4
""", {
    "0": dict(wdth=0, rotate=0, tu=300),
    "1": dict(wdth=1, rotate=15, tu=-150),
    "2": dict(wdth=0.25, rotate=-15, tu=350),
    "3": dict(wdth=0.75, rotate=0, tu=-175),
    "4": dict(wdth=0.5, rotate=25, tu=100)
})

@animation(timeline=at, bg=1, rect=(1500, 300))
def render(f):
    return (StSt("COLDTYPE",
        Font.ColdtypeObviously(), 250
        , **at.kf(f.i, easefn="eeio")
        , r=1, ro=1)
        .align(f.a.r, th=0)
        .f(1)
        .understroke(0, 20)
        .ch(phototype(f.a.r, 2, 200, 30, 0)))