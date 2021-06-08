import unittest
from coldtype.geometry import Rect, Point
from coldtype.pens.draftingpen import DraftingPen
from coldtype.pens.draftingpens import DraftingPens
from coldtype.color import hsl, rgb

class TestDraftingPens(unittest.TestCase):
    def test_gs(self):
        r = Rect(0, 0, 100, 100)
        dps = DraftingPens()
        dp = (DraftingPen()
            .define(r=r)
            .gs("$r↖ $r↗ ↘|65|$r↙ ɜ"))
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

if __name__ == "__main__":
    unittest.main()