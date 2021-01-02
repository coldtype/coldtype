from coldtype.test import *
from coldtype.animation.sequence import Sequence
from coldtype.animation.audio import Wavfile

audio = Wavfile(__sibling__("media/helloworld.wav"))

class Subtitler(Sequence):
    def __init__(self, duration, fps=30, storyboard=[0]):
        super().__init__(duration, fps, storyboard, [])

tl = Subtitler(audio.framelength)

@animation(timeline=tl, audio=audio.path, bg=0)
def lyric_entry(f):
    return DATPen().oval(f.a.r)