from coldtype.test import *

@renderable((500, 500))
def test2_(r):
    return (P()
        .declare(r:=r.inset(50), cf:=65)
        .m(r.pw).l(r.ps).l(r.pn)
        .bxc(r.pe, r.ps, 45)
        .bxc(r.pn, "sw", cf)
        .bxc(r.ps.o(-130, 0), r.pe, cf+10)
        .f(hsl(0.9,l=0.8)).s(0).sw(4)
        .declare(a:=Line(r.pnw, r.pse))
        .line(a)
        .oval((r.ecy & a).o(100, 100)))

@renderable((500, 500))
def test3_(r):
    return (P()
        .declare(r:=r.inset(180), c:=335)
        .m(r.pw).bxc(r.pe, r.pn, c)
        .bxc(r.pw, r.ps, c).cp()
        .f(hsl(0.7, l=0.9)).s(0).sw(4)
        .rotate(90))

@renderable((500, 500))
def test4_(r):
    return (P()
        .declare(r:=r.inset(150), x:=r.ee, y:=r.ee.o(50, 0))
        .line(x).line(y).oval((r.en & y).o(0, 50))
        .declare(r:=r.inset(-20))
        .m(r.pnw).bxc(r.ps, "SW,NE", 175).cp()
        #.gs("(r:=$rI-20)↖ r↓|↙↗|175")
        .f(None).s(0).sw(4))