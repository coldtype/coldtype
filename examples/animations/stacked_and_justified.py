from coldtype import *

# This font does not come w/ Coldtype — but it’s an incredibly cool font worth buying
fatface = Font("~/Type/fonts/fonts/OhnoFatfaceVariable.ttf")

@animation(timeline=Timeline(100, storyboard=[0]), bg=0)
def render(f):
    at = f.a.progress(f.i, loops=1, easefn="eeio")
    cs = f.a.r.inset(0, 50).divide(0.15+at.e*0.7, "maxy")
    c1, c2 = [r.inset(20, 5) for r in cs]
    s = Style(fatface, t=-25, wdth=1, wght=1, ro=1, r=1)
    stacked_and = StyledString("STACKED &",
        s.mod(fitHeight=c1.h, opsz=at.e)).fit(c1).pens()
    justified = StyledString("JUSTIFIED",
        s.mod(fitHeight=c2.h, opsz=1-at.e)).fit(c2).pens()

    return DATPenSet([
        stacked_and.align(c1).trackToRect(c1, pullToEdges=1, r=1),
        justified.align(c2).trackToRect(c2, pullToEdges=1, r=1)
    ]).f(1).understroke(sw=10)