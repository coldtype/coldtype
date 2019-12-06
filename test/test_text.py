from coldtype.animation import *
from coldtype.color import Gradient

varfont = "ç/MutatorSans.ttf"

def basic_test(f):
    return [
        DATPen().oval(f.a.r).f(0, 0.1),
        Slug("COLDTYPE", Style(varfont, 300, wdth=0, wght=1)).pen().f(1, 0, 0.5).align(f.a.r),
    ]

def combine_slugs_test(f):
    ss1 = Slug("OY ", Style(varfont, fontSize=280)).pen().f("darkorchid", 0.3)
    ps2 = Slug("ABC ", Style(varfont, wght=1, fontSize=230)).pens().rotate(-10)
    shape = DATPen().polygon(3, Rect(0, 0, 150, 150)).f("random")
    dps = DATPenSet(ss1, ps2, shape).distribute().align(f.a.r)
    return dps

def multilang_test(f):
    obv = Style("ç/NotoSans-Black.ttf", 180, fill=(1, 0, 0.5))
    r = f.a.r
    _s = ["(جاف + رطب (ما قبل", "+بوابة", "Left الملخبط Right", "9رقمي: سنوات ال0"]
    style = Style("ç/NotoSansArabic-Black.ttf", 200, lang="ar", fill=Gradient.Random(f.a.r))
    dps = Slug(_s[-1], style, obv).fit(f.a.r.w - 100).pens().align(f.a.r)
    return [dps.frameSet().attr(fill=None, stroke=0), dps]

def cjk_multilang_test(f):
    obv = Style(varfont, 300, wdth=1, wght=0, fill=(1, 0, 0.5))
    style = Style("ç/NotoSansCJKsc-Black.otf", 300, lang="zh", fill=Gradient.Random(f.a.r))
    dps = Slug("BPM同步", style, obv).fit(f.a.r.w-100).pens().align(f.a.r)
    return [dps.frameSet().attr(fill=None, stroke=0), dps]

def emoji_test(f):
    ps = Slug("🍕💽 🖥", Style("ç/TwemojiMozilla.ttf", 350, t=20, ch=500, bs=11)).pens().align(f.a.r, tv=1).flatten()
    return [ps, ps.frameSet()]

def multiline_test(f):
    style = Style(varfont, 300, wdth=1, wght=1, fill=0)
    graf = Graf(Lockup.TextToLines("Hello\nWorld".upper(), style), f.a.r.inset(200), leading=100)
    graf.fit()
    return graf.pens().align(f.a.r)

def language_hb_test(f):
    """Should have an accent over the j"""
    style = Style("ç/SourceSerifPro-Black.ttf", 350, wdth=1, wght=1, ss01=True)
    return Slug("ríjks б", style.mod(lang="nl")).pen().align(f.a.r)

def interp_test(f):
    l = 30
    dps = DATPenSet()
    for x in range(l):
        style = Style(varfont, 350, wdth=x/l, wght=0, fill=(0, 0.2))
        dps.addPen(Slug("HELLO", style).pen().align(f.a.r).removeOverlap())
    return dps

def layering_test(f):
    def layerer(ss, gn, dp, dps):
        dps.pens[0].f(1, 0, 0.5)
        dps.pens.insert(0, dp.copy().f(0).translate(70, -70))
        dps.pens.insert(0, dp.copy().f(0, 1, 0).translate(-70, 70))
    return Slug("HELLO", Style(varfont, 300, wdth=1, wght=1, t=-100, reverse=1, layerer=layerer)).pens().align(f.a.r)

def interleaving_test(f):
    return Slug("HELLO", Style(varfont, 300, wdth=1, wght=1, t=-100, reverse=1)).pens().align(f.a.r).f(0).interleave(lambda p: p.f(None).s("random").sw(50))

def db_fmt_test(f):
    p1 = Slug("A"*5, Style(varfont, 300, fill=0, wdth=1, db=1)).pen().align(f.a.r)
    return p1

def gradient_test(f):
    dp1 = StyledString("COLD", Style(varfont, 590, wght=1)).pen().align(f.a.r)
    dp2 = StyledString("TYPE", Style(varfont, 550, t=200)).pen().align(f.a.r)
    dp1.removeOverlap().attr(fill="random")
    dp2.attr(fill=Gradient.Random(f.a.r)).rotate(5).translate(10, 0)
    return [
        dp1.f(None).s("random").sw(10),
        dp2.intersection(dp1),
    ]

def roughen_test(f):
    return StyledString("O", Style(varfont, 900, wdth=1, wght=1)).pen().align(f.a.r, tv=1).removeOverlap().flatten(10).roughen(10).smooth().f(None).s("random").sw(10)

def pixellate_test(f):
    """Currently not great"""
    return StyledString("TXT", Style(varfont, 750, wdth=0, wght=1, filter=lambda fr, p: p.pixellate(f.a.r, inset=10))).pen().align(f.a.r, tv=1)

def text_on_curve_test(f):
    ss = Slug("California".upper(), Style(varfont, 390, t=20, fill=0))
    r = f.a.r.inset(50, 0).take(180, "centery")
    dp = DATPen(fill=None, stroke=("random", 0.3), strokeWidth=10).quadratic(r.p("SW"), r.p("C").offset(0, 300), r.p("NE"))
    ps = ss.pens()
    ps.distributeOnPath(dp)
    return [ps, ps.frameSet(th=True, tv=True), dp]

tests = [
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
]

def render(f):
    res = tests[f.i](f)
    return [
        DATPen().rect(f.a.r).f(1),
        DATPen().gridlines(f.a.r, y=12).s((1, 0, 0.5, 0.2)).sw(5),
        DATPen().rect(f.a.r).f(None).s(0, 0.5, 1, 0.3).sw(20),
        DATPenSet(res)
    ]

current_tests = [tests.index(layering_test)]
current_tests = list(range(0, len(tests)))
timeline = Timeline(100, storyboard=current_tests)
animation = Animation(render, Rect(1920, 1080), timeline, bg=(1, 0))