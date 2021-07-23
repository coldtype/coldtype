import unittest
from pathlib import Path
from coldtype.grid import Grid
from coldtype.geometry import *
from coldtype.color import hsl
from coldtype.text.composer import StSt, Glyphwise, Style, Font
from coldtype.pens.draftingpens import DraftingPens
from coldtype.pens.svgpen import SVGPen

tf = Path(__file__).parent

class TestGlyphwise(unittest.TestCase):
    def _test_glyph_kerning(self, font_path, kern):
        txt = "AVAMANAV"
        #txt = "AVAV"
        ss = StSt(txt, font_path, 100, wdth=0, kern=kern)
        gw = Glyphwise(txt, lambda i, c: Style(font_path, 100, wdth=0, kern=kern, ro=1))
        gwo = Glyphwise(txt, lambda i, c: Style(font_path, 100, wdth=0, kern=(not kern), ro=1))

        #ss.picklejar(Rect(500, 100))
        #gw.picklejar(Rect(500, 100))
        #gwo.picklejar(Rect(500, 100))

        self.assertEqual(len(ss), len(txt))
        self.assertEqual(ss[0].glyphName, "A")
        self.assertEqual(ss[-1].glyphName, "V")
        self.assertEqual(len(gw), len(txt))
        self.assertEqual(ss[0].glyphName, "A")
        self.assertEqual(ss[-1].glyphName, "V")

        if True:
            r = Rect(1500, 500)
            DraftingPens([
                ss,
                gw.f(None).s(0).sw(5),
                gwo.copy().f(None).s(hsl(0.9)).sw(5),
            ]).translate(20, 20).scale(5, point=Point(0, 0)).picklejar(r)

        self.assertEqual(ss.ambit(), gw.ambit())
        self.assertNotEqual(ss.ambit(), gwo.ambit())

        fp = Path(font_path)
        op = (tf / f"ignorables/__{fp.name}.svg")
        op.parent.mkdir(exist_ok=True)
        op.write_text(SVGPen.Composite(DraftingPens([ss, gw.translate(0, 10)]), ss.ambit(), viewBox=True))

        return ss, gw

    def test_format_equality(self):
        fnt = "~/Type/fonts/fonts/OhnoFatfaceVariable.ttf"
        self._test_glyph_kerning(fnt, True)
        self._test_glyph_kerning(fnt, False)
    
    def test_ligature(self):
        clarette = Font.Cacheable("~/Type/fonts/fonts/_wdths/ClaretteGX.ttf")
        r = Rect(1080, 300)
        gl = (Glyphwise(["fi", "j", "o", "ff"],
            lambda i, c: Style(clarette, 200, wdth=1))
            .align(r))
        
        self.assertEqual(len(gl), 4)
        self.assertEqual(gl[0].glyphName, "f_i")
        self.assertEqual(gl[-1].glyphName, "f_f")
        gl.picklejar(r)

if __name__ == "__main__":
    unittest.main()