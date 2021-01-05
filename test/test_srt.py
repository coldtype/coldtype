from coldtype.test import *
from coldtype.time.nle.srt import SRT

wav = __sibling__("../examples/animations/media/house.wav")
path = __sibling__("media/srttest.srt")
srt = SRT(path, 30)

r = (1080, 1080)

def render_clip_fn(f, idx, clip, ftext):
    return ftext, Style(recmono, 50)

@animation(r, timeline=srt, watch=[path], audio=wav)
def stub(f):
    def render_clip_fn(f, idx, clip, ftext):
        return ftext, Style(recmono, 50)

    cg = srt.clip_group(0, f.i)

    cgp = cg.pens(f.i, render_clip_fn, f.a.r)
    return (cgp
        .xa()
        .align(f.a.r)
        .remove_futures())