from coldtype import *
from coldtype.text.composer import Glyphwise

cheee = Font.Cacheable("~/Type/fonts/fonts/CheeeVariable.ttf")

@animation((1080, 290), timeline=Timeline(90))
def welcome(f):
    return DPS([
        (DP(f.a.r).f(hsl(0.7))),
        (Glyphwise("WELCOME", lambda i, c:
            Style(cheee, 250,
                yest=f.e("ceio", 1),
                grvt=f.adj(i*10).e("seio", 3)))
            .f(None).s(1).sw(2)
            .track(f.e("eeio", 1, rng=(0, -100)))
            .align(f.a.r, tv=1)
            .pen())])

release = welcome.export("gif")