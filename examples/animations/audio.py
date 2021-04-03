import numpy as np
import soundfile as sf
from coldtype import *
from coldtype.time.audio import Wavfile

"""
You'll need to `pip install soundfile` in yourt virtualenv to get this to work
"""

audio = Wavfile("examples/animations/media/coldtype.wav")
obvs = Font("assets/ColdtypeObviously.designspace")

@animation(duration=audio.framelength, bg=0, audio=__sibling__("media/coldtype.wav"))
def render(f):
    amp = audio.amp(f.i)
    return (StyledString("COLDTYPE",
        Style(obvs, 700,
            tu=-50+150*(0.2+pow(amp,2)*5),
            rotate=5+10*amp,
            wdth=0,
            r=1,
            ro=1))
        .pens()
        .align(f.a.r)
        .f(hsl(0.9, s=0.6, l=0.4))
        .understroke(s=1, sw=20)
        .phototype(f.a.r, cutw=45)
        )