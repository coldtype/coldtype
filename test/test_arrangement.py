import unittest
from coldtype.runon.arrangement import * #INLINE
from coldtype.geometry import Rect
from coldtype.text import StSt, Font

class TestArrangement(unittest.TestCase):
    def test_auto_recursion(self):
        l = Arrangement(Rect(500, 500))
        self.assertEqual(l.depth(), 0)
        self.assertEqual(l.v, l.r)
        self.assertEqual(l.v, l.rect)

        l.divide(0.5, "N")
        self.assertEqual(l.depth(), 1)
        self.assertEqual(l.rect.w, 500)
        self.assertEqual(l.rect.h, 500)
        self.assertEqual(l[0].rect.w, 500)
        self.assertEqual(l[0].rect.h, 250)
        self.assertEqual(l[1].rect.h, 250)

        l.divide(200, "W")
        self.assertEqual(l.depth(), 2)
        self.assertEqual(l.rect.w, 500)
        self.assertEqual(l.rect.h, 500)
        self.assertEqual(l[0].rect.w, 500)
        self.assertEqual(l[0].rect.h, 250)
        self.assertEqual(l[1].rect.h, 250)
        self.assertEqual(l[0][0].rect.w, 200)
        self.assertEqual(l[1][0].rect.w, 200)
        
        l[1][1].subdivide(3, "W")
        self.assertEqual(l[1][1][1].rect.w, 100)
    
    def test_duck(self):
        l = Arrangement(Rect(500, 500))
        l.grid(2, 2, "abcd")

        self.assertEqual(l.val_present(), False)
        self.assertEqual(l[0].tag(), "a")
        self.assertEqual(l[-1].tag(), "d")

        txt = (StSt("ASDF", Font.MutatorSans(), 50))
        self.assertEqual(txt.ambit().x, 0)
        
        txt1 = txt.copy().align(l["b"])
        txt2 = txt.copy().align(l["b"].rect)
        
        self.assertEqual(txt.ambit().x, 0)
        self.assertEqual(txt1.ambit().x, 333.725)
        self.assertEqual(txt2.ambit().x, 333.725)

if __name__ == "__main__":
    unittest.main()