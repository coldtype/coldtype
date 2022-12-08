from coldtype import *
from coldtype.fx.warping import warp
from coldtype.fx.skia import phototype

keyframes = [
    dict(wdth=0, wght=0, rotate=-15, leading=200,
        font_size=700, warp=0, blur=15),
    dict(wdth=1, wght=1, rotate=0, leading=10,
        font_size=50, warp=200, blur=5),
    dict(wdth=0, wght=1, rotate=15, leading=100,
        font_size=320, warp=50, blur=3),
    dict(wdth=0.5, wght=0.5, rotate=0, leading=-470,
        font_size=250, warp=0, blur=1)]

at = AsciiTimeline(8, 30, """
                <
0   1   2   3   
""", keyframes).shift("end", +10)

@animation(timeline=at, bg=0)
def warp_blur(f):
    state = f.t.kf("eeio")
    return (StSt("WARP\nBLUR", Font.MuSan(), ro=1, **state)
        .xalign(f.a.r)
        .align(f.a.r)
        .pen()
        .f(1)
        .ch(warp(None, # can be a number like 5 to preserve curves
            f.i*30, f.i, mult=int(state["warp"])))
        .ch(phototype(f.a.r, state["blur"], cutw=50)))