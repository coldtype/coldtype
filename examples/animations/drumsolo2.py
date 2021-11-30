from coldtype import *

audio = __sibling__("media/c78.wav")

midi = (Programs.Midi(
    __sibling__("media/c78.mid")
    , text=0, bpm=120
    , lookup={
        0: (36, 41), # kicks
        1: 37, # snare
        2: 45, # tom-lo
        3: 47}) # tom-hi
    #.hide()
    )

ar = [[5, 50], [3, 20], [3, 30], [3, 30]]

@animation(timeline=midi.t, bg=0, render_bg=1, audio=audio)
def drumloop(f):
    kc = f.a.t.ki(0, f.i).count()

    def styler(g):
        return [Style(Font.MutatorSans(), 350 if kc == 1 else 450), dict(
            wdth=(e:=f.a.t.ki(g.i, f.i)).adsr(ar[g.i]),
            wght=e.adsr(ar[g.i], rng=(0, 0.5)))]

    return (Glyphwise("LOOP", styler)
        .align(f.a.r, th=0)
        .f(1))