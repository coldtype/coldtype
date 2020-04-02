from coldtype import *
from coldtype.color import Gradient
from random import randint
from functools import partial
from pprint import pprint

varfont = Font("ç/MutatorSans.ttf")
coldtype_obvs_ufo = Font("ç/ColdtypeObviously_CompressedBlackItalic.ufo")

try:
    vinila_hvar = Font("≈/Vinila-VF-HVAR-table.ttf")
    vinila_no_hvar = Font("≈/VinilaVariable.ttf")
except:
    pass

page = Rect(1920, 1080)

def basic_test(r):
    return Slug("COLDTYPE", Style(varfont, 300, wdth=0, wght=1)).pens().f(1, 0, 0.5).align(r)

def combine_slugs_test(r):
    ss1 = Slug("OY ", Style(varfont, fontSize=280)).pen().f("darkorchid", 0.3)
    print(ss1.f())
    ps2 = Slug("ABC ", Style(varfont, wght=1, fontSize=230)).pens().rotate(-10)
    shape = DATPen().polygon(3, Rect(0, 0, 150, 150)).f("random")
    return DATPenSet(ss1, ps2, shape).distribute().align(r)

async def multilang_test():
    latin_font = await Font.Preload("ç/NotoSans-Black.ttf")
    arabic_font = await Font.Preload("≈/GretaArabicCompressedAR-Heavy.otf")
    latin_style = Style(latin_font, 180, fill=(1, 0, 0.5))
    arabic_style = Style(arabic_font, 350, lang="ar", fill=Gradient.Random(page))

    _s = ["(جاف + رطب (ما قبل", "+بوابة", "Left الملخبط Right", "9رقمي: سنوات ال 0", "ميد/سايد"]

    #for c in _s[3]:
    #    print(c)
    
    segs = SegmentedString(_s[2], dict(Arab=arabic_style, Latn=latin_style))
    ss = Lockup(segs.styled_strings).pens().align(page)
    return ss
    #dps = StyledString(_s[2], style).pens().align(page) #.fit(page.w - 100).pens().align(page)
    #return [dps.frameSet().attr(fill=None, stroke=0), dps]

def cjk_multilang_test(r):
    obv = Style(varfont, 300, wdth=1, wght=0, fill=(1, 0, 0.5))
    style = Style("ç/NotoSansCJKsc-Black.otf", 300, lang="zh", fill=Gradient.Random(r))
    dps = Slug("BPM同步", style, obv).fit(r.w-100).pens().align(r)
    return [dps.frameSet().attr(fill=None, stroke=0), dps]

async def emoji_test():
    twemoji = Font("ç/TwemojiMozilla.ttf")
    await twemoji.load()
    ps = StyledString("🍕💽🖥", Style(twemoji, 350, t=20, ch=500, bs=11)).pens().align(page, tv=1)
    print(ps[0].frame)
    return ps, ps.frameSet()
    #print(fs[0].bounds())
    #return ps, ps.frameSet()

async def color_font_test():
    bungee = Font("≈/PappardelleParty-VF.ttf")
    await bungee.load()
    ps = StyledString("COLDTYPE!", Style(bungee, 550, palette=5)).pens().align(page)
    print(ps[0].frame)
    return ps, ps.frameSet()

def multiline_test(r):
    style = Style(varfont, 300, wdth=1, wght=1, fill=0)
    graf = Graf(Lockup.TextToLines("Hello\nWorld".upper(), style), r.inset(200), leading=100)
    graf.fit()
    return graf.pens().align(r)

def language_hb_test(r):
    """Should have an accent over the j"""
    style = Style("ç/SourceSerifPro-Black.ttf", 350, wdth=1, wght=1, ss01=True)
    return Slug("ríjks б", style.mod(lang="nl")).pen().align(r)

def interp_test(r):
    l = 30
    dps = DATPenSet()
    for x in range(l):
        style = Style(varfont, 350, wdth=x/l, wght=0, fill=(0, 0.2))
        dps.append(Slug("HELLO", style).pen().align(r).removeOverlap())
    return dps

def layering_test(r):
    def layerer(ss, gn, dp, dps):
        dps[0].f(1, 0, 0.5)
        dps.insert(0, dp.copy().f(0).translate(70, -70))
        dps.insert(0, dp.copy().f(0, 1, 0).translate(-70, 70))
    return Slug("HELLO", Style(varfont, 300, wdth=1, wght=1, t=-100, reverse=1, layerer=layerer)).pens().align(r)

def interleaving_test(r):
    return Slug("HELLO", Style(varfont, 300, wdth=1, wght=1, t=-100, reverse=1)).pens().align(r).f(0).interleave(lambda p: p.f(None).s("random").sw(50))

def db_fmt_test(r):
    p1 = Slug("A"*5, Style(varfont, 300, fill=0, wdth=1, db=1)).pen().align(r)
    return p1

def gradient_test(r):
    dp1 = StyledString("COLD", Style(varfont, 590, wght=1)).pen().align(r)
    dp2 = StyledString("TYPE", Style(varfont, 550, t=200)).pen().align(r)
    dp1.removeOverlap().attr(fill="random")
    dp2.attr(fill=Gradient.Random(r)).rotate(5).translate(10, 0)
    return [
        dp1.f(None).s("random").sw(10),
        dp2.intersection(dp1),
    ]

def roughen_test(r):
    return StyledString("O", Style(varfont, 900, wdth=1, wght=1)).pen().align(r, tv=1).removeOverlap().flatten(10).roughen(10).smooth().f(None).s("random").sw(10)

def pixellate_test(r):
    """Currently not great"""
    return StyledString("TXT", Style(varfont, 750, wdth=0, wght=1, filter=lambda idx, gn, fr, p: p.pixellate(r, inset=10))).pen().align(r, tv=1)

def text_on_curve_test(r):
    ss = Slug("California".upper(), Style(varfont, 390, t=20, fill=0))
    r = r.inset(50, 0).take(180, "centery")
    dp = DATPen(fill=None, stroke=("random", 0.3), strokeWidth=10).quadratic(r.p("SW"), r.p("C").offset(0, 300), r.p("NE"))
    ps = ss.pens()
    ps.distributeOnPath(dp)
    return [ps, ps.frameSet(th=True, tv=True), dp]

def pathops_test(r):
    square = DATPen().rect(r.inset(200).square()).translate(-100, -100)
    circle = DATPen().oval(r.inset(200).square()).translate(100, 100)
    return square.intersection(circle)

def catmull_test(r):
    dp = DATPen()
    points = []
    last_pt = (0, 0)
    for x in range(0, 10):
        too_close = True
        while too_close:
            pt = (randint(0, r.w), randint(0, r.h))
            if abs(last_pt[0] - pt[0]) > 100 and abs(last_pt[1] - pt[1]) > 100:
                too_close = False
            last_pt = pt
        points.append(last_pt)
    return dp.catmull(points).endPath().f(None).s("random").sw(20)

def map_points_test(r):
    pt_labels = DATPenSet()
    def point_mapper(idx, x, y):
        pt_labels.append(StyledString(str(idx), Style("ç/NotoSans-Black.ttf", 20, wght=1, wdth=0)).pen().translate(x, y))
        if idx in [12, 11]:
            return x+200, y
        elif idx in [7, 6]:
            return x+50, y
    e = StyledString("E", Style(varfont, 500, ro=1, wdth=1, wght=1)).pen().align(r).map_points(point_mapper)
    return e, pt_labels.f(0, 0.5)

def explode_test(r):
    o_o, o_i = StyledString("O", Style(varfont, 500, wdth=1, wght=1)).pen().align(r, tv=1).explode()
    o_i.f(1, 0, 0.5).rotate(90).translate(20, 0)
    o_o.f("random", 0.5)
    return o_o, o_i

def varfit_simple_test(r):
    fw = 800
    ss = StyledString("HELLO WORLD", Style(varfont, 300, wdth=1, wght=0.25, t=50, tl=-100, r=1, ro=1)).fit(fw).pens().align(r).f(0).understroke(s=1)
    return DATPen().f("random", 0.5).rect(r.take(fw, "centerx")), ss

text = """ABRACADABRA
SALT PEANUTS
VARIABILITY
AND A LONGER LINE, TO TEST TRACKING
AND A SHORTER LINE"""

def varfit_test(r):
    s = Style(varfont, 300, wdth=1, wght=0, t=200, tl=-10, varyFontSize=1, fill=1, r=1, ro=1)
    #ss = Graf(Slug.LineSlugs(.upper(), s), r.take(1000, "centerx"), leading=10).fit()
    #ssp = ss.pens().align(r)
    sss = []
    for line in text.upper().split("\n"):
        sss.append(StyledString(line, s))
    ssp = Graf(sss, r.take(1000, "centerx"), leading=10).fit().pens().align(r)
    return [
        #DATPen().rect(r.take(1000, "centerx")).f(0.5, 0, 1, 0.3),
        ssp.interleave(lambda p: p.s(0).sw(5))
    ]

def align_test(r):
    r = r.take(1000, "centerx")
    s = Style("ç/NotoSans-Black.ttf", 100)
    g = Graf(Slug.LineSlugs("HEADLINES\nUSED TO\nDO THIS", s), r.inset(0, 0), leading=10).pens().f(0).align(r)
    g[1].xAlignToFrame("centerx")
    g[2].xAlignToFrame("maxx")
    return DATPen().rect(r).f(0.5, 0, 1, 0.3), DATPen().rect(g[1].getFrame(th=0)).f("random", 0.63), g

def gx_hvar_test(r):
    wdth = 1
    return [StyledString("Hello", Style(vinila_hvar, 500, wdth=wdth)).pen().align(r), StyledString("Hello", Style(vinila_no_hvar, 500, wdth=wdth)).pen().align(r).translate(10, 10).f("random", 0.5)]

def ufo_test(r):
    return StyledString("COLDTYPE", Style(coldtype_obvs_ufo, 900, tu=0, ro=1)).pens().align(page).f("random", 0.5).s("random")

def family_wdth_test():
    arab = Style("≈/GretaArabicCondensedAR-Light.otf", 100, narrower=Style("≈/GretaArabicCompressedAR-Light.otf", 100))
    latn = Style("≈/ObviouslyVariable.ttf", 100, wdth=1)
    ss = SegmentedString("Left الملخبط Right", dict(Arab=arab, Latn=latn))
    ss.fit(2000)
    pprint(ss.segment_data)
    return ss.pens().align(page)


all_tests = [
    basic_test,
    combine_slugs_test,
    multilang_test,
    cjk_multilang_test,
    emoji_test,
    multiline_test,
    language_hb_test,
    interp_test,
    layering_test,
    interleaving_test,
    db_fmt_test,
    gradient_test,
    roughen_test,
    pixellate_test,
    text_on_curve_test,
    pathops_test,
    catmull_test,
    map_points_test,
    explode_test,
    varfit_simple_test,
    varfit_test,
    align_test,
    gx_hvar_test,
    ufo_test,
]

def render(r, i):
    res = tests[i](r)
    return [
        DATPen().rect(r).f(1),
        DATPen().gridlines(r, y=12).s((1, 0, 0.5, 0.2)).sw(5),
        DATPen().rect(r).f(None).s(0, 0.5, 1, 0.3).sw(20),
        DATPenSet(res)
    ]

renders = [
    family_wdth_test
]

#tests = [emoji_test]
#
#renders = []
#for idx, _ in enumerate(tests):
#    renders.append(partial(render, page, idx))