from coldtype.test import *
from coldtype.animation.sequence import Sequence
from coldtype.animation.audio import Wavfile

audio = Wavfile(__sibling__("media/helloworld.wav"))

class Subtitler(Sequence):
    def __init__(duration, fps=30, storyboard=[0]):
        super().__init__(duration, fps, storyboard, [])

tl = Subtitler(audio.framelength)

@animation(timeline=tl, audio=audio.path, bg=0)
def lyric_entry(f):
    wh = 700
    wave = (audio
        .frame_waveform(f.i, f.a.r.inset(0, 300))
        .translate(0, f.a.r.h/2))

    return [
        wave.s(1).sw(25).phototype(f.a.r, blur=15, fill=bw(0.2)),
        (DATText(str(f.i),
            Style("Helvetica", 50, load_font=0, fill=bw(0.2)),
            f.a.r.inset(10)))]