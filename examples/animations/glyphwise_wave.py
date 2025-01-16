from coldtype import *

DEBUG = 0

@animation((1080, 1080/2), timeline=30)
def cilati_wave(f:Frame):
    def styler(g:GlyphwiseGlyph):
        fa = f.adj(g.i*20)
        return (Style(Font.MuSan(), 270,
            show_frames=DEBUG,
            no_shapes=DEBUG,
            wdth=fa.e(ease:="qeio", 1),
            wght=fa.e(ease, 1)))

    return (Glyphwise("COLD\nTYPE".upper(), styler)
        .xalign(f.a.r)
        .lead(50)
        .f(0)
        .align(f.a.r, tx=0, ty=1))