from coldtype import *

Style.RegisterShorthandPrefix("≈", "~/Type/fonts/fonts")
swear = Font.Cacheable("≈/SwearCilatiVariable.ttf")
fatface = Font.Cacheable("≈/OhnoFatfaceVariable.ttf")
cheee = Font.Cacheable("≈/CheeeVariable.ttf")

@animation((1080, 1080/2), timeline=60, solo=0)
def cilati_wave(f:Frame):
    return (Glyphwise("Cilati", lambda g:
        Style(swear, 340,
            opsz=(fa:=f.adj(g.i*8)).e(ease:="seio", 1),
            wght=fa.e(ease, 1)))
        .f(0)
        .align(f.a.r))

@animation((1080, 1080/2), timeline=50, solo=0)
def fatface_wave(f):
    return (Glyphwise("WAVEFORM", lambda g:
        (Style(fatface,
            100+(fa:=f.adj(g.i*4)).e(ease:="seio", 1)*150,
            wdth=fa.e(ease, 1),
            opsz=fa.e(ease, 1),
            rotate=-15+30*fa.e(ease, 1))))
        .align(f.a.r, h=200)
        .f(0))

loop = Loop(120, 8, [
    dict(grvt=0, yest=1, rotate=0),
    dict(grvt=1, yest=0, rotate=0),
    dict(grvt=1, yest=1, rotate=0),
    dict(grvt=0, yest=0, rotate=180)])

@animation((1080, 520), timeline=loop, solo=0, bg=0)
def cheee_wild(f):
    return (Glyphwise("CHEEE", lambda g:
        (Style(cheee, 270,
            **f.a.t.currentState((f.i-g.i*30), "eeio"))))
        .f(1)
        .align(f.a.r)
        .translate(0, 10))