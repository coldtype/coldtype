from coldtype import *
from coldtype.fx.skia import phototype

fnt = Font.MutatorSans()

@animation(timeline=Timeline(90, 24), bg=0, render_bg=1)
def glyphwise(f):
    def styler(g):
        return [
            Style(fnt, 250, wdth=0.15),
            Style(fnt, 250,
                wdth=f.adj(-g.i*2).e("eeio", 2),
                wght=f.adj(-g.i*3).e("seio", 3),
                ro=1,
                tv=1)]

    return (Glyphwise("COLD\nTYPE", styler)
        .xalign(f.a.r, th=0)
        .lead(30)
        .align(f.a.r, th=0)
        .collapse()
        .rp()
        .fssw(1, 0, 7, 1)
        .ch(phototype(f.a.r, 3, 190, cutw=15)))