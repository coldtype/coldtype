import numpy as np
import soundfile as sf
from coldtype import *
from coldtype.time.audio import Wavfile

"""
You'll need to `pip install soundfile` in yourt virtualenv to get this to work
"""

audio = Wavfile("examples/animations/media/coldtype.wav")
obvs = Font("assets/ColdtypeObviously.designspace")

@animation(duration=audio.framelength, storyboard=[13])
def render(f):
    amp = audio.amp(f.i)
    return StyledString("COLDTYPE", Style(obvs, 700, tu=-50+150*(0.2+pow(amp,2)*5), r=1, ro=1, rotate=5+10*amp, wdth=0)).pens().align(f.a.r).f(hsl(0.9, l=0.7)).s(0).sw(5)