import unittest
from pathlib import Path
from coldtype.grid import Grid
from coldtype.geometry import *
from coldtype.text.composer import StSt, Glyphwise, Style, Font
from coldtype.pens.draftingpens import DraftingPens
from coldtype.pens.svgpen import SVGPen

tf = Path(__file__).parent

class TestGlyphwise(unittest.TestCase):
    def _test_glyph_kerning(self, font_path, kern):
        ss = StSt("AVAMANAV", font_path, 100, wdth=0, kern=kern)
        gw = Glyphwise("AVAMANAV", lambda i, c: Style(font_path, 100, wdth=0, kern=kern))
        gwo = Glyphwise("AVAMANAV", lambda i, c: Style(font_path, 100, wdth=0, kern=(not kern)))

        self.assertEqual(len(ss), 8)
        self.assertEqual(ss[0].glyphName, "A")
        self.assertEqual(ss[-1].glyphName, "V")
        self.assertEqual(len(gw), 8)
        self.assertEqual(ss[0].glyphName, "A")
        self.assertEqual(ss[-1].glyphName, "V")

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

if __name__ == "__main__":
    unittest.main()