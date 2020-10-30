from coldtype.test import *

txt = """
Behold! [h]
An attempt at rich[i] text
And one[b] more[b] line
"""

mistral = Font.Cacheable("~/Type/fonts/fonts/_script/MistralD.otf")
choc = Font.Cacheable("~/Type/fonts/fonts/_script/ChocStd.otf")
blanco = Font.Cacheable("~/Type/fonts/fonts/_text/Blanco-Regular.otf")
reiner = Font.Cacheable("~/Type/fonts/fonts/_script/ReinerScript-Bold.otf")

def render_txt(txt, styles):
    if "i" in styles:
        return txt, Style(mistral, 110, xShift=7, bs=-6)
    elif "h" in styles:
        return txt.upper(), Style(choc, 150, bs=-20)
    elif "b" in styles:
        return txt.upper(), Style(reiner, 90, bs=0, fill=hsl(0.9))
    return txt, Style(blanco, 64)
    
@test()
def test_plockup(r):
    pens = (RichText(txt, render_txt, r)
        .xa()
        .align(r, tv=1)
        .f(0))
    
    pens[1][0].rotate(180).translate(0, -5)
    pens[1][1].f(Gradient.H(
        pens[1][1].bounds(),
        hsl(0.6, s=1),
        hsl(0.95, s=1)))
    return pens