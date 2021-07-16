import unittest
from coldtype import Rect, Font, Style, DP, Path, hsl
from coldtype.text.richtext import RichText
from coldtype.remote import show_picklejar

f1 = Font("assets/ColdtypeObviously-VF.ttf")
f2 = Font("assets/MutatorSans.ttf")

class TestRichText(unittest.TestCase):
    def test_preserve_space(self):
        r = Rect(1200, 300)
        rt = RichText(r, "HELLO[i] COLDTYPE", dict(
            i=Style(f2, 200, wdth=0, wght=1),
            default=Style(f1, 200, wdth=0))).align(r)

        self.assertEqual(rt[0][0].data.get("txt"), "COLDTYPE")
        self.assertEqual(rt[0][1].data.get("txt"), "HELLO ")

        self.assertEqual(rt[0][1][0].glyphName, "space")
        self.assertEqual(rt[0][1][-1].glyphName, "H")

        self.assertEqual(rt[0][0][0].glyphName, "E")
        self.assertEqual(rt[0][0][-1].glyphName, "C")

        space_width = rt[0][1][0].ambit(th=0).w
        self.assertEqual(space_width, 50)

        self.assertGreater(
            rt[0][1].ambit(th=0).w - space_width,
            rt[0][1].ambit(th=1).w)
        
        rt.picklejar(r)

if __name__ == "__main__":
    unittest.main()