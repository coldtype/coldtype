from coldtype import *
from coldtype.animation.audio import Wavfile

audio = Wavfile(__sibling__("media/helloworld.wav"))
audio = Wavfile(__sibling__("media/12272020.wav"))

@animation(timeline=Timeline(audio.framelength), audio=audio.path)
def playback(f):
    wh = 700
    wave = DATPen()
    samples = audio.samples_for_frame(f.i)[::1]
    ww = f.a.r.w/len(samples)
    for idx, w in enumerate(samples):
        if idx == 0:
            wave.moveTo((0, w[0]*wh))
        else:
            wave.lineTo((idx*ww, w[0]*wh))
    wave.endPath()
    wave.f(None).s(1).sw(3).translate(0, f.a.r.h/2)

    return [
        wave.s(0),
        (DATText(str(f.i), Style("Times", 100, load_font=0), f.a.r.inset(200)))
    ]