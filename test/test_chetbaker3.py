from coldtype import *
from coldtype.warping import warp_fn
from drafting.text.richtext import RichText

r = Rect(1080, 1080)

from fontTools.misc.bezierTools import splitCubicAtT

obv2 = Font.Cacheable("~/Type/fonts/fonts/ObviouslyVariable.ttf")
obv = Font.Cacheable("~/Type/fonts/fonts/OhnoFatfaceVariable.ttf")

tl = Timeline(2)

lockup = (RichText(r,
    "THE KITCHEN\nCABINET\nTRANSATLANTIC[a] \nCABLE[a] EP[a2]",
    {
        "default":Style(obv, 480, wdth=0.75, wght=0.15, slnt=0.5, opsz=0.75, tu=-10),
        "a2":Style(obv2, 250, wdth=1, wght=0.15, slnt=0.5, opsz=0, tu=-100),
        "a": Style(obv2, 250, wdth=0.65, wght=0.25, tu=-50, slnt=1),
    },
    graf_style=GrafStyle(leading=30),
    #leading=30,
    fit=r.w-0
    )
    #.pens()
    .xa()
    .align(r)
    .pmap(lambda i,p: p.flatten(3)))

def bendr(self, r:Rect, curves, cx:DATPen=None, tangent=None, offset=(0, 1)):
    crv0 = DATPen().moveTo(r.psw).boxCurveTo("N", 0.15, r.pse)
    crvl = DATPen().moveTo(r.psw).boxCurveTo("N", 0.15, r.pse)
    bw = self.getFrame().w
    bh = self.getFrame().h

    def bender(x, y):
        ic = DATPen.Interpolate([crv0, *curves, crvl], min(1, max(0, y / bh)))
        c11, _ = ic.split_t(offset[0] + (x/bw)*offset[1])
        _, _a, _b, _c = c11
        if tangent and True:
            tan = math.degrees(math.atan2(_c[1] - _b[1], _c[0] - _b[0]) + math.pi*.5)
            ax = math.sin(math.radians(90-tan)) * y
            by = math.cos(math.radians(tan)) * y
            if cx:
                cxt, _ = cx.split_t(x/bw)
            else:
                af = cxt[-1][1]/bh

            af = math.sin((x/bw)*(math.pi))
            return x+ax*af*tangent[0], y + Point(_c).y + by*tangent[1]
        return x, y + Point(_c).y
    return self.nonlinear_transform(bender)

DATPen.bendr = bendr

@animation(r, timeline=tl, bg=0, rstate=1)
def stub(f, rs):
    ri = r
    e = f.a.progress(f.i, loops=0, easefn="eeio").e
    
    rsmouse = Point([0, 0])
    rsmouse = r.ps.offset(-2000, 900)
    #rsmouse = rs.mouse
    #print(rsmouse)

    by = (DATPen()
        .moveTo(ri.psw.offset(0, -70))
        .curveTo(
            ri.psw.interp(-0.13, rsmouse),
            ri.pse.interp(0.53, rsmouse),
            ri.pse.offset(0, -210)))
    
    bx = (DATPen()
        .moveTo(ri.psw)
        .curveTo(
            ri.psw.interp(1.3, ri.ps),
            ri.pse.interp(1.3, ri.ps),
            ri.pse))

    global lockup
    if False:
        lockup = DATPens([
            DATPen().rect(r.inset(50)).outline(50),
            DATPen().line(r.inset(50).edge("mdx")).outline(50),
            DATPen().line(r.inset(50).edge("mdy")).outline(50)
        ]).f(1).pen().flatten(5)

    return DATPens([
        DATPen().rect(f.a.r).f(hsl(0.6, s=0.7, l=0.5)),
        (lockup
            .pen()
            .addFrame(r)
            .cast(DATPen)
            .bendr(r, [by], bx, tangent=[e, e+0.15])
            #.scale(0.5)
            #.at_rotation(e*360, λp: p.bendr(r, [by], bx))
            #.rotate(25)
            #.bendr(r, [by], bx)
            #.rotate(-25)
            .f(1)
            .scale(0.65)
            #.rotate(5)
            .phototype(f.a.r, blur=2, cut=150, cutw=25, fill=bw(1)))])