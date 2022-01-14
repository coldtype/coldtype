import unittest
from pathlib import Path
from coldtype.geometry import *
from coldtype.color import hsl
from coldtype.runon.path import P
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
        self.assertEqual(ufo[0].v.value, ds[0].v.value)
        self.assertEqual(ufo[-1].v.value, ds[-1].v.value)

        P([
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
        txt.align(r, th=1)
        self.assertEqual(space.ambit().x, 863.5)
        #txt.picklejar(r)

        txt = StSt("A B", Font.MutatorSans(), 1000, space=500)
        space = txt[1]
        self.assertEqual(space.glyphName, "space")
        self.assertEqual(space.ambit().w, 500)
        self.assertEqual(txt.ambit().w, 1093+250)
        self.assertEqual(space.ambit().x, 400)
        txt.align(r, th=1)
        self.assertEqual(space.ambit().x, 863.5-(250/2))
        #txt.picklejar(r)

    def test_static_fonts(self):
        r = Rect(1200, 300)
        f1 = Font.ColdtypeObviously()
        co = (StSt("CDELOPTY", f1, 200)
            .align(r)
            .picklejar(r))
        
        self.assertAlmostEqual(co.ambit(th=0).w, 998.8)
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
    
    def test_unstripped_text(self):
        st1 = StSt("HELLO\n", Font.MutatorSans(), 100)
        self.assertEqual(len(st1), len("HELLO"))
        st2 = StSt("HELLO\n", Font.MutatorSans(), 100, strip=False)
        self.assertEqual(len(st2), 2)
        st3 = st2.collapse().deblank()
        self.assertEqual(len(st3), len(st1))
        st4 = StSt("\n\nHELLO\n", Font.MutatorSans(), 100)
        self.assertEqual(len(st4), len("HELLO"))
        st5 = StSt("\n\nHEL\nL\nO\n", Font.MutatorSans(), 100)
        self.assertEqual(len(st5), 3)
    
    def test_zero_font_size(self):
        s = Style(Font.ColdtypeObviously(), 0)
        self.assertEqual(s.fontSize, 0)

        s = Style(Font.ColdtypeObviously(), -1)
        self.assertEqual(s.fontSize, 0)

        s = Style(Font.ColdtypeObviously(), -1000)
        self.assertEqual(s.fontSize, 0)

        st = StSt("COLD", Font.ColdtypeObviously(), 0)
        self.assertEqual(len(st), 4)
        self.assertEqual(st[0].glyphName, "C")
        self.assertEqual(st[-1].glyphName, "D")
    
    def test_strict_multiline_stst(self):
        st = (StSt("COLD", Font.ColdtypeObviously(), 100,
            multiline=1))
        
        self.assertEqual(len(st), 1)
        self.assertEqual(len(st[0]), 4)

        st = (StSt("COLD\nTYPE", Font.ColdtypeObviously(), 100,
            multiline=1))
        
        self.assertEqual(len(st), 2)
        self.assertEqual(len(st[1]), 4)

        st = (StSt("COLD\nTYPE", Font.ColdtypeObviously(), 100,
            multiline=0))
        
        self.assertEqual(len(st), 2)
        self.assertEqual(len(st[1]), 4)
    
    def test_depth(self):
        st = (StSt("These are some words", Font.RecursiveMono()))
        self.assertEqual(st.depth(), 1)

        st = (StSt("These are some words", Font.RecursiveMono(), multiline=1))
        self.assertEqual(st.depth(), 2)

        st = P([(StSt("These are some words", Font.RecursiveMono(), multiline=1))])
        self.assertEqual(st.depth(), 3)

        st = (StSt("These are some words\nbut now on multiple lines\nisn't that interesting", Font.RecursiveMono()))
        self.assertEqual(st.depth(), 2)
    
    def test_word_splitting(self):
        st = (StSt("These are some words", Font.RecursiveMono()))

        self.assertEqual(st.depth(), 1)
        self.assertEqual(st[0].glyphName, 'T')
        self.assertEqual(len(st), 20)

        st = st.wordPens()

        self.assertEqual(st.depth(), 1)
        self.assertEqual(
            st[0].data("word"),
            'T/h.italic/e.italic/s.italic/e.italic')
        
        self.assertEqual(len(st), 4)
        
        st = (StSt("These are some words", Font.RecursiveMono(), multiline=1))

        self.assertEqual(st.depth(), 2)
        self.assertEqual(st[0][0].glyphName, 'T')
        self.assertEqual(len(st[0]), 20)

        st = st.wordPens()
        self.assertEqual(st.depth(), 2)
        self.assertEqual(st[0][0].data("word"),
            'T/h.italic/e.italic/s.italic/e.italic')
        self.assertEqual(len(st[0]), 4)

        st = (StSt("These are\nsome words", Font.RecursiveMono()))

        self.assertEqual(st.depth(), 2)
        self.assertEqual(st[0][0].glyphName, 'T')
        self.assertEqual(len(st[0]), 9)

        st = st.wordPens()
        self.assertEqual(st.depth(), 2)
        self.assertEqual(st[-1][-1].data("word"),
            'w.italic/o/r.italic/d.italic/s.italic')
        self.assertEqual(len(st[0]), 2)


if __name__ == "__main__":
    unittest.main()