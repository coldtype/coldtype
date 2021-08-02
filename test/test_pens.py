import unittest
from random import Random
from coldtype.geometry import Rect, Point
from coldtype.pens.draftingpen import DraftingPen
from coldtype.pens.draftingpens import DraftingPens
from coldtype.color import hsl, rgb
from coldtype.pens.drawablepen import DrawablePenMixin
from coldtype.renderer.reader import SourceReader
from coldtype.text.composer import StSt, Font

co = Font.Cacheable("assets/ColdtypeObviously-VF.ttf")
mutator = Font.Cacheable("assets/MutatorSans.ttf")

class TestDraftingPens(unittest.TestCase):
    def test_gs(self):
        r = Rect(0, 0, 100, 100)
        dps = DraftingPens()
        dp = (DraftingPen()
            .define(r=r)
            .gs("$r↖ $r↗ $r↙|↘|65 ɜ"))
        self.assertEqual(len(dp.value), 4)
        self.assertEqual(dp.value[-2][-1][0], Point(100, 35))
        self.assertEqual(dp.value[-1][0], "endPath")
        self.assertEqual(dp.unended(), False)
        dps.append(DraftingPens([dp]))
        self.assertEqual(len(dps.tree().splitlines()), 3)
        self.assertEqual(dps.tree().splitlines()[-1],
            " | | DraftingPen<4mvs:end/>")
        
    def test_gs_arrowcluster(self):
        r = Rect(100, 100)
        dp = (DraftingPen()
            .define(r=r)
            .gs("$r↖↗↘"))
        
        self.assertEqual(len(dp.value), 4)
        self.assertEqual(dp.value[0][-1][0], Point(0, 100))
        self.assertEqual(dp.value[1][-1][0], Point(100, 100))
        self.assertEqual(dp.value[2][-1][0], Point(100, 0))
    
    def test_gs_relative_moves(self):
        r = Rect(100, 100)
        dp = (DraftingPen()
            .define(r=r)
            .gs("$r↖ ¬OX50OY-50 §OY-50"))
        
        self.assertEqual(len(dp.value), 4)
        self.assertEqual(dp.value[0][-1][0], Point(0, 100))
        self.assertEqual(dp.value[1][-1][0], Point(50, 50))
        self.assertEqual(dp.value[2][-1][0], Point(0, 50))
    
    def test_gss(self):
        """
        A rect passed to gs and gss should create the same value on the pen
        """
        dp1 = (DraftingPen()
            .define(r=Rect(100, 100))
            .gss("$r"))
        
        dp2 = (DraftingPen()
            .define(r=Rect(100, 100))
            .gs("$r"))
        
        self.assertEqual(dp1.value, dp2.value)
        
    def test_reverse(self):
        dp = (DraftingPen()
            .define(r=Rect(100, 100))
            .gs("$r↖ $r↗ $r↘ ɜ"))
        p1 = dp.value[0][-1]
        p2 = dp.reverse().value[-2][-1]
        self.assertEqual(p1, p2)
    
    def test_transforms(self):
        dp = (DraftingPen(Rect(100, 100))
            .frame(Rect(100, 100))
            .align(Rect(200, 200)))
        
        self.assertEqual(dp.frame().mxx, 150)
        self.assertEqual(dp.value[-2][-1][-1][0], 50)

        self.assertEqual(
            dp.copy().rotate(45).round().value,
            dp.copy().rotate(360+45).round().value)
        
        self.assertEqual(dp.copy().scale(2).ambit().w, 200)

    def test_pens_ambit(self):
        dps = (DraftingPens([
                DraftingPen(Rect(50, 50)),
                DraftingPen(Rect(100, 100, 100, 100))])
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
        dps = (DraftingPens([
            DraftingPen(Rect(50, 50)),
            DraftingPen()
        ]))
        self.assertEqual(len(dps), 2)
        dps.remove_blanks()
        self.assertEqual(len(dps), 1)
    
    def test_collapse(self):
        dps = DraftingPens([
            DraftingPens([DraftingPens([DraftingPen()])]),
            DraftingPens([DraftingPen()]),
        ])

        dps.collapse() # should not mutate by default
        self.assertIsInstance(dps[0], DraftingPens)
        self.assertIsInstance(dps[0][0], DraftingPens)

        dps.collapse(onself=True) # now it should mutate
        self.assertEqual(len(dps), 2)
        self.assertNotIsInstance(dps[0], DraftingPens)
        self.assertNotIsInstance(dps[1], DraftingPens)
    
    def test_find(self):
        dps = DraftingPens([
            DraftingPens([DraftingPens([DraftingPen().tag("find-me").f(hsl(0.9))])]),
            DraftingPen().tag("not-me"),
            DraftingPens([DraftingPen().tag("find-me").f(hsl(0.3))])])

        self.assertEqual(dps.find("find-me")[0].f().h/360, 0.9)
        self.assertAlmostEqual(dps.find("find-me")[1].f().h/360, 0.3)

    def test_cond(self):
        dps = (DraftingPens([
            (DraftingPen().cond(True,
                lambda p: p.f(rgb(1, 0, 0))))]))
        
        self.assertEqual(dps[0].f().r, 1)

        def _build(condition):
            return (DraftingPens([
                (DraftingPen().cond(condition,
                    lambda p: p.f(rgb(0, 0, 1)),
                    lambda p: p.f(rgb(1, 0, 0))))]))
        
        self.assertEqual(_build(True)[0].f().b, 1)
        self.assertEqual(_build(False)[0].f().r, 1)
    
    def test_alpha(self):
        dps = (DraftingPens([
            (DraftingPens([
                (DraftingPen().a(0.5))
            ]).a(0.5))
        ]).a(0.25))

        def walker(p, pos, data):
            if pos == 0:
                self.assertEqual(data["alpha"], 0.0625)
            elif pos == 1 and data["depth"] == 0:
                self.assertEqual(data["alpha"], 0.25)
            elif pos == 1 and data["depth"] == 1:
                self.assertEqual(data["alpha"], 0.125)

        dps.walk(walker)
    
    def test_visibility(self):
        dps = (DraftingPens([
            (DraftingPens([
                (DraftingPen().v(1).tag("visible")),
                (DraftingPen().v(0).tag("invisible"))
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
        dps[0][0].v(0)
        dps.walk(walker, visible_only=True)
        self.assertEqual(visible_pen_count, 0)
    
    def test_style(self):
        src = """
from coldtype import *

def two_styles(r):
    return (DATPen()
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
    return (DATPen()
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
            rs[0][-1][0].attr(rs[0][0].style, "fill"),
            rs[1][-1][0].attr(rs[1][0].style, "fill"))
        
        self.assertNotEqual(
            rs[2][-1][0].attr(rs[2][0].style, "fill"),
            rs[3][-1][0].attr(rs[3][0].style, "fill"))
        
        self.assertEqual(rs[2][-1][0].attr(rs[2][0].style, "stroke").get("weight"), 5)
        self.assertEqual(rs[3][-1][0].attr(rs[3][0].style, "stroke").get("weight"), 15)

        dpm = DrawablePenMixin()
        dpm.dat = rs[3][-1][0]
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
        dps = DraftingPens([
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
        dps = DraftingPens()
        rnd = Random(0)
        r = Rect(1000, 500)

        for _ in range(0, 11):
            dps += (DraftingPen()
                .rect(Rect(100, 100))
                .f(hsl(rnd.random(), s=0.6))
                .rotate(rnd.randint(-45, 45)))
        dps = (dps
            .distribute()
            .track(-50)
            .reversePens()
            .understroke(s=0.2).align(r))
        
        self.assertEqual(len(dps), 22)
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


if __name__ == "__main__":
    unittest.main()