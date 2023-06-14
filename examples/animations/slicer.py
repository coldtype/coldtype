from coldtype import *
from coldtype.fx.skia import phototype

rs = random_series(-(r:=50), r, seed=0)

@animation((1080, 1080), bg=0, tl=120)
def slicer(f):
    s = Scaffold(f.a.r.inset(-500, 0)).grid(21, 1)
    
    txt = (StSt("COLD\nTYPE", Font.ColdObvi(), f.e(r=(180, 440)), wght=1, leading=50)
        .xalign(f.a.r)
        .align(f.a.r, ty=1)
        .pen()
        .removeOverlap())

    skew = 0.25
    
    return (P().enumerate(s, lambda x:
        P(x.el.rect.inset(2))
            .skew(skew, 0, pt=(0, 0))
            .intersection(txt)
            .translate(rs[x.i]*skew, rs[x.i])
            .f(1)
            .ch(phototype(f.a.r, 1.5, 180, 35))))