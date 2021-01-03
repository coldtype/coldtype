from coldtype.test import *
from coldtype.animation.audio import Wavfile
from coldtype.animation.nle.subtitler import Subtitler, lyric_editor


tl = Subtitler(
    "test/lyric_data.json",
    "test/media/helloworld.wav",
    storyboard=[3])


@lyric_editor(tl, bg=0, data_font=recmono)
def lyric_entry(f, rs):
    def render_clip_fn(f, idx, clip, ftext):
        return ftext, Style(recmono, 100)

    return (tl.clip_group(0, f.i)
        .pens(f, render_clip_fn, f.a.r)
        .f(1)
        .xa()
        .align(f.a.r)
        .remove_futures())