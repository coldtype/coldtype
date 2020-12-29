from coldtype import *
from coldtype.animation.audio import Wavfile

audio = Wavfile(__sibling__("media/helloworld.wav"))

@animation(timeline=Timeline(audio.framelength), audio=audio.path)
def playback(f):
    playback.play_audio_frame(f.i)
    return (DATText(str(f.i), Style("Times", 100, load_font=0), f.a.r.inset(200)))
