from coldtype import *
from coldtype.time.midi import *

audio = __sibling__("media/c78.wav")

mr = MidiReader2(__sibling__("media/c78.mid")
    , bpm=120
    , lookup={
        0: (36, 41), # kicks
        1: 37, # snare
        2: 45, # tom-lo
        3: 47}) # tom-hi

ar = [[5, 50], [3, 20], [3, 30], [3, 30]]

@animation(timeline=mr, bg=0, render_bg=1, audio=audio)
def drumloop(f):
    kc = mr.ki(0, f.i).count()

    def styler(g):
        return [Style(Font.MutatorSans(), 350 if kc == 1 else 450), dict(
            wdth=(e:=mr.ki(g.i, f.i)).adsr(ar[g.i]),
            wght=e.adsr(ar[g.i], rng=(0, 0.5)))]

    return (Glyphwise("LOOP", styler)
        .align(f.a.r, th=0)
        .f(1))