from coldtype import *
from coldtype.warping import warp_fn

r = Rect(1080, 1080)

from fontTools.misc.bezierTools import splitCubicAtT

obv = Font.Cacheable("~/Type/fonts/fonts/ObviouslyVariable.ttf")

tl = Timeline(5)

lockup = (Composer(r,
    "CHET BAKER\nJAZZ DOCUMENTARY\nTRUMPET & SINGING\nWEST COAST JAZZ",
    #"LO! THERE",
    Style(obv, 330, wdth=0.25, wght=0.25, slnt=1),
    leading=20,
    fit=r.w)
    .pens()
    .xa()
    .align(r)
    )

def bend22(self, curves, offset=(0, 1)):
    bw = self.getFrame().w
    bh = self.getFrame().h
    def bender(x, y):
        ic = DATPen.Interpolate(curves, y / bh)
        icb = ic.bounds()
        a1 = ic.value[0][-1][0]
        b1, c1, d1 = ic.value[-1][-1]
        c11, _ = splitCubicAtT(a1, b1, c1, d1, offset[0] + (x/bw)*offset[1])
        _c1 = c11[-1]
        return x, y + Point(_c1).y
    return self.nonlinear_transform(bender)

DATPen.bend22 = bend22

@animation(r, timeline=tl, bg=0, rstate=1)
def stub(f, rs):
    ri = r
    bc = (DATPen()
        .moveTo(ri.psw)
        .boxCurveTo(ri.pse.offset(0, 0), "N", 0.5))
    rsmouse = Point([800, -500])
    bc2 = (DATPen()
        .moveTo(ri.psw.offset(0, 100))
        .curveTo(ri.psw.interp(0.85, rsmouse), ri.pse.interp(0.25, rsmouse), ri.pse.offset(0, 300))
        #"NE", 0.36)
        )
    #bc4 = (DATPen()
    #    .moveTo(ri.psw)
    #    .boxCurveTo(ri.pse.offset(0, 500),
    #    "N", -0.17))
    bc3 = (DATPen()
        .moveTo(ri.psw)
        .boxCurveTo(ri.pse.offset(0, 0),
        "N", 0.5))

    e = f.a.progress(f.i, loops=1, easefn="eeio").e

    return DATPens([
        DATPen().rect(f.a.r).f(0),
        DATPens([
            #bc,
            #bc2,
            #bc3,
        ]).f(None).s(hsl(0.9)).sw(15),
        (lockup.pen()
        #.align(r, "mdx", "mny")
        .addFrame(r)
        #.flatten(55)
        .bend22([bc, bc2, bc3], offset=(0, 1))
        .f(1)
        .scale(0.85)
        .phototype(f.a.r, blur=2, cut=90, cutw=25.5))])