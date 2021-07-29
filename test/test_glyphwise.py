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
    def _test_glyph_kerning(self, font_path, kern, pj=False):
        txt = "AVAMANAV"
        #txt = "AVAV"
        ss = StSt(txt, font_path, 100, wdth=0, kern=kern)
        gw = Glyphwise(txt, lambda g: Style(font_path, 100, wdth=0, kern=kern, ro=1))
        gwo = Glyphwise(txt, lambda g: Style(font_path, 100, wdth=0, kern=(not kern), ro=1))

        self.assertEqual(len(ss), len(txt))
        self.assertEqual(ss[0].glyphName, "A")
        self.assertEqual(ss[-1].glyphName, "V")
        self.assertEqual(len(gw), len(txt))
        self.assertEqual(ss[0].glyphName, "A")
        self.assertEqual(ss[-1].glyphName, "V")

        if pj:
            r = Rect(1500, 500)
            DraftingPens([
                ss,
                gw.f(None).s(0).sw(5),
                gwo.copy().f(None).s(hsl(0.9)).sw(5),
            ]).translate(20, 20).scale(5, point=Point(0, 0)).picklejar(r, name=f"gw_kern_{kern}")

        self.assertEqual(ss.ambit(), gw.ambit())
        self.assertNotEqual(ss.ambit(), gwo.ambit())

        fp = Path(font_path)
        op = (tf / f"ignorables/__{fp.name}.svg")
        op.parent.mkdir(exist_ok=True)
        op.write_text(SVGPen.Composite(DraftingPens([ss, gw.translate(0, 10)]), ss.ambit(), viewBox=True))

        return ss, gw

    def test_format_equality(self):
        fnt = "~/Type/fonts/fonts/OhnoFatfaceVariable.ttf"
        self._test_glyph_kerning(fnt, False, pj=False)
        self._test_glyph_kerning(fnt, True, pj=True)
    
    def test_ligature(self):
        clarette = Font.Cacheable("~/Type/fonts/fonts/_wdths/ClaretteGX.ttf")
        r = Rect(1080, 300)
        gl = (Glyphwise(["fi", "j", "o", "ff"],
            lambda g: Style(clarette, 200, wdth=g.i/3))
            .align(r))
        
        self.assertEqual(len(gl), 4)
        self.assertEqual(gl[0].glyphName, "f_i")
        self.assertEqual(gl[-1].glyphName, "f_f")
        gl.picklejar(r)
    
    # def test_grouped(self):
    #     fnt = "~/Type/fonts/fonts/OhnoFatfaceVariable.ttf"
    #     r = Rect(1000, 200)
    #     gw = (Glyphwise(["AB", "CD"], lambda g:
    #         Style(fnt, 250, wdth=i, opsz=i))
    #         .align(r))
        
    #     gw.picklejar(r)

    def test_variable_args(self):
        fnt = Font.Find("OhnoFatfaceV")
        r = Rect(1080, 300)
        
        (Glyphwise("FATFACE 1 ARG", lambda g:
            Style(fnt, 200, wdth=g.e))
            .align(r)
            .picklejar(r))
        
        es = []
        def print_e(i, g):
            es.append(g.e)
            return Style(fnt, 200, opsz=g.e, wdth=1-g.e)
        
        (Glyphwise("FATFACE 2 ARG", print_e)
            .align(r)
            .picklejar(r))
        
        self.assertEqual(es[0], 0)
        self.assertEqual(es[-1], 1)

if __name__ == "__main__":
    unittest.main()