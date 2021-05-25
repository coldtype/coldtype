from coldtype import *

Style.RegisterShorthandPrefix("≈", "~/Type/fonts/fonts")
fnt = Font.Cacheable("≈/SwearCilatiVariable.ttf")
ff = Font.Cacheable("≈/OhnoFatfaceVariable.ttf")
cheee = Font.Cacheable("≈/CheeeVariable.ttf")


@animation((1080, 1080/2), timeline=60, solo=0)
def cilati_wave(f:Frame):
    chrs = DATPens()
    for idx, c in enumerate("Cilati"):
        fa = f.adj(idx*8)
        chrs += StSt(c, fnt, 340,
            opsz=fa.e(ease:="seio", 1),
            wght=fa.e(ease, 1)).f(0)
    return (chrs.distribute().align(f.a.r))


@animation((1080, 1080/2), timeline=50, solo=0)
def fatface_wave(f):
    chrs = DATPens()
    for idx, c in enumerate("MEZCAL"):
        fa = f.adj(idx*5)
        chrs += StSt(c, ff, 200+fa.ie(ease:="seio", 1)*300, ro=1,
            wdth=fa.e(ease, 1),
            opsz=0.75).f(0)
    return (chrs.distribute().align(f.a.r, h=310))


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