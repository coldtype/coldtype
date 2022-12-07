from coldtype import *

audio = __sibling__("media/c78.wav")

midi = MidiTimeline(__sibling__("media/c78.mid")
    , bpm=120
    , lookup={
        0: (36, 41), # kicks
        1: 37, # snare
        2: 45, # tom-lo
        3: 47, # tom-hi
    })

@animation((1080, 540), timeline=midi, bg=0, render_bg=1)
def drumloop(f):
    kicks = f.a.t.ki(0, f.i).index()

    def styler(g):
        # return an array
        # — first is style for metrics
        # - second is mods to style for animation
        return [Style(Font.MuSan(), 350, tu=100),
            dict(wdth=f.a.t.ki(g.i).adsr((10, 130)),
                 wght=f.a.t.ki(g.i).adsr((5, 20), r=(0, 1)))]

    s = hsl(0.3) if kicks == 0 else hsl(0.8)

    return (Glyphwise("DRUM", styler)
        .align(f.a.r, tx=0)
        .fssw(-1, s, 4)
        .sm(0.5))