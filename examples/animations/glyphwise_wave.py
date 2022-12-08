from coldtype import *

@animation((1080, 1080/2), timeline=30)
def cilati_wave(f:Frame):
    return (Glyphwise("COLD\nTYPE".upper(), lambda g:
        Style(Font.MuSan(), 270,
            #show_frames=1,
            #no_shapes=1,
            wdth=(fa:=f.adj(g.i*20)).e(ease:="qeio", 1),
            wght=fa.e(ease, 1)))
        .xalign(f.a.r)
        .lead(50)
        .f(0)
        .align(f.a.r, tx=0))