from coldtype import *

Style.RegisterShorthandPrefix("≈", "~/Type/fonts/fonts")
swear = Font.Cacheable("≈/SwearCilatiVariable.ttf")
fatface = Font.Cacheable("≈/OhnoFatfaceVariable.ttf")
cheee = Font.Cacheable("≈/CheeeVariable.ttf")

@animation((1080, 1080/2), timeline=60, solo=0)
def cilati_wave(f:Frame):
    chrs = DATPens()
    for idx, c in enumerate("Cilati"):
        fa = f.adj(idx*8)
        chrs += StSt(c, swear, 340,
            opsz=fa.e(ease:="seio", 1),
            wght=fa.e(ease, 1)).f(0)
    return (chrs.distribute().align(f.a.r))

@animation((1080, 1080/2), timeline=50, solo=0)
def fatface_wave(f):
    chrs = DATPens()
    for idx, c in enumerate("WAVEFORM"):
        fa = f.adj(idx*4)
        chrs += (StSt(c, fatface,
            150+fa.ie(ease:="seio", 1)*150,
            wdth=fa.e(ease, 1),
            opsz=fa.ie(ease, 1),
            rotate=-10+20*fa.e(ease, 1),
            ).f(0))
    return (chrs.distribute().align(f.a.r, h=200))


loop = Loop(120, 8, [
    dict(grvt=0, yest=1, rotate=0),
    dict(grvt=1, yest=0, rotate=0),
    dict(grvt=1, yest=1, rotate=0),
    dict(grvt=0, yest=0, rotate=180)])
@animation((1080, 1080/2), timeline=loop, solo=0)
def cheee_wild(f):
    chrs = DATPens()
    for idx, c in enumerate("CHEEE"):
        chrs += (StSt(c, cheee, 270,
            **f.a.t.current_state((f.i-idx*30), "eeio"))
            .f(0))
    return (chrs.distribute().align(f.a.r))