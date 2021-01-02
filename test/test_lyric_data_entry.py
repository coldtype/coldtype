from coldtype.test import *
from coldtype.animation.audio import Wavfile
from coldtype.animation.nle.subtitler import Subtitler


fnt = Font.Cacheable("~/Type/fonts/fonts/ObviouslyVariable.ttf")
audio = Wavfile(__sibling__("media/helloworld.wav"))
        

tl = Subtitler("test/lyric_data.json", audio.framelength, storyboard=[3])

@animation(timeline=tl, audio=audio.path, bg=0, rstate=1, watch=[tl.path])
def lyric_entry(f, rs):
    def render_clip_fn(f, idx, clip, ftext):
        return ftext, Style(fnt, 150, wdth=0.5, wght=0.5)

    cg = tl.clip_group(0, f.i)
    clips = tl.data["tracks"][tl.workarea_track]["clips"]
    if rs.text:
        tl.add_clip(f.i, rs.text)
        tl.persist()
    elif rs.cmd:
        if rs.cmd == "d":
            tl.delete_clip(f.i)
            tl.persist()
        elif rs.cmd == "c":
            tl.cut_clip(f.i)
            tl.persist()
        elif rs.cmd == "e":
            tl.extend_clip(f.i)
            tl.persist()

    return (cg
        .pens(f, render_clip_fn, f.a.r)
        .f(hsl(0.9))
        .xa()
        .align(f.a.r)
        .remove_futures())
    #return DATPen().oval(f.a.r).f(0.1)