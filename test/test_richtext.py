from coldtype.test import *
from drafting.text.richtext import RichText, PythonCode
from functools import reduce


mistral = Font.Cacheable("~/Type/fonts/fonts/_script/MistralD.otf")
choc = Font.Cacheable("~/Type/fonts/fonts/_script/ChocStd.otf")
blanco = Font.Cacheable("~/Type/fonts/fonts/_text/Blanco-Regular.otf")
reiner = Font.Cacheable("~/Type/fonts/fonts/_script/ReinerScript-Bold.otf")


def render_txt(txt, styles):
    if "i" in styles:
        return txt, Style(mistral, 110, xShift=7, bs=-6, fill=0)
    elif "h" in styles:
        return txt.upper(), Style(choc, 150, bs=-20, fill=0)
    elif "b" in styles:
        return txt.upper(), Style(reiner, 90, bs=0, fill=hsl(0.1, s=0.8))
    return txt, Style(blanco, 64, fill=0)
    
txt1 = """
Behold! [h]
An attempt at rich[i] text
And one[b] more[b] line
"""

@test()
def test_rich(r):
    pens = (RichText(r, txt1, render_txt).xa().align(r, tv=1))
    
    pens[1][0].rotate(180).translate(0, -5)
    pens[1][1].f(Gradient.H(
        pens[1][1].bounds(),
        hsl(0.6, s=1),
        hsl(0.95, s=1)))
    return pens

txt2 = """
Behold!≤h≥
An ¬a¬ttempt≤i≥ ¬at ¬rich≤i≥ ¬text
And ¬one more≤b≥ ¬line
"""

@test(solo=0)
def test_rich_custom(r):
    pens = (RichText(r, txt2, render_txt,
        tag_delimiters=["≤", "≥"],
        visible_boundaries=["¶"],
        invisible_boundaries=["¬"])
        .xa()
        .align(r, tv=1))
    
    for p in pens.filter_style("h"):
        (p.f(Gradient.V(p.bounds(), hsl(0.9, s=1), hsl(0.5, s=1)))
            .s(0).sw(2))
    
    for p in pens.filter_style("i"):
        p.f(hsl(0.8, l=0.8))
        for c in p.copy(with_data=True):
            if c.glyphName == "space":
                continue
            p.insert(0, DATPen().rect(c.bounds()).f(hsl(0.7, a=0.75)))
            p.insert(0, DATPen().rect(c.getFrame()).f(hsl(0.05, s=0.7, a=0.7)))
    
    for p in pens.filter_style("b"):
        p.rotate(180).translate(-15, 0)
    
    return pens

code = """
# a rich function

def rich(txt:str):
    # a comment
    text = txt.upper()
    return f"rich:{text}"
"""

def render_code(txt, styles):
    if "Keyword" in styles:
        return txt, Style(choc, 50, fill=hsl(0.9, s=1), bs=2)
    if "Literal.String.Affix" in styles:
        return txt, Style(blanco, 50, fill=hsl(0.1, s=1), rotate=15)
    if "Literal.String.Double" in styles:
        return txt, Style(mistral, 50, fill=hsl(0.3, s=0.5))
    if "Name" in styles:
        return txt, Style(choc, 50, fill=hsl(0.7, s=1))
    if "Name.Function" in styles:
        return txt, Style(choc, 50, fill=hsl(0.6, s=1))
    if "Name.Builtin" in styles:
        return txt, Style(mistral, 50, fill=hsl(0.3, s=1))
    if "Comment.Single" in styles:
        return txt, Style(mistral, 50, fill=0.8)
    else:
        pass
    
    return txt, Style(mistral, 50, fill=(0))

@test(solo=0)
def test_rich_code(r):
    rt = (PythonCode(r.inset(100), code, render_code,
        graf_style=GrafStyle(leading=12))
        #.align(r, tv=1)
        .scale(1)
        .remove_blanklines())
    
    out = DATPens()
    for line in rt:
        out += DATPen().rect(line.getFrame()).f(hsl(0.3, a=0.1))

    out += rt#DPS(rt.pens)
    return out

txt3 = """H [h]

Text
footnote, innit? [i]"""

def render_txt2(txt, styles):
    blanc = "~/Type/fonts/fonts/_text/Blanco-"
    if "i" in styles:
        return txt, Style(blanc + "Italic.otf", 32)
    elif "h" in styles:
        return txt, Style(blanc + "Bold.otf", 72)
    return txt, Style(blanc + "Regular.otf", 42)

@test(solo=0)
def test_plainish(r):
    rt = (RichText(r, txt3, render_txt2, blankfill="¶")
        #.remove_blanks()
        .xa()
        .align(r)
        .scale(2)
        .f(0)
        -.remove_blanklines())
    #return DP(rt.ambit(th=1))
    return rt

txt4 = """
Hello, [a]
World!
"""

@test(solo=0)
def test_style_key_lookup(r):
    rt = (RichText(
        r, txt4, {
            "a": Style(mistral, 200, fill=hsl(0.3)),
            "default": Style(blanco, 100, fill=bw(0))})
        .xa()
        .align(r))
    #print(rt.tree())
    return rt
    return DPS([rt])