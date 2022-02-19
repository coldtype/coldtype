import unittest
from coldtype.geometry import Rect

class TestGeometry(unittest.TestCase):
    def test_rect(self):
        r = Rect(0, 0, 10, 10)
        self.assertEqual(r.xywh(), [0, 0, 10, 10])

        r = Rect(10, 10)
        self.assertEqual(r.xywh(), [0, 0, 10, 10])

        r = Rect(10)
        self.assertEqual(r.xywh(), [0, 0, 10, 10])

        r = Rect([0, 0, 10, 10])
        self.assertEqual(r.xywh(), [0, 0, 10, 10])

        r = Rect([10, 10])
        self.assertEqual(r.xywh(), [0, 0, 10, 10])

        r = Rect("letter")
        self.assertEqual(r.xywh(), [0, 0, 612, 792])
    
    def test_interpolate(self):
        a = Rect(0, 0, 500, 100)
        b = Rect(0, 0, 200, 100)
        i = a.interp(0.5, b)
        self.assertEqual(i.w, 200+(500-200)/2)
        self.assertEqual(i.h, 100)
        self.assertEqual(i.xy(), [0, 0])

if __name__ == "__main__":
    unittest.main()