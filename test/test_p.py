import unittest
from coldtype.runon.path import P

from fontTools.pens.recordingPen import RecordingPen

from coldtype.geometry import Point, Rect
from coldtype.text import StSt, Font, Glyphwise, Style


class TestRunonPath(unittest.TestCase):
    def test_init(self):
        r = P()
        self.assertIsInstance(r.v, RecordingPen)
        self.assertEqual(r.val_present(), False)

        r = P(P())
        self.assertIsInstance(r.v, RecordingPen)
        self.assertIsInstance(r[0].v, RecordingPen)

        r.index(0, lambda e: e.moveTo(0, 0))
        self.assertEqual(r.val_present(), False)
        self.assertEqual(r[0].val_present(), True)
        
        r = P(Rect(50, 50))
        self.assertEqual(r.v.value[0][-1][0], (0, 0))
        self.assertEqual(r.v.value[-2][-1][0], (0, 50))
        self.assertEqual(r.v.value[-1][0], "closePath")

        r = P(P(), P())
        self.assertEqual(len(r), 2)

        r = P([P()]*3)
        self.assertEqual(len(r), 3)
    
    def test_find(self):
        r = P(
            StSt("ABC", Font.MutatorSans(), 100),
            StSt("ABC", Font.MutatorSans(), 100))
        
        r.î([0, 1], lambda p: p.tag("first"))
        r.î([1, 1], lambda p: p.tag("second"))
        
        self.assertEqual(len(r.find({"glyphName":"A"})), 2)
        self.assertEqual(r.find_({"glyphName":"B"}).tag(), "first")
        self.assertEqual(r.find_({"glyphName":"B"}, index=1).tag(), "second")

        self.assertEqual(
            r.find_({"glyphName":"B"}).tag(),
            r.ffg("B").tag())
        
        self.assertNotEqual(r.ffg("B"), r.ffg("B", index=1))

        r.ffg("C", lambda e: e.tag("sizzler"))
        self.assertEqual(r[0][-1].tag(), "sizzler")
        self.assertEqual(r[-1][-1].tag(), None)

        self.assertEqual(len(r[-1]), 3)
        r.ffg("C", lambda e: e.delete(), index=1)
        r.deblank()
        self.assertEqual(len(r[-1]), 2)
    
    def test_collapse(self):
        r = P(
            StSt("ABC", Font.MutatorSans(), 100),
            StSt("DEF", Font.MutatorSans(), 100))
        
        self.assertEqual(len(r), 2)
        self.assertEqual(len(r[0]), 3)
        
        r.collapse()
        self.assertEqual(len(r), 6)
        self.assertEqual(len(r[0]), 0)

    def test_drawing_mixin(self):
        r = P()
        self.assertIsInstance(r._val, RecordingPen)
        self.assertEqual(len(r._val.value), 0)

        r.moveTo(0, 0)
        r.moveTo(Point(1, 1))
        r.moveTo((2, 2))

        self.assertEqual(
            [v[1][0] for v in r.v.value],
            [(0, 0), (1, 1), (2, 2)])
        
        r = (P()
            .moveTo(0, 0)
            .lineTo(10, 10)
            .lineTo(Point(0, 10))
            .lineTo((0, 5))
            .closePath())
        
        self.assertEqual(r.v.value, [
            ('moveTo', ((0, 0),)),
            ('lineTo', ((10, 10),)),
            ('lineTo', ((0, 10),)),
            ('lineTo', ((0, 5),)),
            ('closePath', ())
        ])

        r = (P()
            .rect(Rect(10, 10, 10, 10)))
        
        self.assertEqual(r.v.value, [
            ('moveTo', ((10, 10),)),
            ('lineTo', ((20, 10),)),
            ('lineTo', ((20, 20),)),
            ('lineTo', ((10, 20),)),
            ('closePath', ())
        ])

        r = (P()
            .oval(Rect(10, 10, 10, 10))
            .round())
        
        self.assertEqual(r.v.value, [
            ('moveTo', [(15, 10)]),
            ('curveTo', [(18, 10), (20, 12), (20, 15)]), 
            ('curveTo', [(20, 18), (18, 20), (15, 20)]), 
            ('curveTo', [(12, 20), (10, 18), (10, 15)]), 
            ('curveTo', [(10, 12), (12, 10), (15, 10)]), 
            ('closePath', [])
        ])
    
    def test_layout_mixin(self):
        r = StSt("AB C", Font.MutatorSans(), 100)
        self.assertEqual(r[2].data("glyphName"), "space")
        self.assertAlmostEqual(r[2].ambit().x, 84.3, 2)
        self.assertFalse(r[2].bounds().nonzero())
        r.translate(100, 0)
        self.assertAlmostEqual(r[2].ambit().x, 184.3, 2)
    
    def test_fx_mixin(self):
        r = StSt("ABC", Font.MutatorSans(), 100)

        self.assertEqual(r[0].data("glyphName"), "A")
    
        r = P(P(Rect(0, 0, 100, 100)))
        self.assertEqual(r.ambit().y, 0)
        r.translate(0, 100)
        self.assertEqual(r.ambit().y, 100)
        r.layer(1, 1)

        r.translate(0, 100)
        self.assertEqual(r.ambit().y, 200)
    
        r = StSt("B", Font.MutatorSans(), 100)
        
    def test_glyphwise(self):
        r = Glyphwise("ABC", lambda _: Style(Font.MuSan(), 100))
        self.assertIsInstance(r, P)

        r = Glyphwise("ABC\nDEF", lambda _: Style(Font.MuSan(), 100))
        self.assertIsInstance(r, P)

        r = Glyphwise("ABC\nDEF", lambda g: [Style(Font.MuSan(), 100), dict(wdth=g.e)])
        self.assertIsInstance(r, P)
    
    def test_mods(self):
        r = StSt("ABC", Font.MuSan(), 500, ro=1)
        self.assertEqual(
            r.index([1, 2]).v.value,
            r.index(1).index(2).v.value)
        
        before_rotate = r.index([1, 2]).bounds()
        before_frame = r.index([1]).ambit(tx=0, ty=0)

        r.ffg("B", lambda p: p.î(2, lambda c: c.rotate(-5)))

        self.assertNotEqual(before_rotate, r.î([1, 2]).bounds())
        self.assertEqual(before_frame, r.î(1).ambit())
    
    def test_empty(self):
        r = P()
        r.data(frame=Rect(0, 0, 100, 100))
        r.collapse()
        r.translate(10, 10)
        #print(r)

if __name__ == "__main__":
    unittest.main()