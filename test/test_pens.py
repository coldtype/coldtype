import unittest
from random import Random
from coldtype.geometry import Rect, Point
from coldtype.runon.path import P

from coldtype.color import hsl, rgb
from coldtype.pens.drawablepen import DrawablePenMixin
from coldtype.renderer.reader import SourceReader
from coldtype.text.composer import StSt, Font
from coldtype.fx.chainable import Chainable

co = Font.Cacheable("assets/ColdtypeObviously-VF.ttf")
mutator = Font.Cacheable("assets/MutatorSans.ttf")

class TestPens(unittest.TestCase):
    def test_gs(self):
        r = Rect(0, 0, 100, 100)
        dps = P()
        dp = (P()
            .declare(r:=r)
            .m(r.pnw).l(r.pne).bxc(r.psw, "se")
            .ep())
        self.assertEqual(len(dp.v.value), 4)
        self.assertEqual(dp.v.value[-2][-1][0], Point(100, 35))
        self.assertEqual(dp.v.value[-1][0], "endPath")
        self.assertEqual(dp.unended(), False)
        dps.append(P([dp]))
        self.assertEqual(len(dps.tree().splitlines()), 4)
        self.assertEqual(dps.tree().splitlines()[-1],
            " | - <®:P:RecordingPen(4mvs)>")
        
    def test_gs_arrowcluster(self):
        r = Rect(100, 100)
        dp = (P().m(r.pnw).l(r.pne).l(r.pse).ep())
        
        self.assertEqual(len(dp.v.value), 4)
        self.assertEqual(dp.v.value[0][-1][0], Point(0, 100).xy())
        self.assertEqual(dp.v.value[1][-1][0], Point(100, 100).xy())
        self.assertEqual(dp.v.value[2][-1][0], Point(100, 0).xy())
    
    def test_gs_relative_moves(self):
        r = Rect(100, 100)
        dp = (P().m(r.pnw).l(r.pnw.o(50,-50)).l(r.pnw.o(0,-50)).ep())
        
        self.assertEqual(len(dp.v.value), 4)
        self.assertEqual(dp.v.value[0][-1][0], Point(0, 100).xy())
        self.assertEqual(dp.v.value[1][-1][0], Point(50, 50).xy())
        self.assertEqual(dp.v.value[2][-1][0], Point(0, 50).xy())
        
    def test_reverse(self):
        r = Rect(100, 100)
        dp = (P().m(r.pnw).l(r.pne).l(r.pse).ep())
        p1 = dp.v.value[0][-1]
        p2 = dp.reverse().v.value[-2][-1]
        self.assertEqual(p1, p2)
    
    def test_transforms(self):
        dp = (P(Rect(100, 100))
            .data(frame=Rect(100, 100))
            .align(Rect(200, 200)))
        
        self.assertEqual(dp.data("frame").mxx, 150)
        self.assertEqual(dp.v.value[-2][-1][-1][0], 50)

        self.assertEqual(
            dp.copy().rotate(45).round().v.value,
            dp.copy().rotate(360+45).round().v.value)
        
        self.assertEqual(dp.copy().scale(2).ambit().w, 200)

    def test_pens_ambit(self):
        dps = (P([
                P(Rect(50, 50)),
                P(Rect(100, 100, 100, 100))])
                #.print(lambda x: x.tree())
                )
        ram = dps.ambit()
        self.assertEqual(ram, Rect(0, 0, 200, 200))

        moves = []
        dps.walk(lambda p, pos, _: moves.append([p, pos]))
        self.assertEqual(moves[0][0], dps)
        self.assertEqual(moves[0][1], -1)
        self.assertEqual(moves[1][1], 0)
    
    def test_remove_blanks(self):
        dps = (P([
            P(Rect(50, 50)),
            P()
        ]))
        self.assertEqual(len(dps), 2)
        dps.deblank()
        self.assertEqual(len(dps), 1)
    
    def test_collapse(self):
        rr = Rect(100, 100)
        r = P([
            P([P([P().rect(rr)])]),
            P([P().rect(rr)]),
        ])

        self.assertIsInstance(r[0], P)
        self.assertIsInstance(r[0][0], P)

        r.collapse()
        self.assertIsInstance(r[0], P)
        self.assertIsInstance(r[1], P)

        r = P([
            P([P([P().rect(rr)])]),
            P([P().rect(rr)]),
        ])

        r2 = r.copy().collapse()
        self.assertEqual(len(r), 2)

        self.assertIsInstance(r[0], P)
        self.assertIsInstance(r[0][0], P)

        self.assertIsInstance(r2[0], P)
        self.assertIsInstance(r2[1], P)

        r = P([
            P([P([P()])]),
            P([P()]),
        ])

        r2 = r.copy().collapse()
        self.assertEqual(len(r), 2)
        self.assertEqual(len(r2), 0)

        r = P([
            P([P([P()])]),
            P([P()]),
        ])

        r2 = r.copy().collapse(deblank=False)
        self.assertEqual(len(r), 2)
        self.assertEqual(len(r2), 2)
    
    def test_find(self):
        dps = P([
            P([P([P().tag("find-me").f(hsl(0.9))])]),
            P().tag("not-me"),
            P([P().tag("find-me").f(hsl(0.3))])])

        self.assertEqual(dps.find("find-me")[0].f().h/360, 0.9)
        self.assertAlmostEqual(dps.find("find-me")[1].f().h/360, 0.3)

    def test_cond(self):
        dps = (P([
            (P().cond(True,
                lambda p: p.f(rgb(1, 0, 0))))]))
        
        self.assertEqual(dps[0].f().r, 1)

        def _build(condition):
            return (P([
                (P().cond(condition,
                    lambda p: p.f(rgb(0, 0, 1)),
                    lambda p: p.f(rgb(1, 0, 0))))]))
        
        self.assertEqual(_build(True)[0].f().b, 1)
        self.assertEqual(_build(False)[0].f().r, 1)
    
    def test_alpha(self):
        dps = (P([
            (P([
                (P().alpha(0.5))
            ]).alpha(0.5))
        ]).alpha(0.25))

        def walker(p, pos, data):
            if pos == 0:
                self.assertEqual(data["alpha"], 0.0625)
            elif pos == 1 and data["depth"] == 0:
                self.assertEqual(data["alpha"], 0.25)
            elif pos == 1 and data["depth"] == 1:
                self.assertEqual(data["alpha"], 0.125)

        dps.walk(walker)
    
    def test_visibility(self):
        dps = (P([
            (P([
                (P().visible(1).tag("visible")),
                (P().visible(0).tag("invisible"))
            ]))
        ]))

        def walker(p, pos, data):
            nonlocal visible_pen_count
            if pos == 0:
                visible_pen_count += 1

        visible_pen_count = 0
        dps.walk(walker, visible_only=True)
        self.assertEqual(visible_pen_count, 1)

        visible_pen_count = 0
        dps.walk(walker, visible_only=False)
        self.assertEqual(visible_pen_count, 2)

        visible_pen_count = 0
        dps[0][0].visible(0)
        dps.walk(walker, visible_only=True)
        self.assertEqual(visible_pen_count, 0)
    
    def test_style(self):
        src = """
from coldtype import *

def two_styles(r):
    return (P()
        .oval(r.inset(50).square())
        .f(hsl(0.8))
        .attr("alt", fill=hsl(0.3)))

@renderable()
def no_style_set(r):
    return two_styles(r)

@renderable(style="alt")
def style_set(r):
    return two_styles(r)

def lattr_styles(r):
    return (P()
        .oval(r.inset(50).square())
        .f(hsl(0.5)).s(hsl(0.7)).sw(5)
        .lattr("alt", lambda p: p.f(hsl(0.7)).s(hsl(0.5)).sw(15)))

@renderable()
def lattr_no_style(r):
    return lattr_styles(r)

@renderable(style="alt")
def lattr_style_set(r):
    return lattr_styles(r)
"""

        sr = SourceReader(None, code=src)
        rs = sr.frame_results(0)
        sr.unlink()

        self.assertNotEqual(
            rs[0][-1].attr(rs[0][0].style, "fill"),
            rs[1][-1].attr(rs[1][0].style, "fill"))
        
        self.assertNotEqual(
            rs[2][-1].attr(rs[2][0].style, "fill"),
            rs[3][-1].attr(rs[3][0].style, "fill"))
        
        self.assertEqual(rs[2][-1].attr(rs[2][0].style, "strokeWidth"), 5)
        self.assertEqual(rs[3][-1].attr(rs[3][0].style, "strokeWidth"), 15)

        dpm = DrawablePenMixin()
        dpm.dat = rs[3][-1]
        attrs = [x for _, x in list(dpm.findStyledAttrs(rs[3][0].style))]
        self.assertEqual(len(attrs), 2)
        self.assertEqual(attrs[1][1].get("weight"), 15)

    def test_subsegmenting(self):
        f1 = Font.Cacheable("assets/ColdtypeObviously_BlackItalic.ufo")

        shape = (StSt("C", f1, 1000, wght=0.5)[0]
            .explode()[0])

        self.assertAlmostEqual(
            shape.length()/2,
            shape.copy().subsegment(0, 0.5).length(),
            delta=1)
        
        self.assertAlmostEqual(
            shape.length(),
            shape.copy().subsegment(0, 1).length(),
            delta=1)
        
        shape1 = (StSt("D", f1, 1000, wght=0.5)[0]
            .explode()[0])
        
        shape2 = shape1.copy().fully_close_path()

        self.assertLess(shape1.length(), shape2.length())

        self.assertAlmostEqual(
            shape2.length()/2,
            shape2.copy().subsegment(0, 0.5).length(),
            delta=1)
    
    def test_explode(self):
        r = Rect(1000, 500)
        
        o1 = (StSt("O", co, 500, wdth=1).pen())
        o2 = (StSt("O", co, 500, wdth=1)
            .pen()
            .explode()
            .index(1, lambda p: p.rotate(90))
            .implode().f(hsl(0.3)).align(r))
        
        self.assertEqual(
            o1.explode()[0].ambit().w,
            o2.explode()[0].ambit().w)

        self.assertAlmostEqual(
            o1.explode()[1].ambit().h,
            o2.explode()[1].ambit().w)
    
    def test_scaleToRect(self):
        r = Rect(1000, 500)
        dps = P([
            (StSt("SPACEFILLING", mutator, 50)
                .align(r)
                .f(hsl(0.8))
                .scaleToRect(r.inset(100, 100), False)),
            (StSt("SPACEFILLING", mutator, 50)
                .align(r)
                .f(hsl(0.5))
                .scaleToWidth(r.w-20)),
            (StSt("SPACEFILLING", mutator, 50)
                .align(r)
                .f(hsl(0.3))
                .scaleToHeight(r.h-50))])
        
        self.assertAlmostEqual(
            dps[0].ambit(th=1).w, r.inset(100).w)
        self.assertAlmostEqual(
            dps[0].ambit(tv=1).h, r.inset(100).h)
        self.assertAlmostEqual(
            dps[1].ambit(th=1).w, r.w-20)
        self.assertAlmostEqual(
            dps[2].ambit(tv=1).h, r.h-50)
        
        dps.picklejar(r)
    
    def test_distribute_and_track(self):
        dps = P()
        rnd = Random(0)
        r = Rect(1000, 500)

        for _ in range(0, 11):
            dps += (P()
                .rect(Rect(100, 100))
                .f(hsl(rnd.random(), s=0.6))
                .rotate(rnd.randint(-45, 45)))
        dps = (dps
            .distribute()
            .track(-50)
            .reverse()
            .understroke(s=0.2)
            .align(r)
            )
        
        self.assertEqual(len(dps), 11)
        self.assertEqual(dps.ambit(th=1).round().w, 830)
    
        dps.picklejar(r)
    
    def test_track_to_rect(self):
        r = Rect(1000, 500)
        text = (StSt("COLD", co, 300, wdth=0, r=1)
            .align(r)
            .track_to_rect(r.inset(50, 0), r=1))
        
        self.assertEqual(text[0].glyphName, "D")
        self.assertEqual(text[-1].ambit().round().x, 50)
        self.assertEqual(text[0].ambit().round().x, 883)
    
    def test_distribute_oval(self):
        r = Rect(1000, 500)
        txt = (StSt("COLDTYPE "*7, co, 64,
            tu=-50, r=1, ro=1)
            .distribute_on_path(P()
                .oval(r.inset(50))
                .reverse()
                .repeat())
            .understroke(s=0, sw=5))
        
        txt.picklejar(r)

        self.assertEqual(len(txt), 62)
        
        x, y = txt[-1].ambit().xy()
        self.assertAlmostEqual(x, 500, 0)
        self.assertAlmostEqual(y, 50, 0)
    
    def test_distribute_path_lines(self):
        r = Rect(1080, 1080).inset(200)
        p = (P()
            .moveTo(r.psw)
            .lineTo(r.pn)
            .lineTo(r.pse)
            .endPath())

        lockup = (StSt("COLDTYPE",
            Font.MutatorSans(), 220, wght=.4, wdth=0.5)
            .distribute_on_path(p)
            .align(r, tv=1, th=1)
            .f(0))
        
        lockup.picklejar(Rect(1080, 1080))

        x, y = lockup[3].ambit().xy()
        self.assertEqual(lockup[3].glyphName, "D")
        self.assertAlmostEqual(x, 454, 0)
        self.assertAlmostEqual(y, 690, 0)

        x, y = lockup[-1].ambit().xy()
        self.assertEqual(lockup[-1].glyphName, "E")
        self.assertAlmostEqual(x, 792, 0)
        self.assertAlmostEqual(y, 312, 0)
    
    def test_stack(self):
        r = Rect(540, 540)
        sr = Rect(100, 100)

        res = (P([
            (P().oval(sr)
                .f(hsl(0.5))
                .tag("A")),
            (P().oval(sr)
                .f(hsl(0.7))
                .tag("B")),
            (P().oval(sr)
                .f(hsl(0.9))
                .tag("C"))])
            .stack(10))
        
        res.picklejar(r)

        self.assertEqual(res.find_("C").ambit().y, 0)
        self.assertEqual(res.find_("B").ambit().y, 110)
        self.assertEqual(res.find_("A").ambit().y, 220)
    
    def test_stack_and_lead(self):
        r = Rect(540, 540)
        sr = Rect(100, 100)

        res = (P([
            (P().oval(sr)
                .f(hsl(0.5))
                .tag("A")),
            (P().oval(sr)
                .f(hsl(0.7))
                .tag("B")),
            (P().oval(sr)
                .f(hsl(0.9))
                .tag("C"))])
            .stack(10)
            .lead(10))
        
        res.picklejar(r)

        self.assertEqual(res.find_("C").ambit().y, 0)
        self.assertEqual(res.find_("B").ambit().y, 120)
        self.assertEqual(res.find_("A").ambit().y, 240)
    
    def test_chain(self):
        def c1(a):
            def _c1(p:P):
                return [a]
            return Chainable(_c1)
        
        def c2(a):
            def _c2(p:P):
                p.data(hello=a)
                return None
            return Chainable(_c2)
        
        p1 = P() | c1(1)
        self.assertEqual(p1, [1])

        p2 = P() | c2("chain")
        self.assertTrue(isinstance(p2, P))
        self.assertEqual(p2.data("hello"), "chain")


if __name__ == "__main__":
    unittest.main()