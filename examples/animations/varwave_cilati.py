from coldtype import *

@animation((1080, 1080/2), timeline=60)
def cilati_wave(f:Frame):
    return (Glyphwise("Cilati", lambda g:
        Style("SwearCilatiVariable", 340,
            opsz=(fa:=f.adj(g.i*8)).e(ease:="seio", 1),
            wght=fa.e(ease, 1)))
        .f(0)
        .align(f.a.r))