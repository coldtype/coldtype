from coldtype import *

@animation((1080, 290), timeline=Timeline(90), render_bg=True, bg=hsl(0.65))
def welcome(f):
    return (Glyphwise("ABC", lambda g:
        Style("CheeeVar", 250,
            tu=f.e("eeio", 1, rng=(0, -350)),
            yest=f.e("ceio", 1),
            grvt=f.adj(g.i*10).e("seio", 3)))
        .fssw(-1, 1, 3)
        .align(f.a.r, ty=1))

release = welcome.export("gif")