from coldtype import *

Style.RegisterShorthandPrefix("≈", "~/Type/fonts/fonts")
swear = Font.Cacheable("≈/SwearCilatiVariable.ttf")
fatface = Font.Cacheable("≈/OhnoFatfaceVariable.ttf")
cheee = Font.Cacheable("≈/CheeeVariable.ttf")

@animation((1080, 1080/2), timeline=60, solo=0)
def cilati_wave(f:Frame):
    return (DATPens.Enumerate("Cilati", lambda i, c:
        StSt(c, swear, 340,
            opsz=(fa:=f.adj(i*8)).e(ease:="seio", 1),
            wght=fa.e(ease, 1)).f(0))
        .distribute()
        .align(f.a.r))

@animation((1080, 1080/2), timeline=50, solo=0)
def fatface_wave(f):
    return (DATPens.Enumerate("WAVEFORM", lambda i, c:
        (StSt(c, fatface,
            150+(fa:=f.adj(i*4)).ie(ease:="seio", 1)*150,
            wdth=fa.e(ease, 1),
            opsz=fa.ie(ease, 1),
            rotate=-15+30*fa.e(ease, 1),
            ).f(0)))
        .distribute()
        .align(f.a.r, h=200))

loop = Loop(120, 8, [
    dict(grvt=0, yest=1, rotate=0),
    dict(grvt=1, yest=0, rotate=0),
    dict(grvt=1, yest=1, rotate=0),
    dict(grvt=0, yest=0, rotate=180)])

@animation((1080, 520), timeline=loop, solo=0)
def cheee_wild(f):
    return (DATPens.Enumerate("CHEEE", lambda i, c:
        (StSt(c, cheee, 270,
            **f.a.t.current_state((f.i-i*30), "eeio"))
            .f(1)))
        .distribute()
        .align(f.a.r)
        .translate(0, 10)
        .insert(0, DP(f.a.r).f(0)))

def release(passes):
    FFMPEGExport(cheee_wild, passes).gif().write()