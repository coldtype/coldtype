import unittest
from coldtype.geometry import *
from coldtype.sh import sh

class TestTest(unittest.TestCase):
    def test_test(self):
        r = Rect(0, 0, 100, 100)
        self.assertEqual(sh(f"{r}TX=50"), [Rect([25.0,0,50,100])])
        self.assertEqual(sh("↗|65|10|↑"), [["NE", 65, 10, "N"]])

if __name__ == "__main__":
    unittest.main()