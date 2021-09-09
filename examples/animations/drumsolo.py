from coldtype import *
from coldtype.time.midi import MidiReader
from coldtype.fx.skia import phototype 

midi = MidiReader(__sibling__("media/68.mid"), bpm=151)

@animation(timeline=midi, bg=hsl(0.65, 0.8, l=0.2), render_bg=1)
def drumsolo(f):
    d = midi[0].fifve(f.i)
    lk1 = {
        "O": d([36, 38], 5, 50),
        "M": d([42, 62, 63], 3, 20),
        "U": d([60, 61, 64], 3, 10),
        "H": d([81, 93, 94, 98], 3, 10),
        "R": d([49, 50, 65, 71], 3, 20),
        "D": d([72, 73, 74], 3, 50),
        "S": d([52, 54, 86], 3, 50),
        "P": d([51], 3, 350)
    }

    return (Glyphwise("DRUM\nSHOP", lambda g:
            [Style(Font.MutatorSans(), 350),
             Style(Font.MutatorSans(), 350,
                wdth=lk1.get(g.c, 0),
                wght=0.25*lk1.get(g.c, 0))])
        .track(40, v=1)
        .xalign(f.a.r, th=0)
        .align(f.a.r, th=0)
        .f(1)
        .pen()
        .ch(phototype(f.a.r,
            blur=2, cut=190, cutw=25,
            fill=hsl(0.65, 0.8, l=0.75))))

release = drumsolo.export("h264",
    audio=__sibling__("media/68.wav"),
    vf="eq=brightness=0.0:saturation=1.5",
    loops=2)