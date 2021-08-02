import unittest
from pathlib import Path
from coldtype.geometry import *
from coldtype.color import hsl
from coldtype.pens.datpen import DPS
from coldtype.text.composer import StSt, Font, Style

tf = Path(__file__).parent

class TestText(unittest.TestCase):
    def _test_glyph_names(self, r, font_path):
        ss = StSt("CDELOPTY", font_path, 300, wdth=0).align(r)
        self.assertEqual(len(ss), 8)
        self.assertEqual(ss[0].glyphName, "C")
        self.assertEqual(ss[-1].glyphName, "Y")
        return ss

    def test_format_equality(self):
        r = Rect(800, 300)

        ttf = self._test_glyph_names(r, Font.ColdtypeObviously())
        otf = self._test_glyph_names(r, "assets/ColdtypeObviously_CompressedBlackItalic.otf")
        ufo = self._test_glyph_names(r, "assets/ColdtypeObviously_CompressedBlackItalic.ufo")
        ds = self._test_glyph_names(r, "assets/ColdtypeObviously.designspace")

        # TODO why isn't the ttf version equal to these?
        self.assertEqual(ufo[0].value, ds[0].value)
        self.assertEqual(ufo[-1].value, ds[-1].value)

        DPS([
            ttf, otf, ufo, ds
        ]).f(None).s(hsl(0.5, a=0.3)).sw(1).picklejar(r)
    
    def test_space(self):
        r = Rect(2000, 1000)

        txt = StSt("A B", Font.MutatorSans(), 1000)
        space = txt[1]
        self.assertEqual(space.glyphName, "space")
        self.assertEqual(space.ambit().w, 250)
        self.assertEqual(txt.ambit().w, 1093)
        self.assertEqual(space.ambit().x, 400)
        txt.align(r)
        self.assertEqual(space.ambit().x, 863.5)
        #txt.picklejar(r)

        txt = StSt("A B", Font.MutatorSans(), 1000, space=500)
        space = txt[1]
        self.assertEqual(space.glyphName, "space")
        self.assertEqual(space.ambit().w, 500)
        self.assertEqual(txt.ambit().w, 1093+250)
        self.assertEqual(space.ambit().x, 400)
        txt.align(r)
        self.assertEqual(space.ambit().x, 863.5-(250/2))
        #txt.picklejar(r)

    def test_static_fonts(self):
        r = Rect(1200, 300)
        f1 = Font.ColdtypeObviously()
        co = (StSt("CDELOPTY", f1, 200)
            .align(r)
            .picklejar(r))
        
        self.assertEqual(co.ambit(th=0).w, 998.8)
        self.assertAlmostEqual(co.ambit(th=1).w, 1018.8, 1)
        self.assertEqual(len(co), 8)
        self.assertEqual(f1.font.fontPath.stem, "ColdtypeObviously-VF")
    
    def test_color_font(self):
        txt = StSt("C", "~/Type/fonts/fonts/PappardelleParty-VF.ttf", 100, palette=2)
        self.assertEqual(len(txt), 1)
        self.assertEqual(len(txt[0]), 3)
        self.assertEqual(txt[0][0].glyphName, "C_layer_0")
        self.assertEqual(txt[0][-1].glyphName, "C_layer_2")
        self.assertAlmostEqual(txt[0][0].f().h, 176.666, 2)

        txt = StSt("C", "~/Type/fonts/fonts/PappardelleParty-VF.ttf", 100)
        self.assertAlmostEqual(txt[0][0].f().h, 196.318, 2)
    
    def test_narrowing_family(self):
        r = Rect(1080, 300)
        style = Style("~/Type/fonts/fonts/nikolai/Nikolai-Bold.otf", 200, narrower=Style("~/Type/fonts/fonts/nikolai/Nikolai-NarrowBold.otf", 200, narrower=Style("~/Type/fonts/fonts/nikolai/Nikolai-CondBold.otf", 200)))

        txt = StSt("Narrowing", style, fit=r.w)
        self.assertEqual(int(txt.ambit().w), 928)

        txt = StSt("Narrowing", style, fit=r.w-200)
        self.assertEqual(int(txt.ambit().w), 840)

        txt = StSt("Narrowing", style, fit=r.w-400)
        self.assertEqual(int(txt.ambit().w), 733)

        txt = StSt("Narrowing", style, fit=r.w-600)
        self.assertEqual(int(txt.ambit().w), 733)


if __name__ == "__main__":
    unittest.main()