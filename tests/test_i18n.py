from coldtype.test import *
import unicodedata

co = Font.ColdObvi()
mutator = Font.MutatorSans()

zh = Font.Cacheable("assets/Noto-unhinted/NotoSansCJKsc-Black.otf")

latin_font = Font("assets/Noto-unhinted/NotoSans-Black.ttf")
arabic_font = Font.Find("GretaArabicCompressedAR-Heavy.otf")
ar_light = Font.Find("GretaArabicCondensedAR-Light.otf")
hebrew_font = Font.Find(r"GretaSansCondensedH\+L\-Medium\.otf")

fnt_en = Font.Cacheable("assets/SourceSerif4-VariableFont_opsz,wght.ttf")

r = Rect(1000, 500)

def gn_to_c(gn):
    return chr(int(gn.replace("uni", ""), 16))

def gn_to_uniname(gn):
    return unicodedata.name(gn_to_c(gn))

@test()
def test_mixed_lang_slug(_r):
    out = P()

    obv = Style(co, 300, wdth=1, wght=0, lang="en")
    style = Style(zh, 300, lang="zh")
    dps = (Slug("CO同步", style, obv)
        .fit(r.w-100)
        .pens()
        .align(r, tx=1))
    
    assert dps[-1].ambit().round() == Rect([657,138,300,220])
    
    assert dps[0].glyphName == "C"
    assert dps[1].glyphName == "O"
    assert dps[2].glyphName == "cid12378"
    assert dps[3].glyphName == "cid23039"
    assert dps.depth() == 1

    dps.attach(out)

    dps = (Slug("CO同步", style, obv)
        .fit(r.w-100)
        .pens(flat=False)
        .align(r, tx=1))
    
    assert dps[0].data("lang") == "en"
    assert dps[0][0].glyphName == "C"
    assert dps[0][1].glyphName == "O"

    assert dps[1].data("lang") == "zh"
    assert dps[1][0].glyphName == "cid12378"
    assert dps[1][1].glyphName == "cid23039"

    assert dps.depth() == 2

    dps.attach(out)

    return out.stack(100).align(_r).scale(0.25)

@test(100)
def test_mixed_lang_stst(_r):
    out = P()

    dps = (StSt("CO同步TY", zh, 300,
        lang="zh",
        fallback=Style(co, 300, wdth=1, wght=0, lang="en"),
        fit=r.w-100)
        .align(r, tx=1))
    
    dps[1].translate(10, 0)
    dps.attach(out)
    
    assert dps[1][-1].ambit().w == 300
    
    assert dps[0].data("lang") == "en"
    assert dps[0][0].glyphName == "C"
    assert dps[0][1].glyphName == "O"
    
    assert dps[1].data("lang") == "zh"
    assert dps[1][0].glyphName == "cid12378"
    assert dps[1][1].glyphName == "cid23039"

    assert dps[2].data("lang") == "en"
    assert dps[2][0].glyphName == "T"
    assert dps[2][1].glyphName == "Y"

    return out.align(_r).scale(0.25)

@test()
def test_rtl_multiline_stst(_r):
    out = P()

    txt = 'Limmmm/Satلل\nوصل الإستيرِو'
    arabic = Style(ar_light, 150, lang="ar", bs=-1,
        fallback=Style(latin_font, 100, fill=("hr", 0.5, 0.5)))
    
    dps = StSt(txt, arabic, leading=30).xalign(r).align(r)

    dps.attach(out)

    lgn = dps[-1][-1][-1].glyphName
    lc = gn_to_c(lgn)
    
    assert unicodedata.name(lc) == "ARABIC LETTER WAW"
    assert dps[-1][-1][-1].ambit().round() == Rect([707,148,42,87])
    
    assert dps[0][0][0].glyphName == "L"
    assert dps[0][1][-1].glyphName == "uniFEDF"

    return out.align(_r).scale(0.65)

@test((100))
def test_hebrew(_r):
    out = P()

    hebrew = Style(hebrew_font, 130)
    slug = Slug('קומפרסיה ועוד', hebrew)
    dps = slug.pens().align(r, tx=1).attach(out)

    assert gn_to_c(dps[-1].glyphName) == "ק"
    assert dps[-1].ambit().round() == Rect([719,212,52,76])

    return out.align(_r).scale(0.75)

@test()
def test_multidir_seg_string(_r):
    txt = "+بوابة"

    latin = Style(latin_font, 130, fill=("hr", 0.5, 0.5))
    arabic = Style(arabic_font, 150, lang="ar", bs=-1)
    seg = SegmentedString(txt, dict(Arab=arabic, Latn=latin)).pens()
    slug = Slug(txt, arabic, latin).pens()

    dps = P([
        seg.align(r, tx=1).translate(0, 100),
        slug.align(r, tx=1).translate(0, -100)])
    
    assert dps[0][-1].glyphName == "plus"
    assert gn_to_uniname(dps[0][0].glyphName) == "ARABIC LETTER TEH MARBUTA FINAL FORM"
    assert dps[1][0].glyphName == "plus"
    assert gn_to_uniname(dps[1][1].glyphName) == "ARABIC LETTER TEH MARBUTA FINAL FORM"

    return dps.align(_r).scale(0.5)
    
@test(150)
def test_combine_slugs(_r):
    s1 = Slug("YO", Style(co, 300, wdth=1)).pens()
    line = P().rect(Rect(100, 20))
    s2 = Slug("OY", Style(co, 300, wdth=0)).pens()
    shape = P().oval(Rect(100, 100))
    dps = P([s1, line, s2, shape]).distribute().align(r, tx=1)
    assert dps.ambit().round() == Rect([127,138,737,225])
    assert dps[1].ambit().round() == Rect([540,138,100,20])

    return dps.align(_r).scale(0.5)

@test(120)
def test_language_specific_forms(_r):
    out = P()
    txt = StSt("ríjks", fnt_en, 350, lang="NLD").attach(out)
    
    assert txt[1].glyphName == "iacute"
    assert txt[2].glyphName == "uni0237"
    txt = StSt("ríjks", fnt_en, 350).attach(out)
    assert txt[1].glyphName == "iacute"
    assert txt[2].glyphName == "j"

    return out.distribute().track(100).align(_r).scale(0.25)

@test(120)
def test_korean_fallback(_r):
    txt = Slug("사이드체인 HPF", Style(zh, 72), Style(fnt_en, 72, fill=hsl(0.3)), print_segments=True).pens().align(_r)
    
    assert txt[0].glyphName == "cid52858"
    assert txt[-1].glyphName == "F"
    
    return txt

@test(120)
def test_language_specific_ufo(_r):
    hershey_gothic = Font.Find("Hershey-TriplexGothicGerman.ufo")
    txt = StSt("Grieß".upper(), hershey_gothic, 200, tu=-100)
    assert len(txt) == 6
    assert txt[-1].glyphName == "S"
    assert txt[-2].glyphName == "S"

    return txt.outline(2).align(_r).scale(0.5)