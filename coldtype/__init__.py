import math
import sys
import os
import re
import copy

name = "coldtype"
dirname = os.path.dirname(__file__)

from pprint import pprint
from pathlib import Path

if __name__ == "__main__":
    sys.path.insert(0, os.path.realpath(dirname + "/.."))

from coldtype.beziers import CurveCutter, raise_quadratic
from coldtype.color import normalize_color
from coldtype.pens.datpen import DATPen, DATPenSet
from coldtype.geometry import Rect, Point
from coldtype.text.shaper import segment

from coldtype.text.style import Style, StyledString, FittableMixin

try:
    # relies on undeclared dependencies
    from defcon import Font
    import glyphsLib
    from coldtype.pens import OutlinePen
except:
    pass



class GrafStyle():
    def __init__(self, leading=10, x="centerx", xp=0, **kwargs):
        self.leading = kwargs.get("l", leading)
        self.x = x
        self.xp = xp


class Graf():
    def __init__(self, lines, container, style=None, **kwargs):
        if isinstance(container, Rect):
            self.container = DATPen().rect(container)
        else:
            self.container = container
        if style and isinstance(style, GrafStyle):
            self.style = style
        else:
            self.style = GrafStyle(**kwargs)
        self.lines = lines
    
    def lineRects(self):
        # which came first, the height or the width???
        rects = []
        leadings = []
        box = self.container.getFrame()
        leftover = box
        for l in self.lines:
            box, leftover = leftover.divide(l.height(), "maxy")
            if self.style.leading < 0:
                # need to add pixels back to leftover
                leftover.h += abs(self.style.leading)
            else:
                leading, leftover = leftover.divide(self.style.leading, "maxy")
                leadings.append(leading)
            rects.append(box)
        return rects
    
    def width(self):
        return max([l.width() for l in self.lines])

    def fit(self):
        rects = self.lineRects()
        for idx, l in enumerate(self.lines):
            l.fit(rects[idx].w - self.style.xp)
        return self
    
    def pens(self):
        rects = self.lineRects()
        pens = DATPenSet()
        for idx, l in enumerate(self.lines):
            r = rects[idx]
            dps = l.pens().translate(r.x, r.y)
            dps.container = r
            dps.align(dps.container, x=self.style.x, y=None)
            pens.pens.append(dps)
        return pens
    
    def fpa(self, rect=None):
        return self.fit().pens().align(rect or self.container.getFrame())


class Lockup(FittableMixin):
    def __init__(self, slugs, preserveLetters=True, nestSlugs=True):
        self.slugs = slugs
        self.preserveLetters = preserveLetters
        self.nestSlugs = nestSlugs
    
    def width(self):
        return sum([s.width() for s in self.slugs])
    
    def height(self):
        return max([s.height() for s in self.slugs])
    
    def textContent(self):
        return "/".join([s.textContent() for s in self.slugs])

    def shrink(self):
        adjusted = False
        for s in self.slugs:
            adjusted = s.shrink() or adjusted
        return adjusted

    def pens(self):
        pens = []
        x_off = 0
        for s in self.slugs:
            x_off += s.margin[0]
            if self.preserveLetters:
                dps = s.pens()
                dps.translate(x_off, 0)
                if self.nestSlugs:
                    pens.append(dps)
                else:
                    pens.extend(dps.pens)
            else:
                dps = s.pen()
                dps.translate(x_off, 0)
                pens.append(dps)
            x_off += dps.getFrame().w
            x_off += s.margin[1]
            x_off += s.strings[-1].tracking
        return DATPenSet(pens)
    
    def pen(self):
        return self.pens().pen()
    
    def TextToLines(text, primary, fallback=None):
        lines = []
        for line in text.split("\n"):
            lines.append(Lockup([Slug(line, primary, fallback)]))
        return lines
    
    def SlugsToLines(slugs):
        return [Lockup([slug]) for slug in slugs]


def T2L(text, primary, fallback=None):
    return Lockup.TextToLines(text, primary, fallback)


class Slug(FittableMixin):
    def __init__(self, text, primary, fallback=None, margin=[0, 0]):
        self.text = text
        self.primary = primary
        self.fallback = fallback
        self.margin = margin
        self.strings = []
        self.tag()
    
    def tag(self):
        if self.fallback:
            segments = segment(self.text, "LATIN")
            self.strings = [StyledString(s[1], self.fallback if "LATIN" in s[0] else self.primary) for s in segments]
        else:
            self.strings = [StyledString(self.text, self.primary)]
    
    def width(self):
        return sum([s.width() for s in self.strings])
    
    def height(self):
        return max([s.style.capHeight*s.scale() for s in self.strings])
    
    def textContent(self):
        return "-".join([s.textContent() for s in self.strings])

    def shrink(self):
        adjusted = False
        for s in self.strings:
            adjusted = s.shrink() or adjusted
        return adjusted

    def pens(self, atomized=True):
        pens = DATPenSet()
        x_off = 0
        for s in self.strings:
            #x_off += s.margin[0]
            if atomized:
                dps = s.pens(frame=True)
                if dps.layered:
                    pens.layered = True
                dps.translate(x_off, 0)
                pens.pens.extend(dps.pens)
                x_off += dps.getFrame().w
            else:
                dp = s.pen(frame=True)
                dp.translate(x_off, 0)
                pens.pens.append(dp)
                x_off += dp.getFrame().w
            #x_off += dps.getFrame().w
            #x_off += s.margin[1]
        return pens
        #return DATPenSet([s.pens(frame=True) for s in self.strings])
    
    def pen(self):
        return self.pens(atomized=False).pen()





if __name__ == "__main__":
    from coldtype.color import Gradient
    from coldtype.viewer import previewer
    from random import randint
    from coldtype.pens.svgpen import SVGPen

    def basic_test(preview):
        r = Rect((0, 0, 500, 200))
        p1 = Slug("Coldtype!", Style("/Library/Fonts/Zapfino.ttf", 48, fill="random")).pen().align(r)
        p2 = DATPen().rect(r).attr(fill=1)
        preview.send(SVGPen.Composite([p2, p1], r), r)
    
    def ss_bounds_test(font, preview):
        #f = f"≈/{font}.ttf"
        f = font
        r = Rect((0, 0, 700, 120))
        ss = StyledString("ABC", font=f, fontSize=100, variations=dict(wght=1, wdth=1,  scale=True), features=dict(ss01=True))
        dp = ss.pen()
        dp.translate(20, 20)
        #r = svg.rect.inset(50, 0).take(180, "centery")
        #dp.align(r)
        dpf = DATPen(fill=None, stroke=dict(color=("random", 0.5), weight=4))
        for f in ss._frames:
            dpf.rect(f.frame)
        dpf.translate(20, 20)
        if "HVAR" in ss.ttfont:
            #print(ss.ttfont["HVAR"], font)
            pass
        else:
            print(">>>>>>>>>>>>>>>>>>>> NO HVAR", font)
        preview.send(SVGPen.Composite([dp, dpf], r), r)
    
    def ss_and_shape_test(preview):
        r = Rect((0, 0, 500, 120))
        f, v = ["≈/Nonplus-Black.otf", dict()]
        ss1 = Slug("Yoy! ", Style(font=f, variations=v, fontSize=80, baselineShift=5))
        f, v = ["¬/Fit-Variable.ttf", dict(wdth=0.1, scale=True)]
        ps2 = Slug("ABC", Style(font=f, variations=v, fontSize=72)).pens().rotate(-10)
        oval = DATPen().polygon(3, Rect(0, 0, 50, 50)).attr(fill="random")
        ss1_p = ss1.pen().attr(fill="darkorchid")
        #print(ss1_p.frame)
        dps = DATPenSet(
            ss1_p,
            ps2,
            oval
            )
        dps.distribute()
        dps.align(r)
        preview.send(SVGPen.Composite(dps.pens + [DATPen.Grid(r, y=4)], r), r)

    def rotalic_test(preview):
        r = Rect(0, 0, 500, 200)
        ps = Slug("Side", Style("≈/Vinila-VF-HVAR-table.ttf", 200, variations=dict(wdth=0.5, wght=0.7, scale=True))).pens().rotate(-15).align(r)
        preview.send(SVGPen.Composite(
            [DATPen.Grid(r)] + 
            ps.pens + 
            ps.frameSet().pens, r), r)

    def multilang_test(p):
        obv = Style("≈/ObviouslyVariable.ttf", 80, wdth=1, wght=0.7, fill=(1, 0, 0.5))
        r = Rect((0, 0, 600, 140))
        _s = [
            "(رطب (ما قبل",
            "(جاف + رطب (ما قبل",
            "+بوابة",
            "A الملخبط",
            "Ali الملخبط Boba",
            "الكروسفِيد",
            "مستوَى التخفيف",
            "اللٌُوفَاي",
            "9رقمي: سنوات ال0",
        ]
        style = Style("≈/GretaArabicCondensedAR-Heavy.otf",
                100,
                lang="ar",
                fill=Gradient.Random(r))
        lck = Slug(_s[-1], style, obv).fit(r.w - 100)
        dps = lck.pens()
        dps.align(r)
        g = DATPen.Grid(r, y=4)
        p.send(SVGPen.Composite([
            g,
            dps.frameSet().attr(fill=None, stroke=0),
            dps
            ], r), r)

    def cjk_multilang_test(p):
        obv = Style("≈/ObviouslyVariable.ttf", 80, wdth=1, wght=0.7, fill=(1, 0, 0.5))
        r = Rect((0, 0, 600, 140))
        _s = [
            "BPM同步"
        ]
        style = Style("≈/HiraginoSansGBW3.ttf",
                100,
                #lang="zh",
                fill=Gradient.Random(r))
        lck = Slug(_s[0], style, obv).fit(r.w - 100)
        dps = lck.pens()
        dps.align(r)
        g = DATPen.Grid(r, y=4)
        p.send(SVGPen.Composite([
            g,
            dps.frameSet().attr(fill=None, stroke=0),
            dps
            ], r), r)
    
    def tracking_test(p):
        r = Rect(0, 0, 500, 100)
        s1 = Slug("ABC", Style("≈/VulfSans-Medium.otf", 100, tracking=0, fill=("random", 0.2), strokeWidth=2, stroke=("random", 0.75)))
        s2 = Slug("xyz", Style("≈/VulfSans-Black.otf", 100, baselineShift=0, fill=("random", 0.1), strokeWidth=2, stroke=("random", 0.75)))
        ps1 = s1.pens()
        ps1.align(r)
        ps2 = s2.pens()
        ps2.align(r)
        frames = []
        p.send(SVGPen.Composite(
            frames + ps1.pens + ps2.pens + [DATPen.Grid(r, x=6, y=4)], r), r)

    def color_font_test(p):
        r = Rect(0,0,600,300)
        f = "≈/PappardelleParty-VF.ttf"
        t = "XYZ/yoyoma"
        st = Style(f, 300, palette=0, ss09=1)
        pprint(st.stylisticSets())
        ps = Slug(t, st).pens().align(r, tv=0).flatten()
        p.send(SVGPen.Composite([
            #ps.frameSet(),
            ps,
            ], r), r)

    def hoi_test(p):
        r = Rect(0,0,300,300)
        f = "≈/SpaceMonoHOI_2_cubic.ttf"
        st = Style(f, 100, wght=1, slnt=1, ital=0.65, ITA2=0.65, ITA3=0.65, MONO=1)
        ps = Slug("Ran", st).pen().align(r).attr(fill="random")
        p.send(SVGPen.Composite([ps], r), r)

    def emoji_test(p):
        r = Rect(0,0,500,200)
        f = "≈/TwemojiMozilla.ttf"
        t = "🍕💽 🖥"
        ps = Slug(t, Style(f, 100, t=20, ch=500, bs=11)).pens().align(r, tv=0).flatten()
        print("Layered", ps.layered)
        p.send(SVGPen.Composite([
            ps,
            ps.frameSet(),
            ], r), r)
    
    def ufo_test(p):
        r = Rect(0, 0, 500, 200)
        f = "~/Type/grafprojects/scratch2/megalodon.ufo"
        style = Style(f, 300, layer="person", fill=None, stroke=0, strokeWidth=1)
        slug = Slug("{megalodon}", style).fit(r.w)
        p.send(SVGPen.Composite(slug.pen().align(r, th=0), r), r)
    
    def glyphs_test(p):
        r = Rect(0, 0, 500, 200)
        f = "~/Downloads/vulf_compressor/vulf_compressor.glyphs"
        style = Style(f, 200, t=-10, varyFontSize=True)
        slug = Slug("ABC一低保真度", style).fit(r.w)
        p.send(SVGPen.Composite(slug.pen().align(r).removeOverlap().attr(fill="random"), r), r)
    
    def multiline_test(p):
        r = Rect(0, 0, 300, 300)
        f = "≈/ObviouslyVariable.ttf"
        style = Style(f, 50, wdth=1, wght=1, slnt=1, fill=0)
        graf = Graf(Lockup.TextToLines("Hello\n—\nYoyoyo\nMa", style), DATPen().rect(r.take(100, "centerx")))
        graf.fit()
        p.send(SVGPen.Composite(graf.pens().align(r), r), r, bg=1)
    
    def multiline_fit_test(p):
        r = Rect(0, 0, 300, 300)
        f = "≈/Vinila-VF-HVAR-table.ttf"
        style = Style(f, 50, wdth=1, wght=1, fill=0, ss01=True)
        pprint(style.stylisticSets())
        graf = Graf(Lockup.TextToLines("T\nI\nE\nM\nP\nO", style), DATPen().rect(r.take(30, "centerx")))
        graf.fit()
        p.send(SVGPen.Composite(graf.pens().align(r), r), r, bg=1)
    
    def language_hb_test(p):
        r = Rect(0, 0, 300, 100)
        f = "¬/SourceSerifPro-Black.ttf"
        style = Style(f, 50, wdth=1, wght=1, ss01=True)
        dp1 = Slug("ríjks б", style.mod(lang="nl")).pen().align(r)
        p.send(SVGPen.Composite(dp1, r), r)
    
    def custom_kern_test(p):
        f = "≈/VulfMonoLightItalicVariable.ttf"
        r = Rect(0, 0, 300, 100)
        style = Style(f, 50, wdth=0.2, kern=dict(eacute=[0, -300]))
        dp1 = Slug("stéréo", style).pen().attr(fill="random").align(r)
        p.send(SVGPen.Composite(dp1, r), r)
    
    def hwid_test(p):
        f = "≈/HeiseiMaruGothicStdW8.otf"
        r = Rect(0, 0, 300, 100)
        style = Style(f, 30, wdth=0.2, kern=dict(eacute=[0, -300]), bs=lambda i: randint(-20, 20))
        dp1 = Slug("イージーオペレーションディザー", style).fit(r.w).pen().align(r)
        p.send(SVGPen.Composite(dp1, r), r)
    
    def interp_test(p):
        f = "≈/ObviouslyVariable.ttf"
        r = Rect(0, 0, 700, 300)
        dps = DATPenSet()
        l = 30
        for x in range(l):
            style = Style(f, 272, wdth=x/l, wght=0, slnt=1, fill=(0, 0.2))
            dp = Slug("HELLO", style).pen().align(r).removeOverlap()
            dps.addPen(dp)
        p.send(SVGPen.Composite(dps, r), r, bg=1)
    
    def family_test(p):
        f = ["≈/Konsole/Konsole0.2-Wide.otf", "≈/Konsole/Konsole0.2-Regular.otf", "≈/Konsole/Konsole0.2-Compact.otf"]
        r = Rect(0, 0, 300, 100)
        style = Style(f, 60, fill=(1, 0, 0.5))
        dp1 = Slug("Hello world", style).fit(r.w).pen().align(r)
        p.send(SVGPen.Composite(dp1, r), r, bg=1)
    
    def layered_font_test(p):
        r = Rect(0, 0, 1000, 100)
        
        def layered_slugs(txt):
            return [
                Slug(txt, Style("≈/CaslonAntique-Shaded-Fill.otf", 60, fill=(1, 0, 0), t=-20)),
                Slug(txt, Style("≈/CaslonAntique-Shaded-Shadow.otf", 60, fill=(0, 0, 1), t=-20))
            ]
        
        s1, s2 = layered_slugs("Hello-----wor")
        s3, s4 = layered_slugs("ld")
        #dp1 = s1.pen().align(r, th=0)
        #dp2 = s2.pen().align(r, th=0)

        lck = Lockup([s1, s3])
        lck2 = Lockup([s2, s4])
        
        p.send(SVGPen.Composite([
            lck2.pens().align(r, th=0),
            lck.pens().align(r, th=0)
            ], r), r)
    
    def cache_width_test(p):
        #from itertools import chain
        #from fontTools.unicode import Unicode
        f = "~/Goodhertz/plugin-builder/configs/builder/design/GhzNumbersCompressed.ufo"
        r = Rect(0, 0, 300, 100)
        style = Style(f, 30)
        #glyphs = []
        #lookup = {}
        #for g in sorted(style.font, key=lambda g: g.name):
        #    lookup[g.name] = g.width
        #print(lookup)
        #print(style.font)
        #ttf = style.ttfont
        #print(style.ttfont["cmap"].tables)
        #chars = chain.from_iterable([y + (Unicode[y[0]],) for y in x.cmap.items()] for x in ttf["cmap"].tables)
        #for _, c, _ in sorted(set(chars)):
        #    print(c)
        gn = StyledString.TextToGuessedGlyphNames("1.23{uniE801}")
        print(gn)
        dp1 = Slug("1.23{uniE801}", style).fit(r.w).pen().align(r)
        p.send(SVGPen.Composite(dp1, r), r)
    
    def slnt_test(p):
        f = "≈/RoslindaleVariableItalicBeta-VF.ttf"
        r = Rect((0, 0, 500, 300))
        p1 = Slug("Coldtype", Style(f, 100, slnt=1, fill=0)).pen().align(r)
        p2 = DATPen().rect(r).attr(fill=1)
        p.send(SVGPen.Composite([p2, p1], r), r)
    
    def db_fmt_test(p):
        f = "≈/ClaretteGX.ttf"
        r = Rect((0, 0, 500, 300))
        p1 = Slug("A"*5, Style(f, 100, fill=0, wdth=1, ital=0, ss01=True, db=1)).pen().align(r)
        p2 = DATPen().rect(r).attr(fill=1)
        p.send(SVGPen.Composite([p2, p1], r, viewBox=True), max_width=500)

    with previewer() as p:
        if False:
            ss_bounds_test("≈/ObviouslyVariable.ttf", p)
            #ss_bounds_test("≈/MutatorSans.ttf", p)
            ss_bounds_test("≈/VinilaVariable.ttf", p)
            ss_bounds_test("≈/Vinila-VF-HVAR-table.ttf", p)
            #ss_bounds_test("≈/Compressa-MICRO-GX-Rg.ttf", p)
            #ss_bounds_test("≈/BruphyGX.ttf", p)
        
        ss_and_shape_test(p)
        #rotalic_test(p)
        #multilang_test(p)
        #cjk_multilang_test(p)
        #tracking_test(p)
        #color_font_test(p)
        #emoji_test(p)
        #hoi_test(p)
        #ufo_test(p)
        #glyphs_test(p)
        #multiline_test(p)
        #hwid_test(p)
        #multiline_fit_test(p)
        #language_hb_test(p)
        #custom_kern_test(p)
        #interp_test(p)
        #cache_width_test(p)
        #family_test(p)
        #layered_font_test(p)
        #basic_test(p)
        #slnt_test(p)
        #db_fmt_test(p)