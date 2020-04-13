from coldtype import *

# This font does not come w/ Coldtype — but it’s an incredibly cool font worth buying
fatface = Font("≈/OhnoFatfaceVariable.ttf")

@animation(timeline=Timeline(100, storyboard=[0]))
def render(f):
    at = f.a.progress(f.i, loops=1, easefn="eeio")
    c1, c2 = [r.inset(20, 5) for r in f.a.r.inset(0, 50).divide(0.15+at.e*0.7, "maxy")]
    s = Style(fatface, t=-25, wdth=1, wght=1, ro=1, r=1)
    stacked_and = StyledString("STACKED &", s.mod(fitHeight=c1.h, opsz=at.e)).fit(c1).pens()
    justified = StyledString("JUSTIFIED", s.mod(fitHeight=c2.h, opsz=1-at.e)).fit(c2).pens()

    return DATPenSet([
        stacked_and.align(c1).trackToRect(c1, pullToEdges=1, r=1).f(0, 1, 0),
        justified.align(c2).trackToRect(c2, pullToEdges=1, r=1).f(0, 0, 1)
    ]).understroke(s=(1, 0, 0), sw=10)