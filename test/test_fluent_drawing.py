from coldtype import *

SRFH = 150

@renderable((1000, 1000))
def curves(r):
    rr = r.take(750, "mny").take(550, "mnx")
    base = rr.take(SRFH, "mny").take(0.65, "mnx")
    cap = rr.take(SRFH, "mxy").take(0.6, "mnx")
    stem = rr.take(135, "mnx").offset(100, 0)
    mid = (cap.take(100, "mxx").offset(0, -350))
    
    rre = rr.p("E")

    def evencurve(p:DATPen, a, b, x):
        if len(p.value) == 0:
            p.moveTo(a)
        else:
            p.lineTo(a)
        
        ctrl = a.interp(0.5, b)
        p.curveTo(a, b)
        p.line([a, a.interp(0.5, b).setx(x), b], moveTo=False, endPath=False)

    return DATPenSet([
        DATPen()
            #.rect(base)
            #.rect(cap)
            #.rect(mid)
            #.rect(stem)
            .chain(evencurve, cap.p("SE"), mid.p("NE"), rre.x-stem.w)
            .lineTo(mid.p("SE"))
            #.printvl()
            .chain(evencurve, mid.p("SE"), cap.p("NE"), rre.x)
            .closePath()
            .printvl()
            #.lineTo(cap.p("SE"))
            .f(None)
            .s(0)
            .sw(1)
            #.addFrame(rr)
            #.align(r, th=False)
            #.translate(100, 250)
            .translate(100, 100),
        DATPen().rect(rr).translate(100, 100).f(None).s(hsl(0.9, a=0.3)).sw(5),
        DATPen().gridlines(r, 50, absolute=True)])
