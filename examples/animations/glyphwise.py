from coldtype import *
from coldtype.fx.skia import phototype

fnt = Font.MutatorSans()

@animation(timeline=Timeline(90, 24), bg=0, render_bg=1)
def glyphwise(f):
    def styler(g):
        return [
            Style(fnt, 250, wdth=0.15, tu=f.e("seio", rng=(-100, 300))), # metrics
            Style(fnt, 250 # animated
                , wdth=f.adj(-g.i*2).e("eeio", 2)
                , wght=f.adj(-g.i*3).e("seio", 3)
                , ro=1
                , ty=1
                )]

    # should also work w/o an \n in between COLD & TYPE
    return (Glyphwise("COLD\nTYPE", styler, multiline=1)
        .xalign(f.a.r, tx=0)
        .lead(30)
        .align(f.a.r, tx=0)
        .reverse(recursive=True)
        .fssw(1, 0, 7, 1)
        .ch(phototype(f.a.r, 3, 190, cutw=15)))