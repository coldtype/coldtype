from coldtype import *
from coldtype.time.nle.ascii import AsciiTimeline

swear = Font.Find("SwearCilatiVariable")
fatface = Font.Find("OhnoFatfaceVariable")
cheee = Font.Find("CheeeVariable")

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

at = AsciiTimeline(2, 30, """
A   A   B   B   C   C   D    D  <
""", {
    "A": dict(grvt=0, yest=1, rotate=0),
    "B": dict(grvt=1, yest=0, rotate=0),
    "C": dict(grvt=1, yest=1, rotate=0),
    "D": dict(grvt=0, yest=0, rotate=180),
})

@animation((1080, 520), timeline=at, solo=1, bg=0)
def cheee_wild(f):
    return (Glyphwise("CHEEE", lambda g: [
        Style(cheee, 270, tu=50),
        at.kf(f.i+g.i*30, easefn="eeio")])
        .f(1)
        .align(f.a.r, th=0)
        .rp().understroke(0, 8))