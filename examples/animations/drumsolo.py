from coldtype import *
from coldtype.time.midi import MidiReader
from coldtype.fx.skia import phototype 

midi = MidiReader(__sibling__("media/68.mid"), bpm=151)
drums = midi[0]

@animation(timeline=midi, bg=0, render_bg=1)
def drumsolo(f):
    def d(notes, inn, out):
        return drums.fv(f.i, notes, [inn, out])

    kick = drums.fv(f.i, [36, 38], [5, 50])
    snare = drums.fv(f.i, [42, 62, 63], [3, 20])

    lk1 = {
        "O": {6: kick.ease()},
        "M": {3: snare.ease() },
        "U": {2: d([60, 61, 64], 3, 10).ease()},
        "H": {5: d([81, 93, 94, 98], 3, 10).ease()},
        "R": {1: d([49, 50, 65, 71], 3, 20).ease()},
        "D": {0: d([72, 73, 74], 3, 50).ease()},
        "S": {4: d([52, 54, 86], 3, 50).ease()},
        "P": {7: d([51], 3, 350).ease()}
    }

    def styler1(g):
        return Style(
            Font.Find("WTZaft2VariableA"), 350,
            wght=lk1.get(g.c, {}).get(g.i, 0))

    return (Glyphwise("DRUM\nSHOP", styler1)
        .track(4, v=1)
        .xalign(f.a.r, th=0)
        .align(f.a.r, th=0)
        .f(1)
        .pen()
        .layer(
            # lambda p: p
            #     .outline(10, miterLimit=10)
            #     .remove_overlap()
            #     .explode()[0]
            #     .fssw(-1, 1, 10)
            #     .ch(phototype(f.a.r,
            #         blur=3, cut=190, cutw=25, fill=hsl(f.e("l"), 1, 0.7))),
            lambda p: p
                .ch(phototype(f.a.r, blur=2, cut=190, cutw=25))))

release = drumsolo.export("h264",
    #audio=__sibling__("media/68.wav"),
    audio=Path("~/Audio/loops/20210908.wav"),
    audio_loops=2,
    loops=4)