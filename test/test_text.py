import unittest
from pathlib import Path
from coldtype.grid import Grid
from coldtype.geometry import *
from coldtype.text.composer import StSt
from coldtype.pens.svgpen import SVGPen

tf = Path(__file__).parent

class TestText(unittest.TestCase):
    def _test_glyph_names(self, font_path):
        ss = StSt("CDELOPTY", font_path, 100, wdth=0)
        ssps = ss#.pens()
        self.assertEqual(len(ssps), 8)
        self.assertEqual(ssps[0].glyphName, "C")
        self.assertEqual(ssps[-1].glyphName, "Y")

        fp = Path(font_path)
        op = (tf / f"ignorables/{fp.name}.svg")
        op.parent.mkdir(exist_ok=True)
        op.write_text(SVGPen.Composite(ssps, ssps.ambit(), viewBox=True))
        return ssps

    def test_format_equality(self):
        ttf = self._test_glyph_names("assets/ColdtypeObviously-VF.ttf")
        otf = self._test_glyph_names("assets/ColdtypeObviously_CompressedBlackItalic.otf")
        ufo = self._test_glyph_names("assets/ColdtypeObviously_CompressedBlackItalic.ufo")
        ds = self._test_glyph_names("assets/ColdtypeObviously.designspace")

        # TODO why isn't the ttf version equal to these?
        self.assertEqual(ufo[0].value, ds[0].value)
        self.assertEqual(ufo[-1].value, ds[-1].value)

if __name__ == "__main__":
    unittest.main()