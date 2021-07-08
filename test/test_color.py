import unittest
from coldtype.color import *

class TestColor(unittest.TestCase):
    def test_interp(self):
        _hsl = hsl(0.1).hsl_interp(0, hsl(0.9))
        self.assertAlmostEqual(_hsl.hp, 0.1)

        _hsl = hsl(0.1).hsl_interp(1, hsl(0.9))
        self.assertAlmostEqual(_hsl.hp, 0.9)

        _hsl = hsl(0.2).hsl_interp(0.5, hsl(0.6))
        self.assertAlmostEqual(_hsl.hp, 0.4)

if __name__ == "__main__":
    unittest.main()