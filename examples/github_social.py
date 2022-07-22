from coldtype import *
from coldtype.fx.skia import phototype

@renderable((1280, 640), bg=hsl(0.7, 0.6, 0.4), render_bg=True)
def github_social(r):
    def styler(x):
        e = 1 - x.e if not x.l else x.e
        return Style(Font.ColdObvi(), 290, wdth=e, tu=-100*e, rotate=30 if x.l else -10)

    logos = (Glyphwise("COLDTYPE\nCOLDTYPE", styler)
        .lead(10)
        .align(r.take(0.9, "N"))
        .index(1, lambda p: p.t(15, 0))
        .fssw(1, 0, 10, 1)
        .reverse(recursive=True)
        .ch(phototype(r, blur=3, cut=180, cutw=17)))

    return P(logos,
        StSt("A PYTHON LIBRARY", Font.MuSan(), 50, wdth=1)
            .f(1)
            .align(r.take(120, "S")))