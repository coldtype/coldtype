from coldtype import *
from coldtype.timing.audio import Wavfile
from coldtype.fx.skia import phototype

"""
You'll need to `pip install soundfile` in yourt virtualenv to get this to work
"""

audio = Wavfile("examples/animations/media/coldtype.wav")
obvs = Font("assets/ColdtypeObviously.designspace")

@animation(timeline=audio.framelength, bg=0, audio=audio.path)
def render(f):
    amp = audio.amp(f.i)
    return (StSt("COLDTYPE", obvs, 700,
            tu=-50+150*(0.2+pow(amp,2)*5),
            rotate=5+10*amp,
            wdth=0,
            r=1,
            ro=1)
        .align(f.a.r)
        .fssw(hsl(0.9, s=0.6, l=0.4), 1, 20, 1))