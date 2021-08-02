import unicodedata, unittest
from pathlib import Path
from coldtype.geometry import Rect
from coldtype.helpers import glyph_to_uni
from coldtype.pens.datpen import DATPen, DATPens
from coldtype.text.composer import StSt, Font, Style, Slug, Graf, SegmentedString

tf = Path(__file__).parent
co = Font.Cacheable("assets/ColdtypeObviously-VF.ttf")
mutator = Font.Cacheable("assets/MutatorSans.ttf")
zh = Font.Cacheable("assets/NotoSansCJKsc-Black.otf")

latin_font = Font("assets/NotoSans-Black.ttf")
arabic_font = Font("~/Type/fonts/fonts/_i18n/GretaArabicCompressedAR-Heavy.otf")
ar_light = Font("~/Type/fonts/fonts/_i18n/GretaArabicCondensedAR-Light.otf")
hebrew_font = Font("~/Type/fonts/fonts/_i18n/GretaSansCondensedH+L-Medium.otf")

r = Rect(1000, 500)

def gn_to_c(gn):
    return chr(int(gn.replace("uni", ""), 16))

def gn_to_uniname(gn):
    return unicodedata.name(gn_to_c(gn))

class TestI18N(unittest.TestCase):
    def test_mixed_lang_slug(self):
        obv = Style(co, 300, wdth=1, wght=0)
        style = Style(zh, 300, lang="zh")
        dps = (Slug("CO同步", style, obv)
            .fit(r.w-100)
            .pens()
            .align(r))
        
        self.assertEqual(
            dps[-1].ambit().round(),
            Rect([657,138,300,220]))
        
        self.assertEqual(dps[0].glyphName, "C")
        self.assertEqual(dps[1].glyphName, "O")
        self.assertEqual(dps[2].glyphName, "cid12378")
        self.assertEqual(dps[3].glyphName, "cid23039")
    
    def test_rtl_multiline(self):
        ar = 'Limmmm/Satلل\nوصل الإستيرِو'
        lines = ar.split("\n")
        latin = Style(latin_font, 100, fill=("hr", 0.5, 0.5))
        arabic = Style(ar_light, 150, lang="ar", bs=-1)
        slugs = [
            Slug(lines[0], arabic, latin),
            Slug(lines[1], arabic, latin)
        ]
        graf = Graf(slugs, r, leading=30)
        dps = graf.pens().xa().align(r)

        lgn = dps[-1][-1].glyphName
        lc = gn_to_c(lgn)
        
        self.assertEqual(
            unicodedata.name(lc),
            "ARABIC LETTER WAW")
        self.assertEqual(
            dps[-1][-1].ambit().round(),
            Rect([707,148,42,87]))
        
        self.assertEqual(dps[0][0].glyphName, "L")
        self.assertEqual(dps[0][-1].glyphName, "uniFEDF")
    
    def test_hebrew(self):
        hebrew = Style(hebrew_font, 130)
        slug = Slug('קומפרסיה ועוד', hebrew)
        dps = slug.pens().align(r)

        self.assertEqual(gn_to_c(dps[-1].glyphName), "ק")
        self.assertEqual(dps[-1].ambit().round(),
            Rect([719,212,52,76]))
    
    def test_multidir_seg_string(self):
        txt = "+بوابة"
    
        latin = Style(latin_font, 130, fill=("hr", 0.5, 0.5))
        arabic = Style(arabic_font, 150, lang="ar", bs=-1)
        seg = SegmentedString(txt, dict(Arab=arabic, Latn=latin)).pens()
        slug = Slug(txt, arabic, latin).pens()
        dps = DATPens([
            seg.align(r).translate(0, 100),
            slug.align(r).translate(0, -100)])
        
        self.assertEqual(dps[0][-1].glyphName, "plus")
        self.assertEqual(
            gn_to_uniname(dps[0][0].glyphName),
            "ARABIC LETTER TEH MARBUTA FINAL FORM")
        
        self.assertEqual(dps[1][0].glyphName, "plus")
        self.assertEqual(
            gn_to_uniname(dps[1][1].glyphName),
            "ARABIC LETTER TEH MARBUTA FINAL FORM")
        
    def test_combine_slugs(self):
        s1 = Slug("YO", Style(co, 300, wdth=1)).pens()
        line = DATPen().rect(Rect(100, 20))
        s2 = Slug("OY", Style(co, 300, wdth=0)).pens()
        shape = DATPen().oval(Rect(100, 100))
        dps = DATPens([s1, line, s2, shape]).distribute().align(r)
        self.assertEqual(dps.ambit().round(),
            Rect([127,138,737,225]))
        self.assertEqual(dps[1].ambit().round(),
            Rect([540,138,100,20]))
    
    def test_language_specific_forms(self):
        fnt = "assets/SourceSerifPro-Black.ttf"
        txt = StSt("ríjks", fnt, 350, lang="NLD")
        self.assertEqual(txt[1].glyphName, "iacute")
        self.assertEqual(txt[2].glyphName, "uni0237")
        txt = StSt("ríjks", fnt, 350)
        self.assertEqual(txt[1].glyphName, "iacute")
        self.assertEqual(txt[2].glyphName, "j")
    
    def test_language_specific_ufo(self):
        hershey_gothic = Font.Cacheable("~/Type/fonts/fonts/hershey/Hershey-TriplexGothicGerman.ufo")
        txt = StSt("Grieß".upper(), hershey_gothic, 200, tu=-100)
        self.assertEqual(len(txt), 6)
        self.assertEqual(txt[-1].glyphName, "S")
        self.assertEqual(txt[-2].glyphName, "S")


if __name__ == "__main__":
    unittest.main()