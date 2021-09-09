from coldtype import *
from coldtype.time.midi import MidiReader
from coldtype.fx.skia import phototype 

midi = MidiReader(__sibling__("media/68.mid"), bpm=151)
drums = midi[0]

@animation(timeline=midi, bg=hsl(0.65, l=0.2), render_bg=1)
def drumsolo(f):
    d = drums.curried_fve(f.i)
    lk1 = {
        "O": {6: d([36, 38], 5, 50)},
        "M": {3: d([42, 62, 63], 3, 20)},
        "U": {2: d([60, 61, 64], 3, 10)},
        "H": {5: d([81, 93, 94, 98], 3, 10)},
        "R": {1: d([49, 50, 65, 71], 3, 20)},
        "D": {0: d([72, 73, 74], 3, 50)},
        "S": {4: d([52, 54, 86], 3, 50)},
        "P": {7: d([51], 3, 350)}
    }

    return (Glyphwise("DRUM\nSHOP", lambda g:
            Style(Font.Find("WTZaft2VariableA"), 350,
                wght=lk1.get(g.c, {}).get(g.i, 0)))
        .track(4, v=1)
        .xalign(f.a.r, th=0)
        .align(f.a.r, th=0)
        .f(1)
        .pen()
        .ch(phototype(f.a.r,
            blur=2, cut=190, cutw=25, fill=hsl(0.65, l=0.7))))

release = drumsolo.export("h264",
    #audio=__sibling__("media/68.wav"),
    audio=Path("~/Audio/loops/20210908.wav"),
    audio_loops=2,
    loops=4)