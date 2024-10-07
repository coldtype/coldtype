from coldtype.test import *
from coldtype.osutil import on_mac

not_mac = not on_mac()

try:
    from coldtype.drawbot import *
except ModuleNotFoundError:
    if not_mac:
        print("Skipping drawBot test (mac-only)")
    else:
        print("Must install drawBot")

if on_mac():
    @drawbot_renderable((800, 100), bg=1, render_bg=0)
    def test_setup(r):
        txt = StSt("ASDF", Font.RecMono(), 100).align(r).ch(dbdraw)
        assert txt.depth() == 1
        assert txt.ambit().round() == Rect(278, 15, 240, 70)
        return txt

    @drawbot_renderable((800, 200), bg=1, render_bg=0)
    def test_gs_pen(r):
        rr = Rect(0, 0, 100, 100)
        dp = (P()
            .declare(c:=75)
            .m(rr.pne).bxc(rr.ps, "se", c)
            .bxc(rr.pnw, "sw", c).cp()
            .align(r)
            .scale(1.2)
            .f(hsl(0.3, a=0.1))
            .s(hsl(0.9))
            .sw(5)
            .ch(dbdraw))
        
        assert len(dp.v.value) == 4
        assert type(dp) == P

    @drawbot_renderable((800, 300), bg=1, render_bg=0)
    def test_distribute_on_path(r):
        script = Font.RecMono()

        s = (StSt("Hello", script, 100)
            .f(hsl(0.7, s=1))
            .align(r)
            .chain(dbdraw))
        
        with db.savedState():
            db.fill(None)
            db.stroke(0)
            db.strokeWidth(3)
            db.rect(*s.ambit())

        circle = P().oval(r.inset(100, 20)).rotate(0)
        s2 = (s.copy()
            .zero()
            .distribute_on_path(circle)
            .chain(dbdraw))
        
        s2a = (P(s2.ambit(tx=1, ty=1)).fssw(-1, hsl(0.9, a=0.3), 10) | dbdraw)

        with db.savedState():
            db.fill(None)
            db.stroke(0)
            db.strokeWidth(2)
            db.oval(*circle.ambit())
        
        assert s.f() == s2.f()
        assert s2a.ambit(tx=1, ty=1).round() == Rect(403, 19, 265, 114)