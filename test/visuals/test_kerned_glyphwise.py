from coldtype import *
from coldtype.text.composer import Glyphwise

fnt = Font.Find("OhnoFatfaceV")

@animation((2400, 1080), timeline=60, solo=1, bg=0)
def test_kerned_animation(f):
    return (Glyphwise("WAVEFORM", lambda g:
        Style(fnt, (fa:=f.adj(-g.i*10)).e("seio", 1, (250, 500)),
            kern=1, opsz=0, wdth=fa.e("seio", 1)))
        .align(f.a.r, y="mny")
        .f(1))