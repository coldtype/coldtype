from coldtype import *
from coldtype.fx.skia import phototype

@animation(bg=0, timeline=Timeline(30, 15), render_bg=1)
def plus(f):
    def lockup(adj, fill):
        return (Glyphwise("ABC", lambda g:
            Style(Font.MutatorSans(), 750,
                wght=f.adj(adj-g.i*5).e("eeio", 1),
                wdth=(fa:=f.adj(adj-5)).e("eeio", 1, rng=(1, 0)),
                tu=fa.e("eeio", 1, rng=(-250, 0)),
                ro=1))
            .mapv(lambda p: p.align(f.a.r, ty=1, tx=1))
            .pen()
            .fssw(-1, 1, 10)
            .ch(phototype(f.a.r,
                blur=5, cut=f.e("seio", 2, rng=(50, 150)), cutw=15, fill=fill))
            .blendmode(BlendMode.Plus))
    
    return P(
        lockup(0, hsl(f.e("l"))),
        lockup(1.25, hsl(f.adj(-5).e("l"))),
        lockup(3.5, hsl(f.adj(-20).e("l"))))

release = plus.export("h264", loops=6)