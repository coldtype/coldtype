from coldtype import *

@animation((1080, 1080/2), timeline=30)
def cilati_wave(f:Frame):
    return (Glyphwise("Cilati", lambda g:
        Style("SwearCilatiVariable", 340,
            #show_frames=1,
            #no_shapes=1,
            opsz=(fa:=f.adj(g.i*20)).e(ease:="qeio", 1),
            wght=fa.e(ease, 1)))
        .f(0)
        .align(f.a.r, th=0))