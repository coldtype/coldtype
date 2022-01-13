import unittest
from pathlib import Path
from coldtype.grid import Grid
from coldtype.geometry import *
from coldtype.color import hsl
from coldtype.text.composer import StSt, Glyphwise, Style, Font
from coldtype.runon.path import P
from coldtype.pens.svgpen import SVGPen

from coldtype.text.reader import ALL_FONT_DIRS
ALL_FONT_DIRS.insert(0, "~/Type/fonts/fonts")

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
            P([
                ss,
                gw.f(None).s(0).sw(5),
                gwo.copy().f(None).s(hsl(0.9)).sw(5),
            ]).translate(20, 20).scale(5, point=Point(0, 0)).picklejar(r, name=f"gw_kern_{kern}")

        self.assertEqual(ss.ambit(), gw.ambit())
        self.assertNotEqual(ss.ambit(), gwo.ambit())
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
        def print_e(g):
            es.append(g.e)
            return Style(fnt, 200, opsz=g.e, wdth=1-g.e)
        
        (Glyphwise("FATFACE 2 ARG", print_e)
            .align(r)
            .picklejar(r))
        
        self.assertEqual(es[0], 0)
        self.assertEqual(es[-1], 1)
    
    def test_newline(self):
        fnt = Font.Find("OhnoFatfaceV")
        r = Rect(1080, 300)
        
        gs = (Glyphwise("FATFACE\nFACEFAT", lambda g:
            Style(fnt, g.i*10+50, wdth=g.e))
            .align(r)
            .picklejar(r))
        
        self.assertEqual(gs[0][0].ambit().xy(),
            [305.21250000000003, 172.05])
        self.assertEqual(gs[1][-1].ambit().xy(),
            [656.3775, 58.650000000000006])
        self.assertEqual(gs[0][-1].glyphName, "E")
        self.assertEqual(gs[1][-1].glyphName, "T")
    
    def test_newline_onechar(self):
        fnt = Font.MutatorSans()
        r = Rect(1080, 300)
        
        gs = (Glyphwise("T\nYPE", lambda g:
            Style(fnt, 150-g.i*20, wdth=1-g.e))
            .xalign(r)
            .lead(20)
            .align(r)
            #.picklejar(r)
            )
        
        self.assertAlmostEqual(gs[0][0].ambit().xy(),
            [454.5, 153.0])
        self.assertEqual(gs[1][-1].ambit().xy(),
            [629.56, 42.0])
        self.assertEqual(gs[0][0].glyphName, gs[0][-1].glyphName)
        self.assertEqual(gs[0][0].glyphName, "T")
        self.assertEqual(gs[1][-2].glyphName, "P")
    
    def test_kp(self):
        fnt = Font.Find("OhnoFatfaceV")
        r = Rect(1080, 300)

        gs_no_kp = (Glyphwise("FATFACE", lambda g:
            Style(fnt, 250, wdth=1-g.e, ro=1))
            .align(r)
            .fssw(-1, 0, 1)
            .picklejar(r))
        
        gs_kp = (Glyphwise("FATFACE", lambda g:
            Style(fnt, 250, wdth=1-g.e, kp={"A/T":-250}, ro=1))
            .align(r)
            .fssw(-1, 0, 1)
            .picklejar(r))
        
        kp_sw = gs_kp[2].ambit().psw
        no_kp_sw = gs_no_kp[2].ambit().psw
    
        self.assertNotEqual(kp_sw, no_kp_sw)
        self.assertEqual(kp_sw.y, no_kp_sw.y)
    
    def test_tu(self):
        fnt = Font.Find("OhnoFatfaceV")
        r = Rect(1080, 300)

        gs_no_tu = (Glyphwise("FATFACE", lambda g:
            Style(fnt, 250, wdth=1-g.e, ro=1))
            .align(r)
            .fssw(-1, 0, 1)
            .picklejar(r))
        
        gs_tu = (Glyphwise("FATFACE", lambda g:
            Style(fnt, 250, wdth=1-g.e, tu=-50, ro=1))
            .align(r)
            .fssw(-1, 0, 1)
            .picklejar(r))
    
        self.assertLess(gs_tu.ambit().w, gs_no_tu.ambit().w)
    
    def test_multistyle(self):
        def styler1(g):
            return Style(Font.MutatorSans(), 100, wdth=0)
        
        def styler2(g):
            return [
                Style(Font.MutatorSans(), 100, wdth=0),
                Style(Font.MutatorSans(), 100, wdth=g.e),
            ]
        
        r = Rect(300, 100)
        g1 = (Glyphwise("ASDF", styler1)
            .fssw(-1, 0, 1)
            .picklejar(r))
        
        g2 = (Glyphwise("ASDF", styler2)
            .fssw(-1, 0, 1)
            .picklejar(r))
        
        self.assertEqual(g1.ambit().w, g2.ambit().w)
        self.assertNotEqual(g1.ambit(th=1).w, g2.ambit(th=1).w)

        self.assertEqual(g1[-1].glyphName, "F")
        self.assertEqual(g2[-1].glyphName, "F")
        self.assertEqual(g2[-1].data("frame").w, g1[-1].data("frame").w)
        self.assertEqual(g1[-1].ambit(th=1).w, 28.0)
        self.assertEqual(g2[-1].ambit(th=1).w, 86.0)
    
    def test_multiline(self):
        def styler(g):
            return Style(Font.MutatorSans(), 120,
                meta=dict(idx=g.i))
        
        gw = (Glyphwise("AB\nCD\nEF", styler)
            .collapse())
        
        for idx, g in enumerate(gw):
            self.assertEqual(g.data("idx"), idx)
    
    def test_no_reverse(self):
        def styler(g):
            return Style(Font.MutatorSans(), 120, r=1)
        
        with self.assertRaises(Exception) as context:
            (Glyphwise("AB\nCD\nEF", styler))
        
        self.assertIn("r=1 not possible", str(context.exception))

if __name__ == "__main__":
    unittest.main()