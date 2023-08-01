from coldtype import *

mt = MidiTimeline(__sibling__("media/midi_cc.mid"))
wav = __sibling__("media/midi_cc.wav")

fnt = Font.Find("Libido", index=1)
fnt = "BildVariableV4"

@animation(tl=Timeline(120, 30), bg=0, audio=wav)
def cc(f):
    mt.hold(f.i)
    print(mt.ci(104))
    return (P(
        StSt("MIDI", fnt, 300
            , wght=0, wdth=mt.ci(102)),
        StSt("CC", fnt, 300
            , wght=1, wdth=mt.ci(103)),
        StSt("DATA", fnt, 300),
        )
        .stack(20)
        .xalign(f.a.r)
        .align(f.a.r)
        .î(2, lambda p: p.rotate(-5+mt.ci(104)*10))
        .f(1))
