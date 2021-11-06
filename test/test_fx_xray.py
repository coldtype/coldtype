import unittest
from coldtype import StSt, Font, Rect
from coldtype.fx.xray import *

r = Rect(1000, 1000)

class TestFXXray(unittest.TestCase):
    def test_lookup(self):
        t = StSt("A", Font.MutatorSans(), 1000).pen().fssw(-1, 0, 2)
        lk = skeletonLookup(t)
        t.align(r).picklejar(r)
        
        self.assertEqual(len(lk["moveTo"]), 4)
        self.assertEqual(len(lk["lineTo"]), 12)
        self.assertEqual(len(lk["curveOn"]), 0)
        self.assertEqual(len(lk["qCurveOn"]), 0)

        t = StSt("B", Font.MutatorSans(), 1000).pen().fssw(-1, 0, 2)
        lk = skeletonLookup(t)
        t.align(r).picklejar(r)
        
        self.assertEqual(len(lk["moveTo"]), 2)
        self.assertEqual(len(lk["lineTo"]), 12)
        self.assertEqual(len(lk["curveOn"]), 0)
        self.assertEqual(len(lk["qCurveOn"]), 8)

        t = StSt("C", "assets/NotoSansCJKjp-Black.otf", 1000).pen().fssw(-1, 0, 2)
        lk = skeletonLookup(t)
        t.align(r).copy().layer(None, skeleton()).picklejar(r)
        
        self.assertEqual(len(lk["moveTo"]), 1)
        self.assertEqual(len(lk["lineTo"]), 2)
        self.assertEqual(len(lk["curveOn"]), 8)
        self.assertEqual(len(lk["qCurveOn"]), 0)

if __name__ == "__main__":
    unittest.main()