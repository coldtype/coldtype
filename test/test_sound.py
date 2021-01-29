from coldtype import *
from coldtype.time.audio import Wavfile

audio = Wavfile(__sibling__("media/helloworld.wav"))
audio = Wavfile(__sibling__("media/20210106.wav"))
#audio = Wavfile(__sibling__("media/ratchet.wav"))

@animation(timeline=Timeline(audio.framelength), audio=audio.path)
def playback(f):
    wh = 700
    wave = (audio
        .frame_waveform(f.i, f.a.r.inset(0, 300))
        .translate(0, f.a.r.h/2))

    return [
        wave.s(0),
        (DATText(str(f.i),
            Style("Helvetica", 100, load_font=0),
            f.a.r.inset(10)))]