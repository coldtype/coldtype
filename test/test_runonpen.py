import unittest
from coldtype.pens.runonpen import * #INLINE

from fontTools.pens.recordingPen import RecordingPen
from coldtype.geometry import Point, Rect

class TestRunon(unittest.TestCase):
    def test_init(self):
        r = RunonPen()
        self.assertIsInstance(r.v, RecordingPen)
        self.assertEqual(r.val_present(), False)

        r = RunonPen(RunonPen())
        self.assertIsInstance(r.v, RecordingPen)
        self.assertIsInstance(r[0].v, RecordingPen)

        r.index(0, lambda e: e.moveTo(0, 0))
        self.assertEqual(r.val_present(), False)
        self.assertEqual(r[0].val_present(), True)
        
        r = RunonPen(Rect(50, 50))
        self.assertEqual(r.v.value[0][-1][0], (0, 0))
        self.assertEqual(r.v.value[-2][-1][0], (0, 50))
        self.assertEqual(r.v.value[-1][0], "closePath")

        r = RunonPen(RunonPen(), RunonPen())
        self.assertEqual(len(r), 2)

        r = RunonPen([RunonPen()]*3)
        self.assertEqual(len(r), 3)

    def test_drawing_mixin(self):
        r = RunonPen()
        self.assertIsInstance(r._val, RecordingPen)
        self.assertEqual(len(r._val.value), 0)

        r.moveTo(0, 0)
        r.moveTo(Point(1, 1))
        r.moveTo((2, 2))

        self.assertEqual(
            [v[1][0] for v in r.v.value],
            [(0, 0), (1, 1), (2, 2)])
        
        r = (RunonPen()
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

        r = (RunonPen()
            .rect(Rect(10, 10, 10, 10)))
        
        self.assertEqual(r.v.value, [
            ('moveTo', ((10, 10),)),
            ('lineTo', ((20, 10),)),
            ('lineTo', ((20, 20),)),
            ('lineTo', ((10, 20),)),
            ('closePath', ())
        ])

        r = (RunonPen()
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

if __name__ == "__main__":
    unittest.main()