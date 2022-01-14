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

if __name__ == "__main__":
    unittest.main()