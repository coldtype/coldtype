from coldtype.test import *
from coldtype.animation.audio import Wavfile
from coldtype.animation.nle.subtitler import Subtitler


fnt = Font.Cacheable("~/Type/fonts/fonts/ObviouslyVariable.ttf")
audio = Wavfile(__sibling__("media/helloworld.wav"))
        

tl = Subtitler("test/lyric_data.json", audio.framelength, storyboard=[3])

colors = [
    hsl(0.3),
    hsl(0.5),
    hsl(0.9)
]

@animation(timeline=tl, audio=audio.path, bg=0, rstate=1, watch=[tl.path])
def lyric_entry(f, rs):
    def render_clip_fn(f, idx, clip, ftext):
        return ftext, Style(fnt, 150, wdth=0.5, wght=0.5)
    
    seq = DATPenSet()
    sw = 30
    sh = 50

    for tidx, t in enumerate(tl.tracks):
        for cgidx, cg in enumerate(t.clip_groups):
            for cidx, c in enumerate(cg.clips):
                h = c.duration*sh
                #r = Rect(
                #    100,
                #    (c.start*-sh)-h+2,
                #    sw,
                #    h-2)
                
                r = Rect(
                    c.start*sw,
                    sh*tidx,
                    (c.duration*sw)-2,
                    sh)
                
                seq.insert(0, DATPenSet([
                    (DATPen()
                        .rect(r)
                        .f(colors[cgidx].lighter(0.2))),
                    (DATText(c.input_text,
                        Style(recmono, 24, load_font=0, fill=bw(0)),
                        r.inset(2, 5)))
                    ]))

    #seq.translate(0, f.i*sh+f.a.r.h/2)
    seq.translate(f.a.r.w/2 - f.i*sw, 0)
    seq.insert(-1,
        DATPen()
        .rect(f.a.r.take(100, "mny").take(4, "mdx"))
        .f(hsl(0.8)))

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
        elif rs.cmd == "p":
            tl.persist()
        elif rs.cmd == "q":
            tl.extend_prev_clip(f.i)
            tl.persist()

    cs = tl.clips(tl.workarea_track)
    print(tl.closest(f.i, -1, cs))
    print(tl.closest(f.i, +1, cs))
    
    print("-------")

    out = DATPenSet([seq])
    out += (cg
        .pens(f, render_clip_fn, f.a.r)
        .f(hsl(0.9))
        .xa()
        .align(f.a.r)
        .remove_futures())
    
    return out
    #return DATPen().oval(f.a.r).f(0.1)