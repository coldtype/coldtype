from coldtype.test import *
from coldtype.time.audio import Wavfile
from coldtype.time.nle.subtitler import Subtitler, lyric_editor


tl = Subtitler(
    "test/lyric_data.json",
    "test/media/helloworld.wav",
    storyboard=[3])


@lyric_editor(tl, bg=0, data_font=recmono)
def lyric_entry(f, rs):
    def render_clip_fn(f, idx, clip, ftext):
        if "stylized" in clip.styles:
            return ftext.upper(), Style(co, 150, wdth=0.5, tu=50, fill=hsl(0.61, s=1, l=0.7))
        return ftext, Style(recmono, 100, fill=1)

    return (tl.clip_group(0, f.i, styles=[1])
        .pens(f, render_clip_fn, f.a.r)
        .f(1)
        .xa()
        .align(f.a.r)
        .remove_futures())