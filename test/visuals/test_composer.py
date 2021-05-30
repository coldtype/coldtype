from coldtype.test import *

text = """SALT PEANUTS
VARIABLE
LINEPACKING ALGORITHM
AND A LONGER LINE, TO TEST TRACKING
ISNT THIS WILD"""


@test()
def test_multiline_fit(r):
    # This is pretty janky atm
    lockups = Slug.LineSlugs(text, Style(mutator, 120, wdth=1, wght=1, varyFontSize=1, ro=1))
    return Graf(lockups, r, leading=20).fit(r.w-100).pens().map(lambda i,p: p.align(p.getFrame(), th=1, tv=1).track_to_rect(p.getFrame().inset(50, 0), pullToEdges=1).reversePens()).align(r).f(0)


@test()
def test_headline(r):
    s = Style("assets/SourceSerifPro-Black.ttf", 150)
    g = Graf(Slug.LineSlugs("HEADLINES\nUSED TO\nDO THIS", s), r, leading=10).pens().f(0)
    g[1].xAlignToFrame("mdx")
    g[2].xAlignToFrame("mxx")
    return g.align(r, th=0)


@test()
def test_combine_slugs(r):
    s1 = Slug("YO", Style(co, 300, wdth=1)).pens()
    line = DATPen().rect(Rect(100, 20))
    s2 = Slug("OY", Style(co, 300, wdth=0)).pens()
    shape = DATPen().oval(Rect(100, 100))
    return DATPens([s1, line, s2, shape]).distribute().align(r)


try:
    latin_font = Font("assets/NotoSans-Black.ttf")
    arabic_font = Font("≈/_i18n/GretaArabicCompressedAR-Heavy.otf")
    hebrew_font = Font("≈/_i18n/GretaSansCondensedH+L-Medium.otf")
except FontNotFoundException:
    pass


@test()
def test_multidir_seg_string(r):
    _s = ["(جاف + رطب (ما قبل", "+بوابة", "Left الملخبط Right", "90رقمي: سنوات ال", "ميد/سايد"]
    
    latin = Style(latin_font, 130, fill=("hr", 0.5, 0.5))
    arabic = Style(arabic_font, 150, lang="ar", fill=Gradient.Random(r), bs=-1)
    txt = _s[1]
    seg = SegmentedString(txt, dict(Arab=arabic, Latn=latin)).pens()
    slug = Slug(txt, arabic, latin).pens()
    return [
        seg.align(r).translate(0, 100),
        slug.align(r).translate(0, -100)
    ]


@test()
def test_hebrew(r):
    hebrew = Style(hebrew_font, 130, fill=hsl(0.5))
    slug = Slug('קומפרסיה ועוד', hebrew, fallback=Style(latin_font, 130))
    return slug.pens().align(r)


@test()
def test_cjk_multilang(r):
    obv = Style(co, 300, wdth=1, wght=0, fill=("hr",0.5,0.5))
    style = Style("assets/NotoSansCJKsc-Black.otf", 300, lang="zh", fill=Gradient.Random(r))
    dps = Slug("CO同步", style, obv).fit(r.w-100).pens().align(r)
    return [dps.frameSet().attr(fill=None, stroke=0), dps]


def xa(dps, x=Edge.CenterX, th=0):
    if dps._frame:
        return dps.align(dps.getFrame(th=th, tv=0), x=x, transformFrame=0, th=1)
    else:
        raise Exception("No Frame")

@test()
def test_ar_multiline(r):
    ar = 'Limmmm/Satلل\nوصل الإستيرِو'
    lines = ar.split("\n")
    latin = Style(latin_font, 100, fill=("hr", 0.5, 0.5))
    arabic = Style("≈/_i18n/GretaArabicCondensedAR-Light.otf", 150, lang="ar", fill=Gradient.Random(r), bs=-1)
    slugs = [
        Slug(lines[0], arabic, latin),
        Slug(lines[1], arabic, latin)
    ]
    graf = Graf(slugs, r, leading=30)
    dps = graf.pens()
    dps.map(lambda i,p: xa(p.pen()))
    #xa(dps[0])
    #xa(dps[1])
    #dps[0].xAlignToFrame("mdx")
    #dps[1].xAlignToFrame("mdx")
    dps.align(r)
    return [
        DATPen().rect(dps[0].getFrame()).f("random", 0.2),
        DATPen().rect(dps[1].getFrame()).f("random", 0.2),
        dps
    ]

@test()
def test_composer(r):
    return (Composer(r,
        "Hello\nWorld".upper(),
        Style(mutator, 150, wght=1),
        leading=20)
        .pens()
        .xa()
        .align(r))